# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import threading, collections
from contextlib import closing

# PIXHAWK-related
from pymavlink import mavutil

# SPOOKY-related
import spooky, spooky.modules

class MavBatchCache(object):
  '''
  This takes a stream of incoming MAV messages,
  and batches them into a single update
  '''
  def __init__(self, expected_messages):
    self._expected_messages = expected_messages
    self._cache = collections.deque()
    self._time_boot_ms = 0
    self._time_fudge_ms = 20 # 1/20ms = 50Hz

  def _dump_cache(self, quiet=True):
    ret = list(self._cache)
    self._cache = collections.deque()
    self._time_boot_ms = 0
    if not quiet:
      print "Dumping cache with %d messages" % len(ret)
    return ret

  def cache(self, msg):
    '''
    Adds a message to the cache, 
    and flushes the cache if we have all of them
    '''
    if self._time_boot_ms == 0 and hasattr(msg, 'time_boot_ms'):
      self._time_boot_ms = msg.time_boot_ms

    if not hasattr(msg, 'time_boot_ms') or abs(self._time_boot_ms - msg.time_boot_ms) < self._time_fudge_ms:
      self._cache.append(msg)
    else:
      return self._dump_cache()

    msgs_in_cache = [msg.name for msg in self._cache]
    for msg in self._expected_messages:
      if msg not in msgs_in_cache:
        return None
    return self._dump_cache()
    

class OdroidPersonMAVModule(spooky.modules.SpookyModule):
  '''
  This is the Swift Binary Protocol receiver of a remote OdroidPerson.
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "odroidperson_mav", instance_name=instance_name)
    self.bind_ip  = self.main.config.get_my('my-ip')
    self.mav_port = self.main.config.get_foreign(instance_name, 'mav-server-port')
    self.last_update = 0
    #see odroidperson/module_pixhawkhandler.py
    self.listen_for_mav = ['ATTITUDE','GLOBAL_POSITION_INT']
    self.cache = MavBatchCache(self.listen_for_mav)
    self.report_packet_loss_threshold = 30.0

  def cmd_status(self):
    print self, "last received message at %.2f (%.2fs ago)" % (self.last_update, time.time() - self.last_update)

  def handle_incoming(self, msg):
    maybe_batch = self.cache.cache(msg)
    if maybe_batch:
      update = [(msg.name, msg.to_dict()) for msg in maybe_batch]
      self.main.modules.trigger('update_partial_state', self.instance_name, update)

  def run(self):
    try:

      master = mavutil.mavlink_connection('udpin:%s:%d' % (self.bind_ip, self.mav_port))
      print "Module %s listening on %s" % (self, self.mav_port)

      while not self.stopped():
        msg = master.recv_match(type=self.listen_for_mav, blocking=True)
        if not msg or msg is None:
          pass
        if msg.get_type() == 'BAD_DATA':
          continue
        else:
          self.handle_incoming(msg)
          if master.packet_loss() > self.report_packet_loss_threshold:
            print "PIXHAWK UDP: Incoming packet loss exceeding %.2f%%" % self.report_packet_loss_threshold      

    except:
      traceback.print_exc()
    finally:
      master.close()

def init(main, instance_name=None):
  module = OdroidPersonMAVModule(main, instance_name=instance_name)
  module.start()
  return module