# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect, signal, traceback

from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client.drivers.pyftdi_driver import PyFTDIDriver

from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS, MsgObs

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.modules

class SBPUDPBroadcastModule(spooky.modules.SpookyModule, spooky.UDPBroadcaster):
  '''
  For the moment, we just broadcast every OBS coming in.
  If this gives us problems, we can split into two threads,
  one reading OBS, another repeating the last OBS in some error-resilient way.
  '''

  def __init__(self, instance_name, main, sbp_port, sbp_baud, dest=('192.168.2.255', 5000), interval=0.1):
    '''Create a UDP Broadcast socket'''
    spooky.modules.SpookyModule.__init__(self, main, "SBPUDPBroadcast", singleton=True)
    spooky.UDPBroadcaster.__init__(self, dest=dest)
    self.interval = interval
    self.sbp_port = sbp_port
    self.sbp_baud = sbp_baud

  def run(self):
    '''Thread loop here'''
    # Problems? See: https://pylibftdi.readthedocs.org/en/latest/troubleshooting.html
    with PyFTDIDriver(self.sbp_baud) as driver:
      with Handler(Framer(driver.read, driver.write)) as handler:
        try:
          for msg, metadata in handler.filter(SBP_MSG_OBS, SBP_MSG_BASE_POS):
            if self.stopped():
              return
            self.broadcast(msg.pack())
        except KeyboardInterrupt:
          raise
        except socket.error:
          raise
        except SystemExit:
          print "Exit Forced. We're dead."
          return

def init(main, instance_name=None):
  module = SBPUDPBroadcastModule(
      instance_name,
      main,
      main.config.get_my('sbp-port'), 
      main.config.get_my('sbp-baud'),
      dest=(main.config.get_my('udp-bcast-ip'), main.config.get_my('sbp-udp-bcast-port')),
      interval=main.config.get_my('sbp-bcast-sleep'))
  module.start()
  return module