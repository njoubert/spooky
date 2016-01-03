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
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS_LLH, MsgObs
from sbp.navigation import SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME, SBP_MSG_DOPS, SBP_MSG_BASELINE_NED, SBP_MSG_VEL_NED, SBP_MSG_BASELINE_HEADING
from sbp.navigation import MsgPosLLH, MsgGPSTime, MsgDops, MsgBaselineNED, MsgVelNED, MsgBaselineHeading
from sbp.piksi import SBP_MSG_IAR_STATE, MsgIarState

import spooky, spooky.modules, spooky.ip, spooky.swift
from spooky.swift import SBPUDPDriver, SbpMsgCache

class SoloSBPModule(spooky.modules.SpookyModule):
  '''
  This is the Swift Binary Protocol receiver of a remote Solo. 

  







  TODO: It's almost identical to the odroidperson_sbp
  The only difference is a few parameters. Seriously, unify the two!
  
  






  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "solo_sbp", singleton=True)
    self.local_bind_ip  = self.main.config.get_my('my-ip')
    self.sololink_bind_ip  = self.main.config.get_my('sololink-my-ip')
    self.solo_sbp_port = self.main.config.get_my('solo-sbp-port')

    self.relay_recv_port = self.main.config.get_my('solo-sbp-relay-recv-port')
    self.relay_send_port = self.main.config.get_my('solo-sbp-relay-send-port')

    self.last_update = 0
    self.msg_cache = SbpMsgCache()
  
  def cmd_status(self):
    if self.last_update == 0:
      print self, "never received message."
    else:
      print self, "last received message %.2fs ago" % (time.time() - self.last_update)

  def handle_incoming(self, msg, **metadata):
    '''
    Callback for handling incoming SBP messages
    '''
    self.last_update = time.time()
    msg_instance = msg.__class__.__name__

    maybe_batch = self.msg_cache.handle_new_message(msg)

    if maybe_batch:
      update = [(msg.__class__.__name__, spooky.swift.fmt_dict(msg)) for msg in maybe_batch]
      self.main.modules.trigger('update_partial_state', "solo_sbp", update)

  def handle_relay(self, msg, **metadata):
    self.relay_udp.sendto(msg.to_binary(), (self.local_bind_ip, self.relay_send_port))

  def run(self):
    '''Thread loop here'''
    try:
      with SBPUDPDriver(self.sololink_bind_ip, self.solo_sbp_port) as driver:
        with Handler(Framer(driver.read, None, verbose=True)) as source:

          with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as relay_udp:
            relay_udp.setblocking(1)
            relay_udp.settimeout(0.05)
            relay_udp.bind((self.local_bind_ip, self.relay_recv_port))
            self.relay_udp = relay_udp

            print "Module %s listening on %s : %s and relaying to %s (send: %d, recv: %d)" % (self, self.sololink_bind_ip, self.solo_sbp_port, self.local_bind_ip, self.relay_send_port, self.relay_recv_port)

            source.add_callback(self.handle_relay)
            source.add_callback(self.handle_incoming, 
              msg_type=[SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME, SBP_MSG_DOPS, SBP_MSG_BASELINE_NED, SBP_MSG_VEL_NED, SBP_MSG_BASELINE_HEADING, SBP_MSG_IAR_STATE])

            self.ready()

            while not self.stopped():

              try:
                data, addr = relay_udp.recvfrom(4096)
                driver.write(data)
              except socket.timeout:
                pass
              except socket.error:
                traceback.print_exc()
    except:
      traceback.print_exc()
      print "SoloLink SBP FUUUU"

def init(main, instance_name=None):
  module = SoloSBPModule(main, instance_name=instance_name)
  module.start()
  return module