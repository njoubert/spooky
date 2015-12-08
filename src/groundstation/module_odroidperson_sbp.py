# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import threading
from contextlib import closing
import collections
import binascii

from sbp.client.drivers.base_driver import BaseDriver
from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS, MsgObs
from sbp.navigation import SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME, SBP_MSG_DOPS, SBP_MSG_BASELINE_NED, SBP_MSG_VEL_NED, SBP_MSG_BASELINE_HEADING
from sbp.navigation import MsgPosLLH, MsgGPSTime, MsgDops, MsgBaselineNED, MsgVelNED, MsgBaselineHeading


import spooky, spooky.modules

class SBPUDPDriver(BaseDriver):

  def __init__(self, bind_ip, bind_port):
    self.bind_ip = bind_ip
    self.bind_port = bind_port
    self.handle = spooky.BufferedUDPSocket()
    self.handle.setblocking(1)
    self.handle.settimeout(1.0) # I THINK this is what we want......
    self.handle.bind((self.bind_ip, self.bind_port))
    self.last_addr = None
    BaseDriver.__init__(self, self.handle)

  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    print "SBPUDPDriver closing handle and exiting..."
    self.handle.close()

  def read(self, size):
    '''
    Invariant: will return size or less bytes.
    Invariant: will read and buffer ALL available bytes on given handle.
    '''
    data, addr = self.handle.recvfrom(size)
    self.last_addr = addr
    return data

  def flush(self):
    pass

  def write(self, s):
    raise IOError

class OdroidPersonSBPModule(spooky.modules.SpookyModule):
  '''
  This is the Swift Binary Protocol receiver of a remote OdroidPerson.
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "odroidperson_sbp", instance_name=instance_name)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.sbp_port = self.main.config.get_foreign(instance_name, 'sbp-server-port')
    self.last_update = 0
  
  def cmd_status(self):
    print self, "last received message at %.2f (%.2fs ago)" % (self.last_update, time.time() - self.last_update)

  def handle_incoming(self, msg, **metadata):
    '''
    Handles incoming SBP messaes
    '''
    self.last_update = time.time()
    msg_instance = msg.__class__.__name__
    self.main.modules.trigger('update_partial_state', self.instance_name, msg_instance, msg)

  def run(self):
    '''Thread loop here'''
    with SBPUDPDriver(self.bind_ip, self.sbp_port) as driver:
      with Handler(Framer(driver.read, None, verbose=True)) as source:

        print "Module %s listening on %s" % (self, self.sbp_port)

        source.add_callback(self.handle_incoming, 
          msg_type=[SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME, SBP_MSG_DOPS, SBP_MSG_BASELINE_NED, SBP_MSG_VEL_NED, SBP_MSG_BASELINE_HEADING])

        while not self.wait_on_stop(1.0):
          # Sleep until we get killed. The callback above handles actual stuff.
          # This is very nice for clean shutdown.
          pass

def init(main, instance_name=None):
  module = OdroidPersonSBPModule(main, instance_name=instance_name)
  module.start()
  return module
