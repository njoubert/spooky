# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

#Globally useful stuff
import time, socket, sys, os, sys, inspect, traceback
import argparse, json, binascii
import struct
import logging

#Threading-related:
import threading, Queue
from contextlib import closing

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.ip, spooky.modules

from sbp.client.drivers.base_driver import BaseDriver
from sbp.client.loggers.json_logger import JSONLogger
from sbp.client import Handler, Framer
from sbp.navigation import SBP_MSG_POS_LLH, MsgPosLLH
from sbp.acquisition import SBP_MSG_ACQ_RESULT
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS_LLH, MsgObs
from sbp.settings import SBP_MSG_SETTINGS_WRITE, MsgSettingsWrite

class SBPUDPBroadcastDriver(BaseDriver):

  def __init__(self, bind_port):
    self.handle = spooky.ip.BufferedUDPBroadcastSocket(port=bind_port)
    self.last_addr = None
    BaseDriver.__init__(self, self.handle)

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

class SBPUDPBroadcastListenerHandlerThread(spooky.modules.SpookyModule):
  '''
  Very simple repeater:
    Listens for broadcast data coming in on given port
    Send this data to the given data_callback.
  '''

  def __init__(self, main, port=5000):
    spooky.modules.SpookyModule.__init__(self, main, "sbpbroadcastlistener", instance_name=None)
    self.port = port
    self.data_callback = None
    self.daemon = True
    self.dying = False

  def set_data_callback(self, data_callback):
    self.data_callback = data_callback

  def handle_incoming(self, msg, **metadata):
    try:
      print "Received %i" % len(msg.pack())
      if self.data_callback:
        self.data_callback(msg.pack())
    except Queue.Full:
      logger.warn("_recvFromPiksi Queue is full!")

  def run(self):
    try:

      with SBPUDPBroadcastDriver(self.port) as driver:
        with Handler(Framer(driver.read, None, verbose=True)) as source:

          source.add_callback(self.handle_incoming)
          self.ready()

          while not self.wait_on_stop(1.0):
            pass

    except Exception:
      traceback.print_exc()

def init(main, instance_name=None):
  module = SBPUDPBroadcastListenerHandlerThread(main, 
    port=main.config.get_my('sbp-udp-bcast-port'))
  module.start()
  return module