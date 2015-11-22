# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import threading, ctypes

class SpookyModule(threading.Thread):
  '''
  Fundamental building block for error-resistant and robust code.

  Provides a threaded module:
  - Can be hot-loaded and hot-reloaded 
    from the ground station using the 'module' command
  - Keeps exceptions within the scope of this module, 
    so doesn't kill the rest of the app.
  - Can be forced to quit by raising an exception from
    the main thread.

  USAGE:
  - Please check self.stopped() in your run() loop and quit if necessary.
  '''
  def __init__(self, main, module_name, instance_name=None, singleton=False):
    threading.Thread.__init__(self)
    self.daemon          = True
    self._stop           = threading.Event()
    self.main            = main
    self.module_name     = module_name
    self.instance_name   = instance_name
    self.singleton       = singleton
    print "Initializing module %s..." % (self)

  def start(self):
    super(SpookyModule, self).start()

  def stop(self, quiet=False):
    if not quiet:
      print "Stopping module %s" % (self)      
    self._stop.set()
    super(SpookyModule, self).join(1.0)
    if self.isAlive():
      if not quiet:
        print "Join unsuccessful, attempting to raise SystemExit exception"
      self.raiseExc(SystemExit)

  def stopped(self):
    return self._stop.isSet()

  def wait_on_stop(self, timeout):
    ''' 
    Blocks on _stop event for given timeout or until set.
    Returns true if event was triggered.
    '''
    return self._stop.wait(timeout)

  def __str__(self):
    if self.singleton:
      return "'%s' (singleton)" % (self.module_name)
    else:
      return "'%s' (instance='%s')" % (self.module_name, self.instance_name)

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
