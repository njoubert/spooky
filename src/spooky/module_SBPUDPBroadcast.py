# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback

from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client.drivers.pyftdi_driver import PyFTDIDriver

from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS_LLH, MsgObs
from sbp.settings import SBP_MSG_SETTINGS_WRITE, MsgSettingsWrite, SBP_MSG_SETTINGS_SAVE, MsgSettingsSave
from sbp.navigation import SBP_MSG_POS_LLH, MsgPosLLH

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.modules, spooky.ip

class SBPUDPBroadcastModule(spooky.modules.SpookyModule, spooky.ip.UDPBroadcaster):
  '''
  For the moment, we just broadcast every OBS coming in.
  If this gives us problems, we can split into two threads,
  one reading OBS, another repeating the last OBS in some error-resilient way.
  '''

  def __init__(self, instance_name, main, sbp_port, sbp_baud, dest=('192.168.2.255', 5000), interval=0.1):
    '''Create a UDP Broadcast socket'''
    spooky.modules.SpookyModule.__init__(self, main, "SBPUDPBroadcast", singleton=True)
    spooky.ip.UDPBroadcaster.__init__(self, dest=dest)
    self.interval = interval
    self.sbp_port = sbp_port
    self.sbp_baud = sbp_baud
    self.last_sent = None
    self.framer = None
    self.driver = None
    main.add_command('base', self.cmd_base, 'interact with the base station')
    self.init_surveying()

  def handle_all(self, msg, **metadata):
    pass

  def handle_basestation_obs(self, msg, **metadata):
    try:
      self.last_sent = time.time()
      self.broadcast(msg.pack())
    except socket.error:

      traceback.print_exc()

  def init_surveying(self):

    # STOP broadcasting our base position while we're surveying ourselves!
    self.toggle_base_pos_broadcast(value=False)

    self.samples_to_avg_over = 600

    self.surveyed_samples = 0
    self.surveyed_lat = 0
    self.surveyed_lon = 0
    self.surveyed_alt = 0

    self.surveyed_exp_alpha = 2.0/(self.samples_to_avg_over +1) # 2/(N+1) where N is the number of series

  def handle_surveying(self, msg, **metadata):

    if self.surveyed_samples > self.samples_to_avg_over:
      return

    def cum_average(sample, cum_avg, nsamples):
      return (sample + nsamples * cum_avg) / (nsamples + 1)

    def exp_avg(sample, exp_avg, alpha):
      if exp_avg == 0:
        return sample
      return alpha * sample + (1 - alpha) * exp_avg

    # Do a bit of averaging

    # This would be a cumulative average:    
    avg_lat = cum_average(msg.lat, self.surveyed_lat, self.surveyed_samples)
    avg_lon = cum_average(msg.lon, self.surveyed_lon, self.surveyed_samples)
    avg_alt = cum_average(msg.height, self.surveyed_alt, self.surveyed_samples)

    # This would be an exponential average. Let's do that:
    # avg_lat = exp_avg(msg.lat, self.surveyed_lat, self.surveyed_exp_alpha)
    # avg_lon = exp_avg(msg.lon, self.surveyed_lon, self.surveyed_exp_alpha)
    # avg_alt = exp_avg(msg.height, self.surveyed_alt, self.surveyed_exp_alpha)

    self.surveyed_samples += 1
    self.surveyed_lat = avg_lat
    self.surveyed_lon = avg_lon
    self.surveyed_alt = avg_alt

    print "  Surveyed Average: %.6f, %.6f, %.5f" % (self.surveyed_lat, self.surveyed_lon, self.surveyed_alt)
    print "  Surveyed Samples %d/%d" % (self.surveyed_samples, self.samples_to_avg_over)

    # Once we're confident enough, STOP SURVEYING
      # BETTER: (call it lat-lon-alt average has changed little enough?)
    if self.surveyed_samples > self.samples_to_avg_over:
      print "SBPUDPBroadcast: SETTING BASE STATION SURVEYED LOCATION"
      self.set_base_pos_location(self.surveyed_lat, self.surveyed_lon, self.surveyed_alt, save=True)
      self.toggle_base_pos_broadcast(value=True, save=True)

  def run(self):
    '''Thread loop here'''
    # Problems? See: https://pylibftdi.readthedocs.org/en/latest/troubleshooting.html
    # with PyFTDIDriver(self.sbp_baud) as driver:
    try:
      with PySerialDriver(self.sbp_port, baud=self.sbp_baud) as driver:
        self.driver = driver
        self.framer = Framer(driver.read, driver.write)
        with Handler(self.framer) as handler:

          self.handler = handler
          handler.add_callback(self.handle_basestation_obs, msg_type=[SBP_MSG_OBS, SBP_MSG_BASE_POS_LLH])
          handler.add_callback(self.handle_surveying, msg_type=[SBP_MSG_POS_LLH])
          
          self.ready()

          try:
            while not self.wait_on_stop(1.0):
              pass 
          except KeyboardInterrupt:
            raise
          except socket.error:
            raise
          except SystemExit:
            print "Exit Forced. We're dead."
            return


    except:
      traceback.print_exc()
      self.ready()

  def cmd_redo_survey(self):
    self.init_surveying()

  def cmd_base(self, args):

    def usage():
      print 'base (broadcast <t|f> | set_pos <lat> <lon> <alt> | survey)'
      print args

    if 'broadcast' in args:
      if 't' in args:
        self.toggle_base_pos_broadcast(value=True)
      else:
        self.toggle_base_pos_broadcast(value=False)
    elif 'set_pos' in args:
      if len(args) < 4:
        return usage()
      self.set_base_pos_location(args[1], args[2], args[3])
    elif 'survey' in args:
      self.cmd_redo_survey()
    else:
      usage()

  def toggle_base_pos_broadcast(self, value=False, save=True):
    if not self.framer:
      return False

    section = "surveyed_position"
    name    = "broadcast"
    settingValue   = "False"
    
    if value:
      settingValue = "True"

    print "module_SBPUDPBroadcast: Broadcast base pos location: ", settingValue

    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, settingValue))
    self.framer(msg)
    if save:
      msg = MsgSettingsSave()
      self.framer(msg)
    return True

  def set_base_pos_location(self, lat, lon, alt, save=True):
    '''
    assumes lat, lon, alt are already strings in the decimal degrees
    '''
    if not self.framer:
      return False

    print "module_SBPUDPBroadcast: Setting base pos location: ", lat, lon, alt

    section = "surveyed_position"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, "surveyed_lat", lat))
    self.framer(msg)
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, "surveyed_lon", lon))
    self.framer(msg)
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, "surveyed_alt", alt))
    self.framer(msg)
    if save:
      msg = MsgSettingsSave()
      self.framer(msg)
    return True

  def disable_piksi_sim(self, save=True):
    if not self.framer:
      return False

    section = "simulator"
    name    = "enabled"
    value   = "False"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
    self.framer(msg)
    if save:
      msg = MsgSettingsSave()
      self.framer(msg)
    return True

  def enable_piksi_sim(self, save=True):
    if not self.framer:
      return False

    section = "simulator"
    name    = "enabled"
    value   = "True"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
    self.framer(msg)
    if save:
      msg = MsgSettingsSave()
      self.framer(msg)
    return True

  def cmd_status(self):
    if self.last_sent == None:
      print self, "no observation broadcasted yet. handle=",self.driver

    else:
      print self, "last broadcast message %.3fs ago" % (time.time() - self.last_sent)

    if self.surveyed_samples < self.samples_to_avg_over:
      print "CURRENTLY SURVEYING!"
    else:
      print "SURVEYING DONE!"
    print "  Surveyed Average: %.6f, %.6f, %.5f" % (self.surveyed_lat, self.surveyed_lon, self.surveyed_alt)
    print "  Surveyed Samples %d/%d" % (self.surveyed_samples, self.samples_to_avg_over)

  def get_handler(self):
    return self.handler

def init(main, instance_name=None):
  module = SBPUDPBroadcastModule(
      instance_name,
      main,
      main.config.get_my('sbp-port'), 
      main.config.get_my('sbp-baud'),
      dest=(main.config.get_my('udp-bcast-ip'), main.config.get_my('sbp-udp-bcast-port')),
      interval=main.config.get_my('sbp-bcast-sleep'))
  module.start()
  return module