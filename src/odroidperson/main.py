# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, traceback
import argparse, json

import threading
from Queue import Queue
from contextlib import closing

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky.ip

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class UDPBroadcastListenerThread(threading.Thread):

  def __init__(self, main, port=5000):
    threading.Thread.__init__(self)
    self.main = main
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.udp.settimeout(1.0)
    self.udp.bind(('', port))

  def run(self):
    while True:
      try:
          msg, addr = self.udp.recvfrom(4096)
          print "Message from %s: %s" % (addr, msg)
      except (KeyboardInterrupt, SystemExit):
        raise
      except socket.timeout:
        if self.main.dying:
          return
      except socket.error:
        traceback.print_exc()

  def stop(self):
    self.udp.setblocking(0)

class OdroidPerson:

  def __init__(self, config):
    self.config = config
    self.dying = False
    self.broadcastListenerThread = UDPBroadcastListenerThread(self, port=config['sbp-udp-bcast-port'])
    print "Launching with config"
    print config

  def stop(self):
    print ""
    print "Shutting down!"
    print ""
    self.dying = True
    self.broadcastListenerThread.join(1)

  def mainloop(self):

    self.broadcastListenerThread.start()

    try:

      while True:
        time.sleep(1)

    except KeyboardInterrupt:
      self.stop()

#=====================================================================#

def main():
  try:
    
    print "OdroidPerson"

    #All arguments should live in a config file!
    parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Ground Station")
    parser.add_argument("-c", "--config",
                        default=['../config.json'], nargs=1,
                        help="specify the configuration file")
    parser.add_argument("-i", "--ident",
                        default=[''], nargs=1,
                        help="spoof a custom identifier, by default uses IP")
    args = parser.parse_args()

    #Fill out default args
    if args.ident[0] == '':
      args.ident[0] = spooky.ip.get_lan_ip()

    #Get configuration, with globals overwiting instances
    with open(args.config[0]) as data_file:    
      CONFIG = json.load(data_file)
    config = CONFIG[args.ident[0]]
    config.update(CONFIG["GLOBALS"])

    op = OdroidPerson(config)
    op.mainloop()

  except socket.gaierror:
    print "No internet connection"
    return -1




if __name__ == '__main__':
  main()