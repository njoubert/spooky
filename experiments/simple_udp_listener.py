# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

#Globally useful stuff
import time, socket, sys, os, sys, inspect, traceback
import argparse, json, binascii
import struct
import logging

#Threading-related:
import threading, Queue
from contextlib import closing

def main(ip, port, buffer):
  with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp:
    udp.setblocking(1)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    udp.bind((ip, port))

    print "Listening on udp:%s:%s" % (ip, port)
    while True:
      data, addr = udp.recvfrom(buffer)
      print "%s: %s" % (str(addr), str(data))


if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Simple UDP listener")
  parser.add_argument("-i", "--ip",
                      default=['127.0.0.1'], nargs=1,
                      help="Bind to this IP")
  parser.add_argument("-p", "--port", 
                      default=[19000], nargs=1,
                      help="Bind to this port")
  parser.add_argument("-b", "--buffer",
                      default=[8096], nargs=1,
                      help="Size of UDP buffer in bytes")
  args = parser.parse_args()

  main(args.ip[0], args.port[0], args.buffer[0])