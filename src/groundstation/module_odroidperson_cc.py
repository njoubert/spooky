# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import json
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
    self.cc_remote_port = self.main.config.get_foreign(instance_name, 'cc-local-port')
    self.cc_remote_ip   = self.main.config.get_foreign(instance_name, 'my-ip')
    self.cc_send_addr = (self.cc_remote_ip, self.cc_remote_port)

  def cc_ack(self, msg):
    print "ACK RECEIVED"

  def cc_nack(self, msg):
    print "NACK RECEIVED"

  def cc_heartbeat(self, msg):
    print "RECEIVED HEARTBEAT from %s, msg=%s" % (self.cc_remote_ip, msg)
    return True

  def cc_simulator(self, msg):
    return False

  def cc_malformed(self, msg):
    print "CLIENT CLAIMS MALFORMED: %s" % msg['payload']
    return True

  def cc_unsupported(self, msg):
    print "CLIENT CLAIMS UNSUPPORTED: %s" % msg['payload']
    return True

  def send_cc(self, msgtype, payload=None):
    try:
      msg = {'msgtype':msgtype}
      if payload:
        msg['payload'] = payload
      #print "sending message %s to %s, %s" % (msgtype, addr[0], addr[1])
      self.cc_udp.sendto(json.dumps(msg), self.cc_send_addr)
    except socket.error:
      traceback.print_exc()
      raise


  def handle_cc(self, cc_data, cc_addr):
    msg = json.loads(cc_data)

    msg_handler = {
      'ACK':         self.cc_ack,
      'NACK':        self.cc_nack,
      'heartbeat':   self.cc_heartbeat,
      'malformed':   self.cc_malformed,
      'unsupported': self.cc_unsupported,       
    }

    if not 'msgtype' in msg:
      print "MALFORMED: message contains no \'msgtype'\ field."
      return

    if not msg['msgtype'] in msg_handler:
      print "UNSUPPORTED: message type \'%s\' not supported." % msg['msgtype']
      return

    #print "Handling message type %s: %s" % (msg['msgtype'], str(msg))
    
    if msg_handler[msg['msgtype']](msg):
      self.send_cc('ACK')
    else:
      self.send_cc('NACK')


  def enable_piksi_sim(self):
    self.send_cc('simulator', 'True')

  def disable_piksi_sim(self):
    self.send_cc('simulator', 'False')

  def run(self):
    '''Thread loop here'''

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
      cc_udp.setblocking(1)
      cc_udp.settimeout(0.1)
      cc_udp.bind((self.bind_ip, self.cc_port))
      self.cc_udp = cc_udp

      print "Module %s listening on %s" % (self, self.cc_port)
      
      try:
        while True:
          if self.stopped():
            return

          try:
            cc_data, cc_addr = cc_udp.recvfrom(4096)
            self.handle_cc(cc_data, cc_addr)
          except (socket.error, socket.timeout) as e:
            pass

      except SystemExit:
        print "Exit Forced. We're dead."
        return

def init(main, instance_name=None):
  module = OdroidPersonCCModule(main, instance_name=instance_name)
  module.start()
  return module
