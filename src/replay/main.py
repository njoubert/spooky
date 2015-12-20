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

# Serialization Related
import cPickle as pickle
import json
import copy

def replay_log(logfile, dest):
  print "Replaying log %s to %s" % (logfile, str(dest))

  with open(logfile, 'rb') as f:

    state = pickle.load(f)
    nextState = None
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as state_udp_out:
      state_udp_out.setblocking(1)

      while True:
        nextState = pickle.load(f)
        if not nextState:
          print "LOG DONE!"
          return
        data = json.dumps(state)
        try:
          n = state_udp_out.sendto(data, dest)  
          if len(data) != n:
            print("State Output did not send all data!" % self)
        except socket.error as e:
          print "Socket error! %s" % str(e)

        timediff = nextState['_timestamp'] - state['_timestamp']
        print("sleeping for %.4f" % timediff)
        state = nextState
        time.sleep(timediff)

def main():
  #All arguments should live in a config file!
  parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Replay Script")
  parser.add_argument("-i", "--ip",
                      default=['127.0.0.1'], nargs=1,
                      help="specify the IP to send the log to")
  parser.add_argument("-p", "--port",
                      default=[19001], nargs=1,
                      help="specify the port to send the log to")
  parser.add_argument("log", nargs=1, type=str,
                      help="specify the logfile to load",)
  args = parser.parse_args()

  replay_log(args.log[0],(args.ip[0],args.port[0]))

if __name__ == '__main__':
  main()