# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

#Globally useful stuff
import time, socket, sys, os, sys, inspect, traceback
import argparse, json, binascii
import struct
import logging

#Threading-related:
import threading, Queue
from contextlib import closing

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.ip
from spooky import Daemon
from spooky.modules import ModuleHandler

#====================================================================#    

class PiksiBase:

  def __init__(self,  config, ident):
    self.ident  = ident
    self.dying  = False
    self.config = config
    self.send_id = 0
    
    print "PIKSIBASE launching as '%s'" % ident

    self.modules = ModuleHandler(self, 'piksibase')


  def stop(self):
    self.dying = True
    self.modules.unload_all_modules()

  def mainloop(self):

    self.modules.load_module('SBPUDPBroadcast')

    while True:
      time.sleep(1.0)


#=====================================================================#

class PiksiBaseDaemon(Daemon):

  def __init__(self, args, config):
    self.args = args
    self.config = config
    Daemon.__init__(self, '/tmp/PiksiBase.pid', 
        stdin='/dev/null', 
        stdout='/logs/PiksiBase.stdout', 
        stderr='/logs/PiksiBase.stderr')

  def run(self):
    config = self.config
    args = self.args
    pb = PiksiBase(config, args.ident[0])
    pb.mainloop()

#=====================================================================#

def main():
  try:
    print "PiksiBase Launching!"

    #All arguments should live in a config file!
    parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Piksi Base Station UDP Transmitter")
    parser.add_argument("-c", "--config",
                        default=['../config.json'], nargs=1,
                        help="specify the configuration file")
    parser.add_argument("-i", "--ident",
                        default=[''], nargs=1,
                        help="spoof a custom identifier, by default uses IP")
    parser.add_argument("-n", "--network",
                        default=['NETWORK'], nargs=1,
                        help="spoof a custom network, by default uses 'NETWORK'")
    parser.add_argument("-d", "--daemon", 
                        default=[''], nargs=1,
                        help="control daemon. use start/stop/restart")
    args = parser.parse_args()

    #Fill out default args
    if args.ident[0] == '':
      args.ident[0] = spooky.ip.get_lan_ip()

    network_ident = args.network[0]
    config = spooky.Configuration(args.config[0], args.ident[0], network_ident)

    daemon = PiksiBaseDaemon(args, config)

    if args.daemon[0] != '':
      if args.daemon[0] == 'start':
        daemon.start()
      elif args.daemon[0] == 'stop':
        daemon.stop()
      elif args.daemon[0] == 'restart':
        daemon.restart()
      else:
        print "usage: %s --daemon start|stop|restart" % sys.argv[0]
    else:
      daemon.run()

  except socket.gaierror:
    print "No internet connection"
    return -1

if __name__ == '__main__':
  time.sleep(1)
  main()
