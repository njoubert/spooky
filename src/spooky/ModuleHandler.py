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

class ModuleHandler(object):

  def __init__(self, main, module_root):
    self.main = main
    self.module_root = module_root
    self.modules = []

  def get_modules(self, module_name, instance_name=None):
    mods = []
    for (m,p) in self.modules:
      if m.module_name == module_name and (instance_name == None or m.singleton or m.instance_name == instance_name):
        mods.append((m,p))
    return mods

  def listeners_for(self, attr):
    ''' Iterator over functions on each module that supports this call'''
    for (m,p) in self.modules:
      if hasattr(m, attr):
        yield getattr(m, attr)

  def responds_to(self, attr):
    ''' Iterator over modules that supports this call'''
    for (m,p) in self.modules:
      if hasattr(m, attr):
        yield m

  def trigger(self, attr, *args, **kwargs):
    for f in self.listeners_for(attr):
      f(*args, **kwargs)        

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
        if m.instance_name != instance_name and m.singleton:
          print "Module %s only allows a single instance" % (m)
          return
        if forceReload:
          self.unload_module(module_name, instance_name=instance_name)
        else:
          print "Module %s already loaded" % (m)
          return
        
    modpaths = ['%s.module_%s' % (self.module_root, module_name), 'spooky.module_%s' % module_name]
    for modpath in modpaths:
      try:
        package = import_package(modpath)
        reload(package)
        module = package.init(self.main, instance_name=instance_name)
        if isinstance(module, spooky.modules.SpookyModule):
          self.modules.append((module, package))
          return module
        else:
          ex = "%s.init didn't return instance of SpookyModule" % module_name
          break
      except ImportError as msg:
        ex = '%s\n%s' % (msg, traceback.format_exc())
    print "Failed to load module: %s" % ex
    return None

  def unload_module(self, module_name, instance_name=None, quiet=False):
    hasUnloaded = 0
    modules = self.get_modules(module_name, instance_name=instance_name)
    for (m,p) in modules:
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
      self.unload_module(m.module_name, m.instance_name)
  
  def reload_module(self, module_name, instance_name=None):
    ''' Reload ALL instances of this module '''
    modules = self.get_modules(module_name, instance_name=instance_name)
    for (m,p) in modules:
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