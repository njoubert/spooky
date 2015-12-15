# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#
# A Zero-Dependency Network Management Library
#

__all__ = ["ip", "modules", "swift"]

#====================================================================#

import time, socket, sys, os, sys, inspect, signal, traceback
import argparse, json

import threading
import collections
from contextlib import closing

import subprocess

def get_version():
  return subprocess.check_output(["git", "describe", "--dirty", "--always"]).strip()


def find_next_log_filename(prefix):
  i = 0
  while os.path.exists(prefix + "%.7i.pickle" % i):
    i += 1
  return prefix + "%.7i.pickle" % i

#====================================================================#

class DoPeriodically(object):
  '''
  A simple way to call a function every 'period' seconds
  inside a while loop. Doesn't block unless specified.
  '''
  def __init__(self, callback, period):
    self.cb = callback
    self.period = period
    self._last_time = 0

  def tick(self, block=False):
    current_time = time.time()
    if current_time - self._last_time > self.period:
      self._last_time = current_time
      return self.cb()
    elif block:
      sleepiness = self.period - (current_time - self._last_time)
      print "blocking for %fs" % sleepiness
      time.sleep(sleepiness)
      return self.tick(block=True)
    return False

#====================================================================#

class DoEvery(object):
  '''
  A simple way to call a function every 'x' calls
  inside a while loop. Cannot block.
  '''
  def __init__(self, callback, iterations):
    self.cb = callback
    self.iterations = iterations
    self._iters_so_far = 0

  def tick(self):
    self._iters_so_far += 1
    if self._iters_so_far > self.iterations:
      self._iters_so_far = 0
      return self.cb()
    return False

#====================================================================#

class CommandLineHandler(object):
  ''' Responsible for all the command line console features'''
  def __init__(self, command_map={}):
    self.command_map = command_map

  def process_stdin(self, line):
    line = line.strip()
    args = line.split()
    cmd = args[0]

    if cmd == 'help':
      print "Spooky Version %s" % get_version()
      for cmd in self.command_map:
        print cmd.ljust(16), self.command_map[cmd][1]
      return

    if not cmd in self.command_map:
      print "Unknown command '%s'" % line.encode('string-escape')
      return

    (fn, help) = self.command_map[cmd]
    try:
      fn(args[1:])
    except Exception as e:
      print "ERROR in command: %s" % str(e)
      traceback.print_exc()

  def handle_terminal_input(self):
    line = raw_input(">>> ")
    if len(line) == 0:
      return
    else:
      self.process_stdin(line)

#====================================================================#

class Configuration(object):
  '''
  Attempts to be threadsafe.

  Assumes your config is a JSON Object containing at leasT:
    'GLOBALS'
    'NETWORK'
    '<my identifier>'
    '<foreign identifiers>'

  And each identifier contains a list of key-value pairs.
  Thread-safety is only valid for this two-level structure.
  If the second level contains complex objects, thread-safety of 
  modifications the returned value is not guaranteed.
  '''

  def __init__(self, filename, ident, network_ident):
    self._lock = threading.Lock()
    self.ident = ident
    self.network_ident = network_ident
    self.load(filename, ident)

  def load(self, filename, ident):
    self._lock.acquire()
    with open(filename) as data_file:    
      CONFIG = json.load(data_file)
    self.data = CONFIG
    self.ident = ident
    self._lock.release()

  def set_my(self, key, value):
    try:
      self._lock.acquire()
      if key in self.data['GLOBALS']:
        self.data['GLOBALS'][key] = value
      else: 
       self.data[self.ident][key] = value
    finally:
      self._lock.release()

  def get_my(self, key):
    try:
      self._lock.acquire()
      value = None
      if key in self.data[self.ident]:
        value = self.data[self.ident][key]
      elif key in self.data['GLOBALS']:
        value = self.data['GLOBALS'][key]
      if value == None:
        raise KeyError(key)
      else:
        return value
    finally:
      self._lock.release()

  def get_foreign(self, ident, key):
    try:
      self._lock.acquire()
      value = self.data[ident][key]
      return value
    finally:
      self._lock.release()
  
  def get_network(self, key):
    try:
      self._lock.acquire()
      value = self.data[self.network_ident][key]
      return value
    finally:
      self._lock.release()

  def __str__(self):
    z = self.data[self.ident].copy()
    z.update(self.data['GLOBALS'])
    return z.__str__()

  def cmd_config(self, args):
    if len(args) < 1:
      cmd = "list"
    else:
      cmd = args[0].strip()

    if cmd == "help":
      print "config <list|set|unset>"
    elif cmd == "list":
      import pprint
      self._lock.acquire()
      pp = pprint.PrettyPrinter(indent=4)
      pp.pprint(self.data)
      self._lock.release()

#====================================================================#

class BufferedUDPSocket(object):

  def __init__(self):
    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # IF we busy-wait in recvfrom ONLY if there's NOT enough data, 
    # we can use blocking sockets. 
    self._sock.setblocking(1)
    self._sock.settimeout(None)
    self._databuffer = collections.deque()
    self.recv_size = 8192

  def __getattr__(self, name):
    return getattr(self._sock, name)

  def recv(self, bufsize, *flags):
    data, addr = self.recvfrom(bufsize)
    return data

  def recvfrom(self, bufsize, *flags):
    try:
      # Do we also want to run this socket once, even if we have data available?
      # No: we leave it to the outer loop to service this fast enough, else our buffer grows unbounded
      addr = None
      while len(self._databuffer) < bufsize: # Busy-loop
        recvd, addr = self._sock.recvfrom(self.recv_size)
        self._databuffer.extend(recvd)
      data = collections.deque()
      while len(data) < bufsize:
        data.append(self._databuffer.popleft())
      return "".join(data), addr
    except IndexError:
      return "".join(data), addr

class BufferedUDPBroadcastSocket(BufferedUDPSocket):

  def __init__(self, port=5000):
    BufferedUDPSocket.__init__(self)
    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self._sock.bind(('', port))

#====================================================================#

class UDPBroadcaster(object):
  ''' 
  Defines a udp socket in broadcast mode, 
  along with a helper broadcast function
  '''

  def __init__(self, dest=('192.168.2.255', 5000)):
    self.dest = dest
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

  def broadcast(self, msg):
    self.udp.sendto(msg, self.dest)

#====================================================================#

class UDPBroadcastListener(object):
  '''
  Defines a udp socket bound to a broadcast address,
  along with a helper recvfrom function.
  DOES TIMEOUT!
  '''

  def __init__(self, port=5000, timeout=None, blocking=1):
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.udp.settimeout(timeout)
    self.udp.setblocking(blocking)
    self.udp.bind(('', port))

  def recvfrom(self, buffsize):
    return self.udp.recvfrom(buffsize)

#====================================================================#    

class UDPBroadcastListenerHandlerThread(threading.Thread, UDPBroadcastListener):
  '''
  
  DEPRECATED

  Very simple repeater:
    Listens for broadcast data coming in on given port
    Send this data to the given data_callback.
  '''

  def __init__(self, main, data_callback, port=5000):
    threading.Thread.__init__(self)
    UDPBroadcastListener.__init__(self, port=port)
    self.data_callback = data_callback
    self.daemon = True
    self.dying = False

  def run(self):
    while not self.dying:
      try:
          msg, addr = self.recvfrom(4096)
          print "received %s bytes" % str(len(msg))
          if msg:
            self.data_callback(msg)
      except (KeyboardInterrupt, SystemExit):
        raise
      except socket.timeout:
        if self.dying:
          return
      except socket.error:
        traceback.print_exc()

  def stop(self):
    self.dying = True
    self.udp.setblocking(0)

#====================================================================#   

# By Sander Marechal
# http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

import sys, os, time, atexit
from signal import SIGTERM 


'''
EXAMPLE USE CASE:

#!/usr/bin/env python

import sys, time
from daemon import Daemon

class MyDaemon(Daemon):
  def run(self):
    while True:
      time.sleep(1)

if __name__ == "__main__":
  daemon = MyDaemon('/tmp/daemon-example.pid')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: %s start|stop|restart" % sys.argv[0]
    sys.exit(2)


'''
class Daemon:
  """
  A generic daemon class.
  
  Usage: subclass the Daemon class and override the run() method
  """
  def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    self.stdin = stdin
    self.stdout = stdout
    self.stderr = stderr
    self.pidfile = pidfile
  
  def daemonize(self):
    """
    do the UNIX double-fork magic, see Stevens' "Advanced 
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
    """
    try: 
      pid = os.fork() 
      if pid > 0:
        # exit first parent
        sys.exit(0) 
    except OSError, e: 
      sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
      sys.exit(1)
  
    # decouple from parent environment
    # os.chdir("/") 
    os.setsid() 
    os.umask(0) 
  
    # do second fork
    try: 
      pid = os.fork() 
      if pid > 0:
        # exit from second parent
        sys.exit(0) 
    except OSError, e: 
      sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
      sys.exit(1) 
  
    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(self.stdin, 'r')
    so = open(self.stdout, 'a+', 0)
    se = open(self.stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    sys.stdin = si
    sys.stdout = so
    sys.stderr = se

    # write pidfile
    atexit.register(self.delpid)
    pid = str(os.getpid())
    with open(self.pidfile,'w+') as f:
      f.write("%s\n" % pid)

  def delpid(self):
    os.remove(self.pidfile)

  def start(self):
    """
    Start the daemon
    """
    # Check for a pidfile to see if the daemon already runs
    try:
      pf = open(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None
  
    if pid:
      message = "pidfile %s already exist. Daemon already running?\n"
      sys.stderr.write(message % self.pidfile)
      sys.exit(1)
    
    # Start the daemon
    self.daemonize()
    self.run()

  def stop(self):
    """
    Stop the daemon
    """
    # Get the pid from the pidfile
    try:
      pf = open(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None
  
    if not pid:
      message = "pidfile %s does not exist. Daemon not running?\n"
      sys.stderr.write(message % self.pidfile)
      return # not an error in a restart

    # Try killing the daemon process  
    try:
      while 1:
        os.kill(pid, SIGTERM)
        time.sleep(0.1)
    except OSError, err:
      err = str(err)
      if err.find("No such process") > 0:
        if os.path.exists(self.pidfile):
          os.remove(self.pidfile)
      else:
        print str(err)
        sys.exit(1)

  def restart(self):
    """
    Restart the daemon
    """
    self.stop()
    self.start()

  def run(self):
    """
    You should override this method when you subclass Daemon. It will be called after the process has been
    daemonized by start() or restart().
    """
