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
import spooky, spooky.modules

class SoloModule(spooky.modules.SpookyModule):
  '''
  Module connects:
    1) Camera API over UDP; to
    2) DroneKit API to fly the drone around


  Input API:

  { 
    msgtype: 'GOTO',
    payload: {
      position: [0,0,0],
      positiondot: [0,0,0],
      lookat: [0,0,0],
      lookatdot: [0,0,0],
      gimbal: [0,0,0],
      gimbaldot: [0,0,0]
    }
  }

  Semantics:

    - coord system: defined by Piksi NED.
    - If you want the quad to hold position, DO NOT SEND A VELOCITY.
    - You can send whatever combination of messages. lookat is priotitized over gimbal.

  State we send to "systemstate":

  {
    mode
    position
    velocity
    gimbal deets...
  }
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "solo", singleton=True)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.bind_port = self.main.config.get_my('camera_cc_port')
    self.dronekit_device = self.main.config.get_my('dronekit-device')
    self.vehicle = None
    self.vehicle_hb_threashold = 2.0

  # ===========================================================================
  # 3DR SOLO DRONEKIT INTERFACE
  # ===========================================================================



  # ===========================================================================
  # UDP-BASED CAMERA API
  # ===========================================================================

  def camapi_goto(self, msg):
    if not 'payload' in msg:
      return False

    msg = msg['payload']

    print "PRETENDING TO SEND STUFF TO QUAD HERE:"
    print msg

    '''
    {u'shotName': u'Reverse: 1', u'shotDuration': 4.0, u'desiredstate': {u'positiondot': [0.0, 0.0, 0.0], u'gimbal': [0.0, 0.0, 4.18879032], u'gimbaldot': [0.0, 0.0, 0.0], u'coord': u'PiksiNED', u'lookat': [0.0, 0.0, -1272.421], u'lookatdot': [0.0, 0.0, 0.0], u'position': [653.4773, 1131.85583, -1272.421]}}
    '''

    return True

  def handle_camapi(self, data, addr):
    msg = json.loads(data)

    msg_handler = {
      'CAMAPI_GOTO':  self.camapi_goto,       
    }

    if not 'msgtype' in msg:
      print "MALFORMED: message contains no \'msgtype\' field."
      return

    if not msg['msgtype'] in msg_handler:
      print "UNSUPPORTED: message type \'%s\' not supported." % msg['msgtype']
      return
    
    success = msg_handler[msg['msgtype']](msg)

    if not success:
      print "FAILED: message type \'%s\' failed to execute properly" % msg['msgtype']


  # ===========================================================================
  # Command Line Access
  # ===========================================================================

  def cmd_status(self):
    if self.vehicle:
      print "Vehicle state:"
      print " Global Location: %s" % self.vehicle.location.global_frame
      print " Global Location (relative altitude): %s" % self.vehicle.location.global_relative_frame
      print " Local Location: %s" % self.vehicle.location.local_frame
      print " Attitude: %s" % self.vehicle.attitude
      print " Velocity: %s" % self.vehicle.velocity
      print " Battery: %s" % self.vehicle.battery
      print " Last Heartbeat: %s" % self.vehicle.last_heartbeat
      print " Heading: %s" % self.vehicle.heading
      print " Groundspeed: %s" % self.vehicle.groundspeed
      print " Airspeed: %s" % self.vehicle.airspeed
      print " Mode: %s" % self.vehicle.mode.name
      print " Is Armable?: %s" % self.vehicle.is_armable
      print " Armed: %s" % self.vehicle.armed

  def cmd_solo(self, args):

    def usage():
      print args
      print "solo (status|takeoff|land|go|no)"

    if 'status' in args:
      return self.cmd_status()

    return usage()

  # ===========================================================================
  # Main Module Runloop
  # ===========================================================================

  def MAYDAY_stop_solo(self):
    pass

  def check_vehicle(self):
    if self.vehicle.last_heartbeat > self.vehicle_hb_threashold:
      print "SOLO LINK COMPROMISED: Last Heartbeat %.2fs ago" % self.vehicle.last_heartbeat
      print "STOPPING EVERYTHING!"
      self.MAYDAY_stop_solo()

  def run(self):
    try:

      # Configure our SoloLink connection
      print 'Connecting to vehicle on: %s' % self.dronekit_device
      self.vehicle = dronekit.connect(self.dronekit_device, wait_ready=True)

      #todo: set up a high streamrate? what's the solo default?


      CheckIntegrity = spooky.DoPeriodically(self.check_vehicle, 1.0)

      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as camapi_udp:
        camapi_udp.setblocking(1) 
        camapi_udp.settimeout(0.02) # 50Hz
        camapi_udp.bind((self.bind_ip, self.bind_port))

        print "Module %s listening on %s:%s" % (self, self.bind_ip, self.bind_port)

        self.ready()

        while not self.stopped():

          # Exposing a Camera API
          try:
            camapi_data, camapi_addr = camapi_udp.recvfrom(4096)
            self.handle_camapi(camapi_data, camapi_addr)
          except (socket.error, socket.timeout) as e:
            pass

          CheckIntegrity.tick()


    except SystemExit:
      traceback.print_exc()
      return

def init(main, instance_name=None):
  module = SoloModule(main, instance_name=instance_name)
  module.start()
  return module
