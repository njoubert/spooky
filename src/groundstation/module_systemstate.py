# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import threading, collections, Queue
from contextlib import closing

# Serialization Related
import cPickle as pickle
import json
import copy

# SPOOKY-related
import spooky, spooky.modules



class SystemStateModule(spooky.modules.SpookyModule):
  '''
  THREAD-SAFE MODULE to CENTRALIZE SENSOR NETWORK "STATE VECTOR"
  Other modules stream state updates to this module in a thread-safe way,
  This module coordinates everything, producing a complete system state output
  '''

  def __init__(self, main, instance_name=None):

    spooky.modules.SpookyModule.__init__(self, main, "systemstate", singleton=True)
    self._inputQueue = Queue.Queue()
    self._inputQueueTimeout = 0.1
    self._stateLock = threading.Lock()
    self._state = {}
    self.RECORDING = False
    dests = self.main.config.get_my('state_destinations')
    self.state_destinations = [(d[0], d[1]) for d in dests]

  def dump_state(self, filelike):
    pickle.dump(self.get_current(), filelike, pickle.HIGHEST_PROTOCOL)

  def get_current(self):
    self._stateLock.acquire()
    current_state = copy.copy(self._state)
    self._stateLock.release()
    current_state['_timestamp'] = time.time()
    return current_state

  def update_partial_state(self, node, iter):
    '''
    Push a new partial state update to the state vector.
    This assumes iter is of the form [(component, new_state),...]
    '''
    for component, new_state in iter: 
      self._inputQueue.put((node, component, new_state))

  def _handlePartialUpdate(self, item):
    '''INTERNAL: Handles a state up.'''
    self._stateLock.acquire()
    (node, component, new_state) = item
    if str(node) not in self._state:
      self._state[str(node)] = dict()
    self._state[str(node)][str(component)] = new_state
    self._state['_lastupdate'] = time.time()
    self._stateLock.release()

  def cmd_status(self):
    print self, self.get_state_str()

  def get_state_str(self):
    self._stateLock.acquire()
    ret = "RECORDING = %s\n" % str(self.RECORDING)
    for s in self._state:
      ret += " %s: %s\n" % (str(s), str(self._state[s]))
    self._stateLock.release()
    return ret

  def cmd_record_start(self):
    print "Recording system state to %s" % self.log_filename
    self.RECORDING = True

  def cmd_record_stop(self):
    print "Pausing recording system state to %s" % self.log_filename 
    self.RECORDING = False

  def cmd_record_next(self):
    self.RECORDING = False
    print "NOT IMPLEMENTED YET."

  def stop(self, quiet=False):
    self.main.unset_systemstate()
    super(SystemStateModule, self).stop(quiet=quiet)

  def run(self):
    try:
      self.main.set_systemstate(self)

      self.log_filename = spooky.find_next_log_filename(self.main.config.get_my("full-state-logs-prefix"))
      print "Opening logfile: %s" % self.log_filename 
      with open(self.log_filename, 'wb') as f:

        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as state_udp_out:
          state_udp_out.setblocking(1)
          state_udp_out.settimeout(0.05)

          print "Module %s sending data on %s" % (self, str(self.state_destinations))

          # TODO(njoubert): Why not wait on the queue itself? 
          # Cause what if nothing comes in, we still wanna update?
          while not self.wait_on_stop(0.1):
            while not self._inputQueue.empty():
              self._handlePartialUpdate(self._inputQueue.get_nowait())

            if self.RECORDING:
              self.dump_state(f)

            data = json.dumps(self.get_current())
            for dest in self.state_destinations:
              n = state_udp_out.sendto(data, dest)  
              if len(data) != n:
                print("%s State Output did not send all data!" % self)
              else:
                #print("Piksi->UDP sent %d bytes" % n)
                pass


    except SystemExit:
      print "Exit Forced. We're dead."
    except:
      traceback.print_exc()
    finally:
      self.main.unset_systemstate()
      

def init(main, instance_name=None):
  module = SystemStateModule(main, instance_name=instance_name)
  module.start()
  return module
