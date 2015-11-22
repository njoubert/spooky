import sys, os, time

import spooky, spooky.modules

class TestModule(spooky.modules.SpookyModule):
  '''
  This is a dumb test module
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "test", instance_name=instance_name)

  def run(self):
    '''Thread loop here'''
    try:
      while not self.wait_on_stop(1.0):
        print "TestModule (instance %s), here to annoy you!" % (self.instance_name)
    except SystemExit:
      print "Exit Forced. We're dead."
      return

def init(main, instance_name=None):
  module = TestModule(main, instance_name=instance_name)
  module.start()
  return module
