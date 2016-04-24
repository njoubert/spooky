# Copyright (C) 2016 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time
import dronekit
from pymavlink import mavutil # Needed for command message definitions

#Globally useful stuff
import time, socket, sys, os, sys, inspect, traceback
import argparse, json, binascii
import struct
import logging



def messing_with_home(vehicle):

  @vehicle.on_message('HEARTBEAT')
  def listener(self, name, m):
    print("MY HEARTBEAT")

  @vehicle.on_message('HOME_POSITION')
  def listener(self, name, msg):
      print("MY HOME_POSITION")
      print(name)
      print(msg)

  # msg = vehicle.message_factory.command_long_encode(
  #     0, # target system
  #     0, # target component
  #     mavutil.mavlink.MAV_CMD_DO_SET_HOME, # command
  #     0,            # confirmation
  #     2,            # param 1
  #     0,            # param 2
  #     0,            # param 3
  #     0,            # param 4
  #     37.371208169, # lat
  #     122.110969,   # lon
  #     75            # alt
  #     )

  # # send command to vehicle
  # vehicle.send_mavlink(msg)


  msg = vehicle.message_factory.command_long_encode(
      0, # target system
      0, # target component
      mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, # command
      0,            # confirmation
      2,            # param 1
      0,            # param 2
      0,            # param 3
      0,            # param 4
      0,            # param 5
      0,            # param 6
      0             # param 7
      )

  # send command to vehicle
  vehicle.send_mavlink(msg)


  cmds = vehicle.commands
  cmds.wait_ready()
  cmds.download()
  cmds.wait_ready()

  print "This is what DroneKit returns"
  print str(vehicle.home_location)


def main(device, streamrate):

  print "Connecting to ", device

  vehicle = dronekit.connect(device, rate=streamrate, wait_ready=True)

  print "Vehicle Connected!"

  messing_with_home(vehicle)

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    pass
  finally:
    vehicle.close()


if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Solo Home Position Experiments")
  parser.add_argument("-m", "--master",
                      default=['0.0.0.0:14550'], nargs=1,
                      help="Bind to this IP")
  parser.add_argument("-r", "--rate",
                      default=['10'], nargs=1,
                      help="Bind to this IP")
  args = parser.parse_args()

  main(args.master[0], int(args.rate[0]))