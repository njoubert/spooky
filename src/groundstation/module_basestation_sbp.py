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

class BaseStationSBPModule(spooky.modules.SpookyModule):
  '''
  This is the Swift Binary Protocol receiver of a remote OdroidPerson.
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "basestation_sbp", instance_name=instance_name)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.sbp_port = self.main.config.get_my('base-pos-relay-port')
    self.last_update = 0

  def cmd_status(self):
    if self.last_update == 0:
      print self, "never received message."
    else:
      print self, "last received message %.2fs ago" % (time.time() - self.last_update)

  def record_base_position(self, msg, **metadata):
    if msg.msg_type == SBP_MSG_BASE_POS_LLH:
      self.main.modules.trigger('update_partial_state', 'base_station', [('surveyed_pos', (msg.lat, msg.lon, msg.height))])


  def run(self):
    '''Thread loop here'''
    try:
      with SBPUDPDriver(self.bind_ip, self.sbp_port) as driver:
        with Handler(Framer(driver.read, None, verbose=True)) as source:


          print "Module %s listening on %s : %s" % (self, self.bind_ip, self.sbp_port)

          source.add_callback(self.record_base_position)

          self.ready()

          while not self.stopped():
            self.wait_on_stop(10)
            
    except:
      traceback.print_exc()
      print "FUUU"

def init(main, instance_name=None):
  module = BaseStationSBPModule(main, instance_name=instance_name)
  module.start()
  return module
