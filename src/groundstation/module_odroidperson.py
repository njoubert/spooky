import time, socket, sys, os, sys, inspect, signal, traceback
from contextlib import closing
import collections

import spooky, spooky.modules


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
    self.cc_port  = self.main.config.get_foreign('127.0.0.1', 'cc-server-port')
    self.sbp_port = self.main.config.get_foreign('127.0.0.1', 'sbp-server-port')
    self.mav_port = self.main.config.get_foreign('127.0.0.1', 'mav-server-port')

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
    print "Handling CC from '%s':'%s'" % (cc_addr, cc_data)
    # self._incoming_cc.extend(cc_data)
    cc_udp.sendto("ACK", cc_addr)

  def handle_sbp(self, sbp_data, sbp_addr, sbp_udp):
    print "Handling SBP from '%s':'%s'" % (sbp_addr, sbp_data)
    pass

  def run(self):
    '''Thread loop here'''


    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
      cc_udp.setblocking(0)
      cc_udp.settimeout(0.0)
      cc_udp.bind((self.bind_ip, self.cc_port))
      self.cc_udp = cc_udp

      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sbp_udp:
        sbp_udp.setblocking(0)
        sbp_udp.settimeout(0.0)
        sbp_udp.bind((self.bind_ip, self.sbp_port))
        self.sbp_udp = sbp_udp

        print "Module %s listening for Command & Control on %s and SBP on %s." % (self, self.cc_port, self.sbp_port)
        try:
          while True:
            if self.stopped():
              return

            try:
              cc_data, cc_addr   = self.cc_udp.recvfrom(4096)
              self.handle_cc(cc_data, cc_addr, self.cc_udp)
            except (socket.error, socket.timeout) as e:
              pass

            try:
              sbp_data, sbp_addr = self.sbp_udp.recvfrom(4096)
              self.handle_sbp(sbp_data, sbp_addr, self.sbp_udp)
            except (socket.error, socket.timeout) as e:
              pass    

        except SystemExit:
          print "Exit Forced. We're dead."
          return

def init(main, instance_name=None):
  module = OdroidPersonModule(main, instance_name=instance_name)
  module.start()
  return module
