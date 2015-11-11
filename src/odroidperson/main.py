# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect
import argparse, json
from contextlib import closing

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky.ip

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class OdroidPerson:

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

    with open(args.config[0]) as data_file:    
      CONFIG = json.load(data_file)

    if args.ident[0] == '':
      args.ident[0] = spooky.ip.get_lan_ip()

    op = OdroidPerson(CONFIG[args.ident[0]])
    op.mainloop()

  except socket.gaierror:
    print "No internet connection"
    return -1




if __name__ == '__main__':
  main()