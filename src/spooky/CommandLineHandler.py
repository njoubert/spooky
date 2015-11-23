# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import argparse, json

import spooky

class CommandLineHandler(object):
  ''' Responsible for all the command line console features'''
  def __init__(self):
    self.command_map = {
      'exit'     : (self.cmd_stop,                      'exit gracefully'),
      'status'   : (self.cmd_status,                    'show status'),
      'module'   : (self.modules.cmd_module,            'manage modules'),
      'config'   : (self.config.cmd_config,             'manage configuration'),
      'reinit'   : (self.cmd_reinit,                    'reconfigures network from config'),
      'trigger'  : (self.cmd_trigger,                   'triggers a message across modules'),
      'psim'     : (self.cmd_piksisim,                  'toggles the piksi simulator on connected piksis')
    }

  def process_stdin(self, line):
    line = line.strip()
    args = line.split()
    cmd = args[0]

    if cmd == 'help':
      print "Spooky Version %s" % spooky.get_version()
      for cmd in self.command_map:
        print cmd.ljust(16), self.command_map[cmd][1]
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