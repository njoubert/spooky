# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import argparse, json

import threading
from Queue import Queue
from contextlib import closing

from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS, MsgObs

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250


class SBPUDPBroadcastThread(threading.Thread, spooky.UDPBroadcaster):
  '''
  For the moment, we just broadcast every OBS coming in.
  If this gives us problems, we can split into two threads,
  one reading OBS, another repeating the last OBS in some error-resilient way.
  '''

  def __init__(self, main, sbp_port, sbp_baud, dest=('192.168.2.255', 5000), interval=0.1):
    '''Create a UDP Broadcast socket'''
    threading.Thread.__init__(self)
    spooky.UDPBroadcaster.__init__(self, dest=dest)
    self.daemon   = True
    self.main     = main
    self.interval = interval
    self.sbp_port = sbp_port
    self.sbp_baud = sbp_baud
    self.last_msg = {} # Keep track of the last message of each type.

  def run(self):
    '''Thread loop here'''
    with PySerialDriver(self.sbp_port, baud=self.sbp_baud) as driver:
      with Handler(Framer(driver.read, driver.write)) as handler:
        try:
          for msg, metadata in handler.filter(SBP_MSG_OBS, SBP_MSG_BASE_POS):
            self.last_msg[msg.msg_type] = msg
            self.broadcast(msg.pack())
        except KeyboardInterrupt:
          raise
        except socket.error:
          raise

class CommandLineHandler(object):
  ''' Responsible for all the command line console features'''
  def __init__(self):
    self.last_line = ""
    self.command_map = {
      'status'  : (self.cmd_status,   'show status')
    }

  def cmd_status(self):
    print "status"

  def process_stdin(self, line):
    line = line.strip()
    self.last_line = line
    args = line.split()
    cmd = args[0]

    if cmd == 'help':
      print "Spooky Version %s" % spooky.get_version()


  def get_input(self):
    line = raw_input(">>> ")
    if len(line) == 0:
      if len(self.last_line):
        self.process_stdin(self.last_line)
    else:
      self.process_stdin(line)


class GroundStation(CommandLineHandler):

  def __init__(self, config):
    
    CommandLineHandler.__init__(self)

    self.config = config
    self.dying = False
    self.sbpBroadcastThread = SBPUDPBroadcastThread(
      self,
      config['sbp-port'], 
      config['sbp-baud'],
      dest=(config['udp-bcast-ip'], 
      config['sbp-udp-bcast-port']),
      interval=config['sbp-bcast-sleep'])

    self.init_death()


  def init_death(self):  
    '''Setup Graceful Death'''
    def quit_handler(signum = None, frame = None):
        #print 'Signal handler called with signal', signum
        if self.dying:
            print 'Clean shutdown impossible, forcing an exit'
            sys.exit(0)
        else:
            self.dying = True

    # Listen for kill signals to cleanly shutdown modules
    fatalsignals = [signal.SIGTERM]
    try:
      fatalsignals.append(signal.SIGHUP, signal.SIGQUIT)
    except Exception:
      pass

    for sig in fatalsignals:
        signal.signal(sig, quit_handler)

  def stop(self, hard=False):
    print ""
    print "Shutting down"
    print ""
    self.dying = True
    self.sbpBroadcastThread.join(1)
    if hard:
      sys.exit(1)

  def mainloop(self):
    #Fire off all our threads!
    self.sbpBroadcastThread.start()


    # Main command line interface, ensures cleanup on exit 
    while not self.dying:
      # Error handling on the INSIDE so we don't kill app
      try:
        self.get_input()
      except EOFError:
        self.stop(hard=True)
      except KeyboardInterrupt:
        self.stop()
      except Exception:
        #CRUCIAL! This prevents death from exception
        traceback.print_exc()





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