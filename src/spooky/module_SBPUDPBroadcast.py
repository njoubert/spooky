# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback

from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client.drivers.pyftdi_driver import PyFTDIDriver

from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS_LLH, MsgObs
from sbp.settings import SBP_MSG_SETTINGS_WRITE, MsgSettingsWrite

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

  def handle_all(self, msg, **metadata):
    pass

  def handle_basestation_obs(self, msg, **metadata):
    try:
      self.last_sent = time.time()
      self.broadcast(msg.pack())
    except socket.error:

      traceback.print_exc()

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
          
          self.ready()

          #TODO: Get rid of "for msg, metadaya..."

          try:
            for msg, metadata in handler:
              if self.stopped():
                return
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

  def disable_piksi_sim(self):
    if not self.framer:
      return False

    section = "simulator"
    name    = "enabled"
    value   = "False"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
    self.framer(msg)
    return True

  def enable_piksi_sim(self):
    if not self.framer:
      return False

    section = "simulator"
    name    = "enabled"
    value   = "True"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
    self.framer(msg)
    return True

  def cmd_status(self):
    if self.last_sent == None:
      print self, "no observation broadcasted yet. handle=",self.driver

    else:
      print self, "last broadcast message %.3fs ago" % (time.time() - self.last_sent)

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