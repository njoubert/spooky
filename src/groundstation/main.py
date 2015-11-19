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
  def __init__(self):
    self.command_map = {
      'exit'    : (self.cmd_stop,                      'exit gracefully'),
      'status'  : (self.cmd_status,                    'show status'),
      'module'  : (self.cmd_module,                    'manage modules'),
      'config'  : (self.config.cmd_config,             'manage configuration'),
      'reinit'  : (self.cmd_reinit,                    'reconfigures network from config')
    }

  def process_stdin(self, line):
    line = line.strip()
    args = line.split()
    cmd = args[0]

    if cmd == 'help':
      print "Spooky Version %s" % spooky.get_version()
      return

    if not cmd in self.command_map:
      print "Unknown command '%s'" % line.encode('string-escape')
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
      return
    else:
      self.process_stdin(line)

#====================================================================#

class ModuleHandler(object):

  def __init__(self):
    self.modules = []

  def load_module(self, module_name, instance_name=None, forceReload=False):
    ''' 
    Loads and starts a module, 
    stores a reference into self.modules,
    returns a pointer to it
    '''

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

    for (m,p) in self.modules:
      if m.module_name == module_name and (m.singleton or m.instance_name == instance_name):
        if m.singleton:
          print "Module %s only allows a single instance" % (m)
          return
        if not forceReload:
          print "Module %s already loaded" % (m)
          return
        elif forceReload:
          self.unload_module(module_name, instance_name=instance_name)
        
    try:
      modpath = 'groundstation.module_%s' % module_name
      package = import_package(modpath)
      reload(package)
      module = package.init(self, instance_name=instance_name)
      self.modules.append((module, package))
      return module
    except ImportError as msg:
      print traceback.format_exc()

  def unload_module(self, module_name, instance_name=None, quiet=False):
    hasUnloaded = 0
    for (m,p) in self.modules[:]:
      if m.module_name == module_name and (instance_name == None or m.instance_name == instance_name):
        try:
          if hasattr(m, 'stop'):
            m.stop(quiet=quiet)
          self.modules.remove((m,p))
          hasUnloaded += 1
        except Exception as msg:
          print "Failed to unload module"
          traceback.print_exc()

    if hasUnloaded == 0:
      print "Unable to find module '%s' (instance '%s')" % (module_name, instance_name)
      return False
    return True

  def unload_all_modules(self):
    for (m,p) in self.modules[:]:
      self.unload_module(m.module_name)
  
  def reload_module(self, module_name, instance_name=None):
    ''' Reload ALL instances of this module '''
    for (m,p) in self.modules:
      if m.module_name == module_name and (instance_name == None or m.instance_name == instance_name):
        self.load_module(m.module_name, instance_name=m.instance_name, forceReload=True)

  def cmd_module(self, args):
    def print_module_help():
      print "module <status | load module_name (instance_name)| unload module_name (instance_name) | reload module_name (instance_name)>"
      return

    self.check_modules_integrity()

    if len(args) == 0:
      return print_module_help()
    cmd = args[0].strip()

    if cmd == "status":
      print "Modules loaded:"
      for (m,p) in self.modules:
        print "  %s" % (m)
      print "Threads alive:"
      for t in threading.enumerate():
        print " ", t
      
    elif cmd == "load":
      if len(args) == 2:
        self.load_module(args[1])
      elif len(args) == 3:
        self.load_module(args[1], instance_name=args[2])
      else:
        return print_module_help()

    elif cmd == "unload":
      if len(args) == 2:
        self.unload_module(args[1], instance_name=None)
      elif len(args) == 3:
        self.unload_module(args[1], instance_name=args[2])
      else:
        return print_module_help()

    elif cmd == "reload":
      if len(args) == 2:
        self.reload_module(args[1])
      elif len(args) == 3:
        self.reload_module(args[1], instance_name=args[2])
      else:
        return print_module_help()

    else:
      return print_module_help()

  def check_modules_integrity(self):
    for (m,p) in self.modules:
      if not m.isAlive():
        self.unload_module(m.module_name, instance_name=m.instance_name, quiet=True)

#====================================================================#

# Also known as 'MAIN'
class GroundStation(CommandLineHandler, ModuleHandler):

  def __init__(self, config_file, ident):
    self.ident = ident
    self.config = spooky.Configuration(config_file, ident)
    CommandLineHandler.__init__(self)
    ModuleHandler.__init__(self)
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

    self.unload_all_modules()

    if hard:
      sys.exit(1)

  def cmd_stop(self, args):
    self.stop()

  def cmd_status(self, args):
    print "status"

  def configure_network_from_config(self):
    '''
    Will attempt to instantiate everything on our end. 
    Won't reinstantiate running threads, 
    won't interact with remote processes
    '''
    self.load_module('SBPUDPBroadcast')
    for client in self.config.get_network('odroidperson'):
      self.load_module('odroidperson', instance_name=client)

  def cmd_reinit(self, args):
    return self.configure_network_from_config()

  def mainloop(self):

    #Set up our network!
    self.configure_network_from_config()

    # Main command line interface, ensures cleanup on exit 
    while not self.dying:
      # Error handling on the INSIDE so we don't kill app
      try:
        self.handle_terminal_input()
        self.check_modules_integrity()
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
                      default=["actual-server"], nargs=1,
                      help="spoof a custom identifier, by default uses 'server'")
  args = parser.parse_args()

  gs = GroundStation(args.config[0], args.ident[0])
  gs.mainloop()

if __name__ == '__main__':
  main()