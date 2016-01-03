# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

'''

This code is intended to run on Solo.

This provides a bi-directional relay to the Piksi connected Solo

'''

from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client import Handler, Framer
from sbp.client.loggers.udp_logger import UdpLogger

import time, socket, struct, sys, os, sys, inspect, signal, traceback
from contextlib import closing
import threading
from contextlib import closing

DEFAULT_SERIAL_PORT = "/dev/serial/by-id/usb-FTDI_Single_RS232-HS-if00-port0"
DEFAULT_SERIAL_BAUD = 1000000


DEFAULT_UDP_SEND_ADDRESS = "10.1.1.153"
DEFAULT_UDP_SEND_PORT    = 18000

DEFAULT_UDP_BIND_ADDRESS = "0.0.0.0"
DEFAULT_UDP_RECV_PORT    = 18001

def main():

  with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sbp_udp:
    sbp_udp.setblocking(1)
    sbp_udp.settimeout(None)
    sbp_udp.bind((DEFAULT_UDP_BIND_ADDRESS, DEFAULT_UDP_RECV_PORT))

    def handle_incoming(msg, **metadata):
      sbp_udp.sendto(msg.pack(), (DEFAULT_UDP_SEND_ADDRESS, DEFAULT_UDP_SEND_PORT))


    with PySerialDriver(DEFAULT_SERIAL_PORT, DEFAULT_SERIAL_BAUD) as driver:
      with Handler(Framer(driver.read, driver.write)) as handler:

        handler.add_callback(handle_incoming)

        print "***"
        print "*** Solo Relay Running"
        print "***"

        print "Sending to %s : %s" % (DEFAULT_UDP_SEND_ADDRESS, DEFAULT_UDP_SEND_PORT)
        print "Recving on %s : %s" % (DEFAULT_UDP_BIND_ADDRESS, DEFAULT_UDP_RECV_PORT)
        
        try:
          while True:
            data, addr = sbp_udp.recvfrom(4096)
            driver.write(data)
        except KeyboardInterrupt:
          pass


if __name__ == '__main__':
  main()