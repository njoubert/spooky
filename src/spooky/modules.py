# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import threading, ctypes

class SpookyModule(threading.Thread):
  
  def __init__(self, name, main):
    threading.Thread.__init__(self)
    self.daemon   = True
    self._stop    = threading.Event()
    self.main     = main
    self.name     = name
    print "Initializing module '%s'..." % (self.name)

  def start(self):
    super(SpookyModule, self).start()

  def stop(self):
    print "Stopping %s..." % (self.name)
    self._stop.set()
    super(SpookyModule, self).join(1.0)
    if self.isAlive():
      print "Join unsuccessful, attempting to raise SystemExit exception"
      self.raiseExc(SystemExit)

  def stopped(self):
    return self._stop.isSet()

  #See https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
  def _get_my_tid(self):
    """
    determines this (self's) thread id from the context of the caller thread
    """
    if not self.isAlive():
      raise threading.ThreadError("the thread is not active")

    # do we have it cached?
    if hasattr(self, "_thread_id"):
      return self._thread_id

    # no, look for it in the _active dict
    for tid, tobj in threading._active.items():
      if tobj is self:
          self._thread_id = tid
          return tid

    raise Exception("Could not determine thread ID")

  def raiseExc(self, exctype):
    """
    Raises the given exception type in the context of this thread, 
    from the context of the caller's thread.

    If the thread is busy in a system call (time.sleep(),
    socket.accept(), ...), the exception is simply ignored.
    """
    _async_raise( self._get_my_tid(), exctype )

#See https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
def _async_raise(tid, exctype):
  '''Raises an exception in the threads with id tid'''
  if not inspect.isclass(exctype):
      raise TypeError("Only types can be raised (not instances)")
  res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
    ctypes.c_long(tid),
    ctypes.py_object(exctype))
  if res == 0:
      raise ValueError("invalid thread id")
  elif res != 1:
      # "if it returns a number greater than one, you're in trouble,
      # and you should call it again with exc=NULL to revert the effect"
      ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
      raise SystemError("PyThreadState_SetAsyncExc failed")
