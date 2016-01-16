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
import pprint

def replay_log(logfile, dest, 
    startTime=0.0, 
    debug=False, 
    infoOnly=False, 
    loop=True,
    speedup=1.0,
    end=0.0):
  print "Replaying log %s to %s" % (logfile, str(dest))
  pp = pprint.PrettyPrinter(indent=1)

  with open(logfile, 'rb') as f:

    state = pickle.load(f)

    firstStamp = state['_timestamp']
    nextState = None

    if infoOnly:
      print "Log info:"
      try:
        minN = 10000000
        minE = 10000000
        maxN = -1000000
        maxE = -1000000
        while True:      
          state = pickle.load(f)
          data = json.dumps(state)
          for person in ["192.168.2.51", "192.168.2.52"]:
            if person in state:
              if "MsgBaselineNED" in state[person]:
                minN = min(minN, state[person]["MsgBaselineNED"]["n"])
                minE = min(minE, state[person]["MsgBaselineNED"]["e"])
                maxN = max(maxN, state[person]["MsgBaselineNED"]["n"])
                maxE = max(maxE, state[person]["MsgBaselineNED"]["e"])

      finally:
        print "  boundaries: "
        print "    North: [%d mm, %d mm] " % (minN, maxN)
        print "    East:  [%d mm, %d mm] " % (minE, maxE)
        print "  Log created on %s" % time.ctime(os.path.getctime(logfile))
        print "  Log length is %.2fs " % (state['_timestamp'] - firstStamp)
        sys.exit(1)

    try:
      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as state_udp_out:
        state_udp_out.setblocking(1)

        while True:

          # FFWD:
          try:
            if startTime > 0.0:
              print "Fast Forwarding to %.2fs" % startTime
              while (state['_timestamp'] - firstStamp) <= startTime:
                state = pickle.load(f)
          except EOFError:
            print "Specified start point beyond end of file"
            sys.exit(0)

          # SEND:
          try:

            while True:
                
                nextState = pickle.load(f)

                if "solo" in nextState:
                  del nextState["solo"]
                if "solo_sbp" in nextState:
                  del nextState["solo_sbp"]

                data = json.dumps(state)
                try:
                  n = state_udp_out.sendto(data, dest)  
                  if len(data) != n:
                    print("State Output did not send all data!" % self)
                except socket.error as e:
                  print "Socket error! %s" % str(e)

                if debug:
                  pp.pprint(state)

                timediff = (nextState['_timestamp'] - state['_timestamp'])/speedup
                startdiff = state['_timestamp'] - firstStamp
                if (end > 0.0 and startdiff > end):
                  break
                print("Sending state %.2fs from log beginning, then sleeping for %.3fs" % (startdiff, timediff))
                state = nextState
                time.sleep(timediff)
              
          except EOFError:
            if not loop:
              print "Done"
              sys.exit(0)

          finally:
            if loop:
              print "Looping..."
              f.seek(0)
              state = pickle.load(f) 
    except KeyboardInterrupt:
      print ""
      print ""
      print "*** "
      print "*** Good Night, and Good Luck!"
      print "*** "
      sys.exit(0)

def main():
  #All arguments should live in a config file!
  parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Replay Script")
  parser.add_argument("-i", "--ip",
                      default=['127.0.0.1'], nargs=1,
                      help="specify the IP to send the log to")
  parser.add_argument("-p", "--port",
                      default=[19001], nargs=1,
                      help="specify the port to send the log to")
  parser.add_argument("--info",
                      action="store_true",
                      help="print only the info about the log")
  parser.add_argument("-d", "--debug",
                      action="store_true",
                      help="print the state as we are sending it")
  parser.add_argument("-s", "--start",
                      default=[0.0], nargs=1, type=float,
                      help="specify the port to send the log to")
  parser.add_argument("-e", "--end",
                      default=[0.0], nargs=1, type=float,
                      help="specify the port to send the log to")
  parser.add_argument("-x", "--speedup",
                      default=[1.0], nargs=1, type=float,
                      help="specify a speedup factor.")
  parser.add_argument("--dontloop",
                      action="store_true",
                      help="don't loop the log")
  parser.add_argument("log", nargs=1, type=str,
                      help="specify the logfile to load",)
  args = parser.parse_args()

  replay_log(args.log[0],(args.ip[0],args.port[0]), startTime=args.start[0], debug=args.debug, infoOnly=args.info,loop=(not args.dontloop), speedup=args.speedup[0], end=args.end[0])

if __name__ == '__main__':
  main()