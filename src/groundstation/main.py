# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect
import argparse, json

import threading
from Queue import Queue
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

class UDPBroadcastThread(threading.Thread):

  def __init__(self, 
      dest=('192.168.2.255', 5000), 
      interval=0.1):
    '''Create a UDP Broadcast socket'''
    threading.Thread.__init__(self)
    self.dest     = dest
    self.interval = interval
    self.daemon   = True
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
  def run(self):
    '''Thread loop here'''
    try:  
      while True:
        print "bcasting to %s:%s" % self.dest
        self.udp.sendto("Broadcasting a Message Here", self.dest)
        time.sleep(self.interval)
    except socket.error:
      raise

class GroundStation:

  def __init__(self, config):
    self.config = config
    self.broadcastThread = UDPBroadcastThread(
      dest=(config['udp-bcast-ip'], config['sbp-udp-bcast-port']),
      interval=config['sbp-bcast-sleep'])

    
    print "Launching with config"
    print config

  def stop(self):
    print ""
    print "Shutting down"
    print ""
    self.broadcastThread.join(0.5)

  def mainloop(self):
    #Fire off all our threads!
    self.broadcastThread.start()

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
                      default=["localhost-server"], nargs=1,
                      help="spoof a custom identifier, by default uses 'server'")
  args = parser.parse_args()

  #Get configuration, with globals overwiting instances
  with open(args.config[0]) as data_file:    
    CONFIG = json.load(data_file)
  config = CONFIG[args.ident[0]]
  config.update(CONFIG["GLOBALS"])

  gs = GroundStation(config)
  gs.mainloop()

if __name__ == '__main__':
  main()