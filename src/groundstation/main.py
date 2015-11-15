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
import spooky

import module_SBPUDPBroadcast
import module_test

#====================================================================#

class CommandLineHandler(object):
  ''' Responsible for all the command line console features'''
  def __init__(self, main):
    self.main = main
    self.last_line = ""
    self.command_map = {
      'status'  : (self.cmd_status,   'show status'),
      'module'  : (self.cmd_module,   'manage modules')
    }

  def cmd_status(self, args):
    print "status"

  def process_stdin(self, line):
    line = line.strip()
    self.last_line = line
    args = line.split()
    cmd = args[0]

    if cmd == 'help':
      print "Spooky Version %s" % spooky.get_version()
      return

    if not cmd in self.command_map:
      print "Unknown command '%s'" % line.encode('string-escape')
      self.last_line = ""
      return

    (fn, help) = self.command_map[cmd]
    try:
      fn(args[1:])
    except Exception as e:
      print "ERROR in command: %s" % str(e)
      traceback.print_exc()

  def handle_terminal_input(self):
    line = raw_input(">>> ")
    if len(line) == 0:
      if len(self.last_line):
        self.process_stdin(self.last_line)
    else:
      self.process_stdin(line)


#====================================================================#

# Also known as 'MAIN'
class GroundStation(CommandLineHandler):

  def __init__(self, config):
    CommandLineHandler.__init__(self, self)
    self.config = config
    self.dying = False
    self.modules = []
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

  def load_module(self, modname):

    def clear_zipimport_cache():
      """Clear out cached entries from _zip_directory_cache.
      See http://www.digi.com/wiki/developer/index.php/Error_messages"""
      import sys, zipimport
      syspath_backup = list(sys.path)
      zipimport._zip_directory_cache.clear()
   
      # load back items onto sys.path
      sys.path = syspath_backup
      # add this too: see https://mail.python.org/pipermail/python-list/2005-May/353229.html
      sys.path_importer_cache.clear()

    # http://stackoverflow.com/questions/211100/pythons-import-doesnt-work-as-expected
    # has info on why this is necessary.

    def import_package(name):
        """Given a package name like 'foo.bar.quux', imports the package
        and returns the desired module."""
        import zipimport
        try:
            mod = __import__(name)
        except ImportError:
            clear_zipimport_cache()
            mod = __import__(name)
            
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    try:
      modpath = 'groundstation.module_%s' % modname
      package = import_package(modpath)
      reload(package)
      module = package.init(self)
      self.modules.append((module, package))
    except ImportError as msg:
      print traceback.format_exc()

  def unload_module(self, modname):
    for (m,p) in self.modules:
      if m.name == modname:
        if hasattr(m, 'stop'):
          m.stop()
        self.modules.remove((m,p))
        return True
    print "Unable to find module '%s'" % modname
    return False

  def cmd_module(self, args):
    def print_module_help():
      print "module <status|load|unload>"
      return

    if len(args) == 0:
      return print_module_help()
    cmd = args[0].strip()

    if cmd == "status":
      print "Modules loaded:"
      for (m,p) in self.modules:
        print "  %s" % m.name
      print "Threads alive:"
      for t in threading.enumerate():
        print " ", t
      return

    if cmd == "load":
      if len(args) < 2:
        return print_module_help()
      self.load_module(args[1])

    if cmd == "unload":
      if len(args) < 2:
        return print_module_help()
      print "unloading %s" % args[1]
      self.unload_module(args[1])

    else:
      return print_module_help()

  def stop(self, hard=False):
    print ""
    print "Shutting down"
    self.dying = True

    for (m,p) in self.modules:
      m.stop()

    if hard:
      sys.exit(1)

  def mainloop(self):

    #Fire off all our modules!
    self.load_module('SBPUDPBroadcast')

    # Main command line interface, ensures cleanup on exit 
    while not self.dying:
      # Error handling on the INSIDE so we don't kill app
      try:
        self.handle_terminal_input()
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