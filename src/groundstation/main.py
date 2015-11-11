# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect
import argparse, json
from contextlib import closing

from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, MsgObs

# This must be run from the src directory, 
# to correctly have all imports relative to src/
from spooky import *

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

class GroundStation:

  def __init__(self, config):
    self.config = config
    print "Launching with config"
    print config

  def stop(self):
    print "Shutting down!"
    pass

  def mainloop(self):
    try:

      while True:
        time.sleep(1)

    except KeyboardInterrupt:
      self.stop()


#=====================================================================#

def main():
  print "GroundStation"

  #All arguments should live in a config file!
  parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Ground Station")
  parser.add_argument("-c", "--config",
                      default=['../config.json'], nargs=1,
                      help="specify the configuration file")
  parser.add_argument("-i", "--ident",
                      default=["server"], nargs=1,
                      help="spoof a custom identifier, by default uses 'server'")
  args = parser.parse_args()

  with open(args.config[0]) as data_file:    
    CONFIG = json.load(data_file)

  gs = GroundStation(CONFIG[args.ident[0]])
  gs.mainloop()

if __name__ == '__main__':
  main()