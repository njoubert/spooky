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
    BaseDriver.__init__(self, self.handle)

  def read(self, size):
    '''
    Invariant: will return size or less bytes.
    Invariant: will read and buffer ALL available bytes on given handle.
    '''
    return self.handle.recv(size)

  def flush(self):
    pass

  def write(self, s):
    raise IOError

class OdroidPersonModule(spooky.modules.SpookyModule):
  '''
  This is the ground station side of a remote OdroidPerson.

  PORT SPEC:
    - Command and Control UDP Port: Listen for Heartbeat and Identifier
    - SBP Reception Port: Listen for data from Piksi
    - MAV Reception Port: Listen for data from Pixhawk
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "odroidperson", instance_name=instance_name)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.cc_port  = self.main.config.get_foreign(instance_name, 'cc-server-port')
    self.sbp_port = self.main.config.get_foreign(instance_name, 'sbp-server-port')
    self.mav_port = self.main.config.get_foreign(instance_name, 'mav-server-port')

    self._reader_thread = threading.Thread(target=self._thd_sbp)
    self._reader_thread.daemon = True

    # from enum import Enum
    # class CCParserState(Enum):
    #   WAITING     = 0
    #   GET_HEAD    = 1
    #   GET_COMMAND = 2
    #   GET_LEN     = 3
    #   GET_DATA    = 4
    #   GET_FOOTER  = 5

    # self._incoming_cc = collections.deque()
    # self._c_state = CCParserState.WAITING
    # self._c_command = None
    # self._c_len = 0
    # self._c_data = None

  def handle_cc(self, cc_data, cc_addr, cc_udp):
    #print "Handling CC from '%s':'%s'" % (cc_addr, cc_data)
    # self._incoming_cc.extend(cc_data)
    cc_udp.sendto("ACK", cc_addr)

  def handle_sbp(self, sbp_data, sbp_addr, sbp_udp):
    print "Handling SBP from '%s':'%s'" % (sbp_addr, sbp_data)
    pass

  def _thd_sbp(self):
    with SBPUDPDriver(self.bind_ip, self.sbp_port) as driver:
      f = Framer(driver.read, None, verbose=False)
      while True:
        print f.next()

      # with Handler(Framer(driver.read, None, verbose=False)) as source:
      #   try:
      #     for msg, metadata in source:
      #       print "Received %s" % (msg)
      #   except Exception:
      #     traceback.print_exc()


  def run(self):
    '''Thread loop here'''

    self._reader_thread.start()

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
      cc_udp.setblocking(0)
      cc_udp.settimeout(0.0)
      cc_udp.bind((self.bind_ip, self.cc_port))
      self.cc_udp = cc_udp


      print "Module %s listening for Command & Control on %s" % (self, self.cc_port)
      
      try:
        while True:
          if self.stopped():
            return

          try:
            cc_data, cc_addr   = self.cc_udp.recvfrom(4096)
            self.handle_cc(cc_data, cc_addr, self.cc_udp)
          except (socket.error, socket.timeout) as e:
            pass

      except SystemExit:
        print "Exit Forced. We're dead."
        return

def init(main, instance_name=None):
  module = OdroidPersonModule(main, instance_name=instance_name)
  module.start()
  return module
