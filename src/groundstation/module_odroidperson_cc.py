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


class OdroidPersonCCModule(spooky.modules.SpookyModule):
  '''
  This is the Command and Control side of a remote OdroidPerson.
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "odroidperson_cc", instance_name=instance_name)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.cc_port  = self.main.config.get_foreign(instance_name, 'cc-server-port')

  def handle_cc(self, cc_data, cc_addr, cc_udp):
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
    cc_udp.sendto("ACK", cc_addr)

  def run(self):
    '''Thread loop here'''

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
      cc_udp.setblocking(0)
      cc_udp.settimeout(0.0)
      cc_udp.bind((self.bind_ip, self.cc_port))
      self.cc_udp = cc_udp

      print "Module %s listening on %s" % (self, self.cc_port)
      
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
  module = OdroidPersonCCModule(main, instance_name=instance_name)
  module.start()
  return module
