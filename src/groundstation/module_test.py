import sys, os, time

import spooky, spooky.modules

class TestModule(spooky.modules.SpookyModule):
  '''
  This is a dumb test module
  '''

  def __init__(self, instance_name, main):
    '''Create a UDP Broadcast socket'''
    spooky.modules.SpookyModule.__init__(self, "test", instance_name, main)

  def run(self):
    '''Thread loop here'''
    try:
      while True:
        if self.stopped():
          return
        print "TestModule, here to annoy you!"
        time.sleep(1.0)
    except SystemExit:
      print "Exit Forced. We're dead."
      return

def init(main, instance_name, args=None):
  module = TestModule(instance_name, main)
  module.start()
  return module
