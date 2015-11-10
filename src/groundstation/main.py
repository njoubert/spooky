# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import time, socket, sys, os, sys, inspect
import argparse
from contextlib import closing

from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, MsgObs

def add_relative_to_current_source_file_path_to_sys_path(relpath):
    path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],relpath)))
    if path not in sys.path:
        sys.path.insert(0,path)
add_relative_to_current_source_file_path_to_sys_path("../../")

from spooky import *

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

DEFAULT_SERIAL_SBP_PORT = "/dev/ttyUSB0"
DEFAULT_SERIAL_SBP_BAUD = 1000000

class GroundStation:

  def __init__(self, 
      sbp_port=DEFAULT_SERIAL_SBP_PORT,
      sbp_baud=DEFAULT_SERIAL_SBP_BAUD):
    self.sbp_port = sbp_port
    self.sbp_baud = sbp_baud


  def stop(self):
    pass

  def mainloop(self):
    print "Firing up with port=%s, baud=%d" % (self.sbp_port, self.sbp_baud)
    try:

      while True:
        time.sleep(1)

    except KeyboardInterrupt:
      self.stop()


#=====================================================================#

def main():
  parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Ground Station")
  parser.add_argument("-s", "--sbp-port",
                      default=[DEFAULT_SERIAL_SBP_PORT], nargs=1,
                      help="specify the serial port to read SBP from.")
  parser.add_argument("-b", "--sbp-baud",
                      default=[DEFAULT_SERIAL_SBP_BAUD], nargs=1,
                      help="specify the baud rate to use.")
  args = parser.parse_args()


  gs = GroundStation(
    sbp_port = args.sbp_port[0],
    sbp_baud = args.sbp_baud[0])

  gs.mainloop()

if __name__ == '__main__':
  main()