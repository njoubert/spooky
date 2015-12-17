# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback
import argparse, json

import threading
from Queue import Queue
from contextlib import closing

'''

This experiment attempts to send python functions from a 
controller thread to an executor thread, so the controller thread
doesn't block on long-running processes.

Also, can we get a callback when its done?

'''


class ControllerThread(threading.Thread):
  '''
  This thread hands off operations to the executor, so it never blocks.
  '''
  def __init__(self, executor):
    threading.Thread.__init__(self)
    self.executor = executor
    self.name = "NIELS"

  def run(self):

    def deferred():
      print "hello", self.name

    self.executor.execute(deferred)


class ExecutorThread(threading.Thread):
  '''
  This thread performs blocking operations...
  '''
  def __init__(self):
    threading.Thread.__init__(self)
    self.queue = Queue()

  def execute(self, blocking):
    self.queue.put((blocking, None, None))

  def execute_with_callback(self, blocking, callback=lambda x: x):
    self.queue.put((blocking, callback, None))

  def execute_with_event(self, blocking, event):
    self.queue.put((blocking, None, event))

  def run(self):
    while True:
      blocking, callback, event = self.queue.get(True) # Block!
      ret = blocking()
      if callback:
        callback(ret)
      if event:
        event.set()


def main():
  executor = ExecutorThread()
  controller = ControllerThread(executor)

  # Kick off our threads:
  executor.start()
  controller.start()

  # We block forever...
  while True:
    try:
      time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
      traceback.print_exc()
      return

main()