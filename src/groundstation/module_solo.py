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



import numpy

LOCATION_SCALING_FACTOR = 111318.84502145034;

def scale_longitude(llh):
    return numpy.cos(llh[0] * numpy.pi / 180.0)

def llh2ned(llh, llh_ref):
    diffs = numpy.subtract(llh,llh_ref)
    diffs[0] = diffs[0] * LOCATION_SCALING_FACTOR
    diffs[1] = diffs[1] * LOCATION_SCALING_FACTOR * scale_longitude(llh_ref)
    return diffs

def ned2llh(ned, llh_ref):
  lat = llh_ref[0] + (ned[0] / LOCATION_SCALING_FACTOR)
  lng = llh_ref[1] + (ned[1] / (LOCATION_SCALING_FACTOR * scale_longitude(llh_ref)))
  alt = llh_ref[2] - ned[2]
  return numpy.array([lat,lng,alt])

def get_distance_llh(llh1, llh2):
  return numpy.linalg.norm(llh2ned(llh1, llh2))


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
    self.bind_ip  = self.main.config.get_my('listen-on-ip')
    self.bind_port = self.main.config.get_my('camera_cc_port')
    self.dronekit_device = self.main.config.get_my('dronekit-device')
    
    self.vehicle_hb_threashold = 5.0
    self._ENABLE_API = False
    self.statusmsg_API = ""
    
    self.vehicle = None
    self.vehicle_home_ned = [-28157, 25967, 7195]#[0,0,10000]
    self.vehicle_home = None

    self._executor = None
    self.init_executor()

    self.cleared_to_execute = threading.Event()
    self.cleared_to_execute.set()
    self.okay = False

  def init_executor(self):
    if self._executor:
      self._executor.stop()
      # TODO: Potentially CRASH the executor thread here.
    self._executor = spooky.ExecutorThread()
    self._executor.start()


  def stop(self, quiet=False):
    self.MAYDAY_stop_solo()
    self.disconnect()
    super(SoloModule, self).stop(quiet=quiet)

  # ===========================================================================
  # INTERNALS
  # ==========================================================================

  def _spooky_to_vehicle_llh_relative(self, ned):
    '''
    Converts spooky-frame integer mm NED value
    to Drone Global Coordinate Frame with Relative altitude
    '''
    if not self.vehicle_home:
      print "FAILED _spooky_to_vehicle_llh_relative: No vehicle home!"
      return None
    drone_ned = self._spooky_to_vehicle_ned(ned)
    home_llh = [self.vehicle_home.lat, self.vehicle_home.lon, 0]
    return ned2llh(drone_ned, home_llh)

  def _spooky_to_vehicle_ned(self, ned):
    '''
    Converts spooky-frame integer mm NED value
    to Drone-frame float meter NED value
    '''
    if not self.vehicle_home_ned:
      print "_spooky_to_vehicle_ned with no vehicle_home_ned"
      return [
        float(ned[0])/1000.0, 
        float(ned[1])/1000.0, 
        float(ned[2])/1000.0
        ] 
    else:
      return [
        float(ned[0] - self.vehicle_home_ned[0])/1000.0, 
        float(ned[1] - self.vehicle_home_ned[1])/1000.0, 
        float(ned[2] - self.vehicle_home_ned[2])/1000.0
        ]

  def _vehicle_to_spooky_ned(self, ned):
    '''
    Converts a Drone-frame float meter NED value
    to a spooky-frame integer mm NED value
    '''    
    if not self.vehicle_home_ned:
      print "_vehicle_to_spooky_ned with no vehicle_home_ned"
      return [
        int(ned[0] * 1000.0),
        int(ned[1] * 1000.0),
        int(ned[2] * 1000.0)
      ]
    else:
      return [
        int(ned[0]*1000.0) + self.vehicle_home_ned[0], 
        int(ned[1]*1000.0) + self.vehicle_home_ned[1], 
        int(ned[2]*1000.0) + self.vehicle_home_ned[2]
      ]

  # ===========================================================================
  # 3DR SOLO DRONEKIT INTERFACE
  # ===========================================================================

  def connect(self):

    # Configure our SoloLink connection
    def deferred():
      print 'Connecting to vehicle on: %s' % self.dronekit_device
      self.vehicle = dronekit.connect(self.dronekit_device, wait_ready=True)
      #todo: set up a high streamrate? what's the solo default?

      print "Vehicle Connected! Setting airpspeed and downloading commands..."
      
      cmds = self.vehicle.commands
      cmds.download()
      cmds.wait_ready()
      self.vehicle_home = self.vehicle.home_location

      self.vehicle.groundspeed = 0.2 # Make it move SLOWLY
      self.vehicle.airspeed = 0.2

      print "Vehicle Ready!"

    self._executor.execute(deferred)

  def disconnect(self):
    if self.vehicle:
      self.vehicle.close()
    self.vehicle = None
    self.vehicle_home = None
    print "Vehicle Disconnected!"

  def MAYDAY_stop_solo(self):
    if self.vehicle:
      self.vehicle.mode = dronekit.VehicleMode("LOITER")
    self.disable_API()
    self.init_executor()
    if self.vehicle:
      self.vehicle.mode = dronekit.VehicleMode("LOITER")

  def check_vehicle(self):
    ''' We run this periodically in the thread runloop.'''
    if not self.vehicle:
      return
    if self.vehicle.last_heartbeat > self.vehicle_hb_threashold:
      print "SOLO LINK COMPROMISED: Last Heartbeat %.2fs ago" % self.vehicle.last_heartbeat
      print "STOPPING EVERYTHING!"
      self.MAYDAY_stop_solo()

  def enable_API(self):
    print "ENABLING CAMERA API"
    self._ENABLE_API = True

  def disable_API(self):
    print "DISABLING CAMERA API"
    self._ENABLE_API = False

  def arm(self, value=True, timeout=2.0):

    def deferred():
      if not self.vehicle or not self.vehicle.is_armable:
        print " The vehicle is not ready to arm"
        return False
      if value:
        print "Arming into GUIDED mode..."
        self.vehicle.mode    = dronekit.VehicleMode("GUIDED")
        self.vehicle.armed   = True
        armingWait = spooky.BusyWaitWithTimeout(lambda: self.vehicle.armed, 0.1, 5.0)
        if not armingWait.wait():
          print "Vehicle didn't arm in the allotted time..."
          self.vehicle.armed = False
          return False
        else:
          return True
      else:
        print "Disarming"
        self.vehicle.armed   = False

    self._executor.execute(deferred)
    
  def takeoff(self, aTargetAltitude=10.0):

    def deferred():
      if not self.vehicle.armed:
        print "Vehicle is not armed"
        return False

      print "Taking off!"
      self.vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

      # Wait until the self.vehicle reaches a safe height before processing the goto (otherwise the command 
      #  after Vehicle.simple_takeoff will execute immediately).
      while True:
          print " Altitude: ", self.vehicle.location.global_relative_frame.alt      
          if self.vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
              print "Reached target altitude"
              break
          time.sleep(1)

    self._executor.execute(deferred)

  def land(self):
    self._executor.cancel()
    self.vehicle.mode    = dronekit.VehicleMode("Land")

  def rtl(self):
    self._executor.cancel()
    self.vehicle.mode    = dronekit.VehicleMode("RTL")

  def sendLookAtSpookyNED(self, ned, vel=[0,0,0]):
    if not self.vehicle:
      return False
    
    print "sendLookAtSpookyNED", ned
    llh = self._spooky_to_vehicle_llh_relative(ned)
    if llh is None:
      print "Can't look-at, no home location!"
      return

    #roi = dronekit.LocationGlobalRelative(llh[0],llh[1],llh[2])
    #self.vehicle.gimbal.target_location(roi)

    # dronekit.LocationLocal(north, east, down)
    
    msg = self.vehicle.message_factory.command_long_encode(
                                                    1, 1,    # target system, target component
                                                    mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
                                                    0, #confirmation
                                                    0, 0, 0, 0, #params 1-4
                                                    llh[0],
                                                    llh[1],
                                                    llh[2]
                                                    )

    self.vehicle.send_mavlink(msg)

  # #LLH in lat, lon, relative alt. velocity in NED meters per second
  # def sendLookFrom(self, NED, vel=[0,0,0]):
  #   if not self.vehicle.armed:
  #     return

  #   print "sending look from"
  #   dest = Location(llh[0],llh[1],llh[2],is_relative=False)
  #   self.vehicle.commands.goto(dest)

  #   # msg = drone.vehicle.message_factory.set_position_target_global_int_encode(
  #   #           0,  # system time in ms
  #   #           1,  # target system
  #   #           0,  # target component
  #   #           mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
  #   #           448, # ignore accel, take vel and pos
  #   #           int(llh[0] * 1e7),
  #   #           int(llh[1] * 1e7),
  #   #           llh[2],
  #   #           vel[0], vel[1], vel[2], # velocity
  #   #           0, 0, 0, # accel x,y,z
  #   #           0, 0) # yaw, yaw rate

  #   # drone.vehicle.send_mavlink(msg)


  def sendLookFromSpookyNED(self, ned, vel=[0,0,0], useVel=False):
    '''
    Assumes NED is in "mm" integers in our spooky coordinate frame.

    https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED

    '''
    drone_ned = self._spooky_to_vehicle_ned(ned)
    print "sendLookFromSpookyNED ned=", ned, "drone_ned=", drone_ned

    if not self.vehicle:
      return False

    if abs(drone_ned[0]) > 50 or abs(drone_ned[1]) > 50 or (-1*drone_ned[2]) < 1:
      print "LookFrom out of (100,100,-2) bounds... cowarding out..."
      return

    ignoremask = 3520 #ignore yaw stuff, and accel stuff 
    if not useVel:
      ignoremask = ignoremask | 56

    msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
        0,  # system time in ms
        1,  # target system
        0,  # target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        ignoremask, # ignore
        drone_ned[0],
        drone_ned[1],
        drone_ned[2],
        vel[0], vel[1], vel[2], # velocity
        0, 0, 0, # accel x,y,z
        0, 0) # yaw, yaw rate

    self.vehicle.send_mavlink(msg)

    return True

  # ===========================================================================
  # UDP-BASED CAMERA API
  # ===========================================================================

  def camapi_goto(self, msg, prompt=False):
    if not 'payload' in msg:
      return False

    if not self._ENABLE_API:
      self.statusmsg_API = "Received msg %s but camera API not enabled." % msg['msgtype']
      return

    if prompt:
      if not self.cleared_to_execute.isSet():
        return

      self.okay = False
      self.cleared_to_execute.clear()

    msg = msg['payload']

    desiredstate = msg['desiredstate']
    # Unpack payload

    def deferred():
      try:
        if prompt:
          print ""
          print "API CALL: Flying solo to %s looking at %s" % (str(desiredstate['position']), str(desiredstate['lookat']))
          print "This sticks the solo at %s" % str(self._spooky_to_vehicle_ned(desiredstate['position']))
          print "Please type solo <ok>|<no> depending on whether you're okay with this!"
          self.cleared_to_execute.wait()
        if not prompt or self.okay:
          self.sendLookFromSpookyNED(desiredstate['position'])
          self.sendLookAtSpookyNED(desiredstate['lookat'])
        else:
          print "NOPE!"
      except:
          traceback.print_exc()

    self._executor.execute(deferred)

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

    #if not success:
    #  print "FAILED: message type \'%s\' failed to execute properly" % msg['msgtype']


  # ===========================================================================
  # Command Line Access
  # ===========================================================================

  def cmd_status(self):

    print "VEHICLE CONNECTED?", self.vehicle != None
    print "  piksi NED home pos:", self.vehicle_home_ned
    print "SOLO API ENABLED?", self._ENABLE_API
    print "  Solo API last msg:", self.statusmsg_API
    exStatus = self._executor.status()
    print "Executor: Executing? %s Commands in Queue? %d" % (str(exStatus[0]), exStatus[0])
    if self.vehicle:
      print "Vehicle state:"
      print " System Status: %s" % self.vehicle.system_status
      print " Home Location: %s" % self.vehicle.home_location
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

  def cmd_goto(self, n, e, d):
    print "Command to go to (%d,%d,%d) in mm ned spooky frame." % (n, e, d)
    print "Command Result: %s" % self.sendLookFromSpookyNED([n,e,d])

  def cmd_lookat(self, n, e, d):
    print "Command to look at (%d,%d,%d) in mm ned spooky frame." % (n, e, d)
    print "Command Result: %s" % self.sendLookAtSpookyNED([n,e,d])

  def cmd_solo(self, args):

    def usage():
      print "solo (mayday|status|connect|disconnect|arm|takeoff|goto <n> <e> <d>|lookat <n> <e> <d>|rtl|go|stop|set_home <piksi_ip>|ok|no)"
      print args

    if 'mayday' in args:
      return self.MAYDAY_stop_solo()
    elif 'status' in args:
      return self.cmd_status()
    elif 'connect' in args:
      return self.connect()
    elif 'disconnect' in args:
      return self.disconnect()
    elif 'arm' in args:
      self.arm()
      return
    elif 'takeoff' in args:
      self.takeoff()
      return
    elif 'rtl' in args:
      self.rtl()
      return
    elif 'go' in args:
      return self.enable_API()
    elif 'stop' in args:
      return self.disable_API()
    elif 'goto' in args:
      if len(args) < 4:
        return usage()
      return self.cmd_goto(int(args[1]),int(args[2]),int(args[3]))
    elif 'lookat' in args:
      if len(args) < 4:
        return usage()
      return self.cmd_lookat(int(args[1]),int(args[2]),int(args[3]))
    elif 'set_home' in args:
      if len(args) < 2:
        return usage()
      return self.set_home_now(args[1])
    elif 'ok' in args:
      self.okay = True
      self.cleared_to_execute.set()
      return
    elif 'no' in args:
      self.okay = False
      self.cleared_to_execute.set()
      return


    return usage()

  # ===========================================================================
  # Main Module Runloop
  # ===========================================================================

  def set_home_now(self, piksi_ip):
    # OK, we grab the current position of a Piksi baseline
    # and save that as the NED vector to translate from 

    if not self.vehicle:
      print "NO vehicle attached"
      return

    home = self.vehicle.home_location

    systemstate = self.main.modules.get_modules('systemstate')
    
    if not systemstate:
      print "No systemstate loaded, can't grab home."
      return
    systemstate = systemstate[0]

    ned, msg = systemstate.get_piski_baseline_ned(piksi_ip)
    if msg:
      print msg

    self.vehicle_home_ned = ned

  def run(self):
    try:

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