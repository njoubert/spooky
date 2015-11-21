import sys, os, time

import threading, Queue

import spooky, spooky.modules


class SystemStateModule(spooky.modules.SpookyModule):
  '''
  THREAD-SAFE MODULE to CENTRALIZE SENSOR NETWORK "STATE VECTOR"
  Other modules stream state updates to this module in a thread-safe way,
  This module coordinates everything, producing a complete system state output
  '''

  def __init__(self, main, instance_name=None):
    self._inputQueue = Queue.Queue()
    self._inputQueueTimeout = 0.5
    self._stateLock = threading.Lock()
    self._state = {}
    spooky.modules.SpookyModule.__init__(self, main, "systemstate", singleton=True)

  def update_partial_state(component, new_state):
    '''Push a new partial state update to the state vector'''
    self._inputQueue.put((component, new_state))

  def _handlePartialUpdate(item):
    '''INTERNAL: Handles a state up.'''
    self._stateLock.acquire()
    (component, new_state) = item
    self._state[component] = new_state
    self._stateLock.release()

  def get_state_str(self):
    self._stateLock.acquire()
    ret = "SYSTEM STATE:\n"
    for s in self._state:
      " %s: %s\n" % (str(s), str(self._state[s]))
    self._stateLock.release()
    return ret

  def run(self):
    '''Thread loop here'''
    try:
      while True:
        if self.stopped():
          return
        try:
          self._handlePartialUpdate(self._inputQueue.get(True, self._inputQueueTimeout))
        except Queue.Empty:
          pass
    except SystemExit:
      print "Exit Forced. We're dead."
      return

def init(main, instance_name=None):
  module = SystemStateModule(main, instance_name=instance_name)
  module.start()
  return module
