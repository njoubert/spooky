# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, traceback
import argparse, json, binascii

import threading
from Queue import Queue
from contextlib import closing

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.ip

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class SBPPump(threading.Thread):

  def __init__(self, main, port, baud):
    import serial
    threading.Thread.__init__(self)
    self.daemon = True
    self.main = main
    self.port = port
    self.baud = baud

    self._dumb_thread = threading.Thread(target=self._dumb_reader, name="Reader")
    self._dumb_thread.daemon = True

    try:
      self.handle = serial.Serial(port, baud, timeout=1)
      self._dumb_thread.start()
    except (OSError, serial.SerialException):
      print
      print "Serial device '%s' not found" % port
      print "The following serial devices were detected:"
      print
      import serial.tools.list_ports
      for (name, desc, _) in serial.tools.list_ports.comports():
        if desc[0:4] == "ttyS":
          continue
        if name == desc:
          print "\t%s" % name
        else:
          print "\t%s (%s)" % (name, desc)
      print
      raise SystemExit
  
  def _dumb_reader(self):
    try:
      while True:
        self.handle.read(1)
    except (OSError, serial.SerialException):
      print
      print "Piksi disconnected"
      print
      raise SystemExit


  def run(self):
    import serial 
    try:
      while True:
        print "spinning!"
        time.sleep(1)


    except (OSError, serial.SerialException):
      print
      print "Piksi disconnected"
      print
      raise SystemExit


    

class SBPUDPBroadcastListenerThread(threading.Thread, spooky.UDPBroadcastListener):

  def __init__(self, main, port=5000):
    threading.Thread.__init__(self)
    spooky.UDPBroadcastListener.__init__(self, port=port)
    self.daemon = True
    self.main = main

  def run(self):
    while True:
      try:
          msg, addr = self.recvfrom(4096)
          print binascii.hexlify(msg)
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
    self.sbpBroadcastListenerThread = SBPUDPBroadcastListenerThread(self, port=config['sbp-udp-bcast-port'])
    self.SBPPump = SBPPump(self, config['sbp-port'], config['sbp-baud'])
    print "Launching with config"
    print config

  def stop(self):
    print ""
    print "Shutting down!"
    print ""
    self.dying = True
    self.sbpBroadcastListenerThread.join(1)
    self.SBPPump.join(1)

  def mainloop(self):

    self.sbpBroadcastListenerThread.start()
    self.SBPPump.start()

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