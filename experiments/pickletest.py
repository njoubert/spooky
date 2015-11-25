import time, socket, sys, os, sys, inspect, signal, traceback
import argparse, json

try:
    import cPickle as pickle
except:
    import pickle
import pprint
from StringIO import StringIO

'''
My requirements:

- FAST!
- Repeatedly dump a slightly different version of the system state over and over again
- Support large file sizes
- if i don't have to load the whole thing into memory that'd be nice

cPickle with streaming appears to support all of this!


'''

class SystemState(object):

  def __init__(self):
    self.state = {}

  def __str__(self):
    return str(self.state)

  def setState(self, component, state):
    state['timestamp'] = time.time()
    self.state[component] = state


def main():
  # FIRST WE WRITE...
  with open("test.pickle", 'wb') as f:
    s = SystemState()
    i = 0
    while i < 10:
      s.setState("pos", {'x':i, 'y':i**2, 'z':i**4})
      pickle.dump(s, f, pickle.HIGHEST_PROTOCOL)
      f.flush()
      print "dumping..."
      time.sleep(0.05)
      i += 1

  # THEN WE READ...
  with open("test.pickle", 'rb') as f:
    while True:
      try:
        a = pickle.load(f)
        print a
      except EOFError:
        break


if __name__ == '__main__':
  main()
