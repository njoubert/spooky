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
from sbp.navigation import SBP_MSG_POS_LLH, MsgPosLLH

import spooky, spooky.modules

class SBPUDPDriver(BaseDriver):

  def __init__(self, bind_ip, bind_port):
    self.bind_ip = bind_ip
    self.bind_port = bind_port
    self.handle = spooky.BufferedUDPSocket()
    self.handle.setblocking(1)
    self.handle.settimeout(None)
    self.handle.bind((self.bind_ip, self.bind_port))
    self.last_addr = None
    BaseDriver.__init__(self, self.handle)

  def __enter__(self):
    print "ENTERING"
    return self
  
  def __exit__(self, type, value, traceback):
    print "EXITING"
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

  def run(self):
    '''Thread loop here'''
    with SBPUDPDriver(self.bind_ip, self.sbp_port) as driver:
      f = Framer(driver.read, None, verbose=False)

      print "Module %s listening on %s" % (self, self.sbp_port)

      while True:
        print f.next()

def init(main, instance_name=None):
  module = OdroidPersonSBPModule(main, instance_name=instance_name)
  module.start()
  return module
