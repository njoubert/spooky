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
    self._inputQueueTimeout = 0.1
    self._stateLock = threading.Lock()
    self._state = {}
    spooky.modules.SpookyModule.__init__(self, main, "systemstate", singleton=True)

  def update_partial_state(self, node, component, new_state):
    '''Push a new partial state update to the state vector'''
    self._inputQueue.put((node, component, new_state))

  def _handlePartialUpdate(self, item):
    '''INTERNAL: Handles a state up.'''
    self._stateLock.acquire()
    (node, component, new_state) = item
    self._state[(node, component)] = new_state
    #print "Just updated %s:%s to %s" % item
    self._stateLock.release()

  def cmd_status(self):
    print self, self.get_state_str()

  def get_state_str(self):
    self._stateLock.acquire()
    ret = ""
    for s in self._state:
      ret += " %s: %s\n" % (str(s), str(self._state[s]))
    self._stateLock.release()
    return ret

  def stop(self, quiet=False):
    self.main.unset_systemstate()
    super(SystemStateModule, self).stop(quiet=quiet)

  def run(self):
    '''Thread loop here'''
    self.main.set_systemstate(self)
    try:
      while not self.wait_on_stop(0.01):
        #Process the queue at 100hz
        while not self._inputQueue.empty():
          self._handlePartialUpdate(self._inputQueue.get_nowait())
        

    except SystemExit:
      print "Exit Forced. We're dead."
      return

def init(main, instance_name=None):
  module = SystemStateModule(main, instance_name=instance_name)
  module.start()
  return module
