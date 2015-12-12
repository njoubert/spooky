# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import threading, collections
from contextlib import closing

import spooky, spooky.modules

class OdroidPersonMAVModule(spooky.modules.SpookyModule):
  '''
  This is the Swift Binary Protocol receiver of a remote OdroidPerson.
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "odroidperson_mav", instance_name=instance_name)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.sbp_port = self.main.config.get_foreign(instance_name, 'mav-server-port')
    self.last_update = 0

  def cmd_status(self):
    print self, "last received message at %.2f (%.2fs ago)" % (self.last_update, time.time() - self.last_update)

  def run(self):
    '''Thread loop here'''
    try:

      while not self.wait_on_stop(1.0):
        # Sleep until we get killed. The callback above handles actual stuff.
        # This is very nice for clean shutdown.
        print "MAVModule listening..."
        pass

    except:
      print "FUUU"

def init(main, instance_name=None):
  module = OdroidPersonMAVModule(main, instance_name=instance_name)
  module.start()
  return module