import sys, os, time

import spooky, spooky.modules

class OdroidPersonModule(spooky.modules.SpookyModule):
  '''
  This is the ground station side of a remote OdroidPerson.

  PORT SPEC:
    - Command and Control UDP Port: Listen for Heartbeat and Identifier
    - SBP Reception Port: Listen for data from Piksi
    - MAV Reception Port: Listen for data from Pixhawk
  '''

  def __init__(self, main, instance_name=None):
    spooky.modules.SpookyModule.__init__(self, main, "odroidperson", instance_name=instance_name)

  def run(self):
    '''Thread loop here'''

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
      cc_udp.setblocking(1)
      cc_udp.settimeout(0.5)
      cc_udp.bind((UDP_SERVER_IP, UDP_SERVER_PORT))
      self.cc_udp = udp

      try:
        while True:
          if self.stopped():
            return
                

      except SystemExit:
        print "Exit Forced. We're dead."
        return

def init(main, instance_name=None):
  module = OdroidPersonModule(main, instance_name=instance_name)
  module.start()
  return module
