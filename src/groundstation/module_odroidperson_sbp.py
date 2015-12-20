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

class SBPUDPDriver(BaseDriver):

  def __init__(self, bind_ip, bind_port):
    self.bind_ip = bind_ip
    self.bind_port = bind_port
    self.handle = spooky.ip.BufferedUDPSocket()
    self.handle.setblocking(1)
    self.handle.settimeout(1.0) # I THINK this is what we want......
    self.handle.bind((self.bind_ip, self.bind_port))
    self.last_addr = None
    BaseDriver.__init__(self, self.handle)

  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    self.handle.close()

  def read(self, size):
    '''
    Invariant: will return size or less bytes.
    Invariant: will read and buffer ALL available bytes on given handle.
    '''
    try:
      data, addr = self.handle.recvfrom(size)
      if addr is not None:
        self.last_addr = addr
      return data
    except:
      return None

  def flush(self):
    pass

  def write(self, s):
    try:
      self.handle.sendto(s, self.last_addr)
    except Exception as e:
      import traceback
      traceback.print_exc()

class SbpMsgCache(object):
  '''
  This object is responsible for performing batching all the
  many incoming SBP messages into coherent state updates:

  Piksi produces a single state (positon, velocity, baseline, etc) as many messages.
  Here we cache them all, and send a single full state update.
  
  DESIGN: First we "learn" what the last message is before we see a new TOW value
  from then on, we cache until we see that message, then we send a state update.
  We also check, every revision, whether a new last message appears.
  As a fallback, we always flush when TOW rolls over.

  Thus: 
    New msg comes in. Save into current cache
    Set last_seen_tow as msg tow
    
  If no LAST_EXPECTED_MSG:
    If TOW rolls over, 
  FLUSH IF: We see the LAST_EXPECTED_MSG or a new TOW:
    If we saw a new TOW, save the previous msg as the LAST_EXPECTED_MSG
  '''

  def __init__(self):
    self._cache = collections.deque()
    self._cache_tow = 0
    self._cache_start = 0
    self._current_expected_last_msg_name = None
    self._current_expected_last_flags = None
    self.IGNORED_LAST_MSG_NAME = ['MsgIarState']

  def dump_and_clear(self, quiet=True):
    '''
    Returns and clears the current cache, if there's something in it.
    Also updates our expectation of what should be in the cache.
    '''
    if len(self._cache) > 0:
      
      cache_temp = list(self._cache)
      self._cache = collections.deque()
      _current_last_msg = cache_temp[-1]
      _current_last_msg_name = cache_temp[-1].__class__.__name__
      msgs = [msg.__class__.__name__ for msg in cache_temp]

      if not quiet:
        print ">>> Pushing status update of %d messages." % len(cache_temp)
        print "    Last message is %s" % _current_last_msg_name
        print "    Last expected message is %s" % self._current_expected_last_msg_name
        print "    Current node latency is %.4fs" % (time.time() - self._cache_start)
        print "    msgs = [%s]" % ",".join(msgs) 

      # Update our expectation of the last message type, including whether it has flags...
      if _current_last_msg_name not in self.IGNORED_LAST_MSG_NAME:
        self._current_expected_last_msg_name = _current_last_msg_name
        if hasattr(_current_last_msg, 'flags'):
          self._current_expected_last_flags = _current_last_msg.flags
        else:
          self._current_expected_last_flags = None

      # Reset our current TOW
      self._cache_tow = 0

      # Return the current batch
      return cache_temp
    return None

  def is_newer_than_current_cache(self, msg):
    return hasattr(msg, 'tow') and self._cache_tow is not 0 and msg.tow > self._cache_tow

  def is_last_expected_message(self, msg):
    return self._current_expected_last_msg_name == msg.__class__.__name__ and (self._current_expected_last_flags == None or self._current_expected_last_flags == msg.flags)

  def cache_it(self, msg):
    self._cache.append(msg)
    if len(self._cache) == 1:
      self._cache_start = time.time()
    if hasattr(msg, 'tow'):
      self._cache_tow = msg.tow

  def handle_new_message(self, msg):
    ret = None
    # Looks like time rolled over!
    if self.is_newer_than_current_cache(msg):
      ret = self.dump_and_clear()
    
    self.cache_it(msg)

    # Looks like we found our final message!
    if self.is_last_expected_message(msg):
      ret = self.dump_and_clear()    

    return ret

class OdroidPersonSBPModule(spooky.modules.SpookyModule):
  '''
  This is the Swift Binary Protocol receiver of a remote OdroidPerson.
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "odroidperson_sbp", instance_name=instance_name)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.sbp_port = self.main.config.get_foreign(instance_name, 'sbp-server-port')
    self.relay_send_port = self.main.config.get_foreign(instance_name, 'sbp-relay-send-port')
    self.relay_recv_port = self.main.config.get_foreign(instance_name, 'sbp-relay-recv-port')
    self.last_update = 0
    self.msg_cache = SbpMsgCache()

  def cmd_status(self):
    print self, "last received message at %.2f (%.2fs ago)" % (self.last_update, time.time() - self.last_update)

  def handle_incoming(self, msg, **metadata):
    '''
    Callback for handling incoming SBP messages
    '''
    self.last_update = time.time()
    msg_instance = msg.__class__.__name__

    maybe_batch = self.msg_cache.handle_new_message(msg)

    if maybe_batch:
      has_rtk_baseline = False
      for msg in maybe_batch:
        if msg.__class__.__name__ == 'MsgBaselineNED':
          if msg.flags == 1:
            has_rtk_baseline = True
      if has_rtk_baseline:
        remove = -1
        for index in range(len(maybe_batch)):
          msg = maybe_batch[index]
          if msg.__class__.__name__ == 'MsgBaselineNED':
            if msg.flags == 0:
              remove = index
        if remove >= 0:
          print "removing msg %d: %s" % (remove, str(maybe_batch[index]))
          del maybe_batch[remove]

      update = [(msg.__class__.__name__, spooky.swift.fmt_dict(msg)) for msg in maybe_batch]
      self.main.modules.trigger('update_partial_state', self.instance_name, update)

  def handle_relay(self, msg, **metadata):
    self.relay_udp.sendto(msg.to_binary(), (self.bind_ip, self.relay_send_port))

  def run(self):
    '''Thread loop here'''
    try:
      with SBPUDPDriver(self.bind_ip, self.sbp_port) as driver:
        with Handler(Framer(driver.read, None, verbose=True)) as source:

          with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as relay_udp:
            relay_udp.setblocking(1)
            relay_udp.settimeout(0.05)
            relay_udp.bind((self.bind_ip, self.relay_recv_port))
            self.relay_udp = relay_udp

            print "Module %s listening on %s : %s and relaying to %s (send: %d, recv: %d)" % (self, self.bind_ip, self.sbp_port, self.bind_ip, self.relay_send_port, self.relay_recv_port)

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
      print "FUUU"

def init(main, instance_name=None):
  module = OdroidPersonSBPModule(main, instance_name=instance_name)
  module.start()
  return module
