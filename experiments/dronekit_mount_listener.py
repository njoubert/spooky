# Copyright (C) 2016 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time
import dronekit

#Globally useful stuff
import time, socket, sys, os, sys, inspect, traceback
import argparse, json, binascii
import struct
import logging

def callback_mount(vehicle, attr_name, value):
  print time.time(), attr_name, value


def main(device, streamrate):

  print "Connecting to ", device

  vehicle = dronekit.connect(device, rate=streamrate, wait_ready=True)

  print "Vehicle Connected! Setting airpspeed and downloading commands..."

  vehicle.add_attribute_listener('mount', callback_mount)

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    pass
  finally:
    vehicle.close()


if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Solo Mount Listener")
  parser.add_argument("-m", "--master",
                      default=['0.0.0.0:14550'], nargs=1,
                      help="Bind to this IP")
  parser.add_argument("-r", "--rate",
                      default=['10'], nargs=1,
                      help="Bind to this IP")
  args = parser.parse_args()

  main(args.master[0], int(args.rate[0]))