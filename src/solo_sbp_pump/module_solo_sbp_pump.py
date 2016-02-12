# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

# General
import time, socket, sys, os, sys, inspect, signal, traceback
import json
import threading
from contextlib import closing
import collections
import binascii

# 3DR Solo-related
import dronekit
from pymavlink import mavutil # Needed for command message definitions

# Spooky
import spooky, spooky.modules, spooky.coords

class SoloSBPPumpModule(spooky.modules.SpookyModule):
  '''
  Module pumps SBP OBS data to Solo
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "solo_sbp_pump", singleton=True)
    self.dronekit_device = self.main.config.get_my('dronekit-device')
    
    self.vehicle = None

    self.last_gps_obs_inject = 0


  def stop(self, quiet=False):
    self.MAYDAY_stop_solo()
    self.disconnect()
    super(SoloModule, self).stop(quiet=quiet)

  # ===========================================================================
  # 3DR SOLO DRONEKIT INTERFACE
  # ===========================================================================

  def connect(self):
    self.disconnect()

    print 'Connecting to vehicle on: %s' % self.dronekit_device
    self.vehicle = dronekit.connect(self.dronekit_device, wait_ready=False)
    
    print "Vehicle Connected!"
    
  def disconnect(self):
    if self.vehicle:
      self.vehicle.close()
      print "Vehicle Disconnected!" 
    self.vehicle = None
    
  def injectGPS(self, sbpPacket):

    self.last_gps_obs_inject = time.time()

    if not self.vehicle:
      return

    
    data = bytearray(sbpPacket.ljust(110))
    import binascii
    while len(data) > 0:
      end = min(110,len(data))
      sendNow = bytearray(data[0:end].ljust(110))
      data = data[end:len(data)]
      length = len(sendNow)
      msg = self.vehicle.message_factory.gps_inject_data_encode(
        0, #target_system
        0, #target_component,
        length,
        sendNow)

      self.vehicle.send_mavlink(msg)


    self.vehicle.send_mavlink(msg)
    print time.time(), "Send GPS Inject to Solo, len=", length


  # ===========================================================================
  # Main Module Runloop
  # ===========================================================================

  def run(self):
    try:

      
      self.connect()

      self.ready()

      while True:
        time.sleep(0.1)

    except SystemExit:
      pass
    except:
      traceback.print_exc()
    finally:
      self.disconnect()


def init(main, instance_name=None):
  module = SoloSBPPumpModule(main, instance_name=instance_name)
  module.start()
  return module
