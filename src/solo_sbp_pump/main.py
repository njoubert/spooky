# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import argparse, json

import threading
from Queue import Queue
from contextlib import closing

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.ip
from spooky import CommandLineHandler
from spooky.modules import ModuleHandler

#====================================================================#

class SoloSBP(object):

  def __init__(self, config, ident):
    print "SoloSBP launching as '%s'" % ident
    self.ident = ident
    self.config = config
    self.modules = ModuleHandler(self, 'solo_sbp_pump')
    self.dying = False
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
            self.stop()

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
    self.dying = True

    self.modules.unload_all_modules()

    if hard:
      sys.exit(1)


  def configure_network_from_config(self):
    '''
    Will attempt to instantiate everything on our end. 
    Won't reinstantiate running threads, 
    won't interact with remote processes
    '''

    bcast_listener = self.modules.load_module('sbpbroadcastlistener')
    solo = self.modules.load_module('solo_sbp_pump', waitTimeout=15.0)
    if solo:
      bcast_listener.set_data_callback(solo.injectGPS)
      print "CONFIGURATON DONE! SoloSBP is ready"

    else:
      print "FAILED TO GET SOLO"  
    

  def mainloop(self):

    #Set up our network!
    self.configure_network_from_config()


    while not self.dying:
      try:
        time.sleep(1)
      except KeyboardInterrupt:
        self.stop()
      except Exception:
        #CRUCIAL! This prevents death from exception
        traceback.print_exc()

#=====================================================================#

def main():

  #All arguments should live in a config file!
  parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Ground Station")
  parser.add_argument("-c", "--config",
                      default=['../config.json'], nargs=1,
                      help="specify the configuration file")
  parser.add_argument("-i", "--ident",
                      default=[''], nargs=1,
                      help="spoof a custom identifier, by default uses your IP address")
  parser.add_argument("-n", "--network",
                      default=['NETWORK'], nargs=1,
                      help="spoof a custom network, by default uses 'NETWORK'")
  args = parser.parse_args()

  ident = args.ident[0]
  if ident == '':
    ident = 'solo_sbp_pump'

  print ident
  network_ident = args.network[0]

  config = spooky.Configuration(args.config[0], ident, network_ident)

  gs = SoloSBP(config, ident)
  gs.mainloop()

if __name__ == '__main__':
  main()