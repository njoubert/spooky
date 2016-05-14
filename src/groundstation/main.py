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

from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS_LLH, MsgObs, MsgBasePosLLH

#====================================================================#

# Also known as 'MAIN'
class GroundStation(CommandLineHandler):

  def __init__(self, config, ident):
    print "GROUNDSTATION launching as '%s'" % ident
    self.ident = ident
    self.config = config
    self.modules = ModuleHandler(self, 'groundstation')
    self.dying = False
    self.init_death()
    self.command_map = {
      'exit'     : (self.cmd_stop,                      'exit gracefully'),
      'status'   : (self.cmd_status,                    'show status'),
      'module'   : (self.modules.cmd_module,            'manage modules'),
      'config'   : (self.config.cmd_config,             'manage configuration'),
      'reinit'   : (self.cmd_reinit,                    'reconfigures network from config'),
      'trigger'  : (self.cmd_trigger,                   'triggers a message across modules'),
      'psim'     : (self.cmd_piksisim,                  'toggles the piksi simulator on connected piksis'),
      'preset'   : (self.cmd_piksireset,                 'sends a reset message to a connected piksi (optionally specify an IP)'),
      'shutdown' : (self.cmd_shutdown,                  '(IP) shuts down a single or all nodes in network'),
      'restart'  : (self.cmd_restart,                   '(IP) restart a single or all nodes in network (specify an IP to restart a specific node)'),
      'update'   : (self.cmd_update,                    '(IP) does a git pull and restart on a single or all nodes in network'),
      'record'   : (self.cmd_record,                    'start or stop recording data for a session')
    }
    CommandLineHandler.__init__(self, self.command_map)

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

  def cmd_trigger(self, args):
    if len(args) != 1:
      print "we need one and only one argument"
      return
    self.modules.trigger(args[0])

  def cmd_stop(self, args):
    self.stop()

  def cmd_record(self, args):
    if len(args) > 0:
      if 'start' in args:
        return self.modules.trigger('cmd_record_start')
      elif 'stop' in args:
        return self.modules.trigger('cmd_record_stop')
      elif 'next' in args:
        return self.modules.trigger('cmd_record_next')
    print 'USAGE: record (start|stop|next)'

  def cmd_status(self, args):
    self.modules.trigger("cmd_status")

  def cmd_reinit(self, args):
    if len(args):
      if "--force" in args:
        self.modules.unload_all_modules()
    return self.configure_network_from_config()

  def cmd_piksisim(self, args):
    if len(args) > 0:
      if "t" in args:
        self.modules.trigger("enable_piksi_sim")
      else:
        self.modules.trigger("disable_piksi_sim")
    else:
      self.modules.trigger("enable_piksi_sim")
      print "enabling. use 't' for true and 'f' for false to toggle state."

  def cmd_piksireset(self, args):
    if len(args) > 0:
      self.modules.trigger_on("odroidperson_cc", args[0], "reset_piksi")
    else:
      self.modules.trigger("reset_piksi")

  def cmd_shutdown(self, args):
    if len(args) > 0:
      self.modules.trigger_on("odroidperson_cc", args[0], "cmd_shutdown")
    else:
      self.modules.trigger("cmd_shutdown")

  def cmd_restart(self, args):
    if len(args) > 0:
      self.modules.trigger_on("odroidperson_cc", args[0], "cmd_restart")
    else:
      self.modules.trigger("cmd_restart")

  def cmd_update(self, args):
    if len(args) > 0:
      self.modules.trigger_on("odroidperson_cc", args[0], "cmd_update")
    else:
      self.modules.trigger("cmd_update")


  def configure_network_from_config(self):
    '''
    Will attempt to instantiate everything on our end. 
    Won't reinstantiate running threads, 
    won't interact with remote processes
    '''
    self.modules.load_module('systemstate')

    if self.config.get_my("be-the-basestation"):
      print "I AM THE BASE STATION"
      self.modules.load_module('SBPUDPBroadcast')
    else:
      print "I AM NOT THE BASE STATION"
    
    for client in self.config.get_network('odroidperson'):
       self.modules.load_module('odroidperson_cc', instance_name=client)
       self.modules.load_module('odroidperson_sbp', instance_name=client)
       self.modules.load_module('odroidperson_mav', instance_name=client)

    self.modules.load_module('basestation_sbp')

    solo = self.modules.load_module('solo', waitTimeout=15.0)    
    
    # NJ HACK SIGGRAPH 2016: USB broke off...
    solosbp = self.modules.load_module('solo_sbp')
    
    print "CONFIGURATON DONE! Spooky is ready for your commands:"
    
  def set_systemstate(self, module):
    self.systemstate = module

  def unset_systemstate(self):
    self.systemstate = None

  def get_systemstate(self):
    if self.systemstate:
      return self.systemstate
    else:
      return None

  def mainloop(self):

    #Set up our network!
    self.configure_network_from_config()

    # Main command line interface, ensures cleanup on exit 
    while not self.dying:
      # Error handling on the INSIDE so we don't kill app
      try:
        self.handle_terminal_input()
        self.modules.check_modules_integrity()
      except EOFError:
        self.stop(hard=True)
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
                      default=['192.168.2.1'], nargs=1,
                      help="spoof a custom identifier, by default uses your IP address")
  parser.add_argument("-n", "--network",
                      default=['NETWORK'], nargs=1,
                      help="spoof a custom network, by default uses 'NETWORK'")
  args = parser.parse_args()

  ident = args.ident[0]
  if ident == '':
      ident = spooky.ip.get_lan_ip()
      if ident == "127.0.0.1":
        ident = "localhost-server"

  print ident
  network_ident = args.network[0]

  config = spooky.Configuration(args.config[0], ident, network_ident)

  gs = GroundStation(config, ident)
  gs.mainloop()

if __name__ == '__main__':
  main()