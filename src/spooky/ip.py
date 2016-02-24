# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

import os
import socket
import threading
import collections
import traceback
import time

#====================================================================#   

if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

def get_lan_ip(tries=3, timeout=1.0):
  attempts = 0
  while attempts < tries:
    try:
        
        ip = socket.gethostbyname(socket.gethostname())
        if ip.startswith("127.") and os.name != "nt":
            interfaces = [
                "eth0",
                "eth1",
                "eth2",
                "wlan0",
                "wlan1",
                "wifi0",
                "ath0",
                "ath1",
                "ppp0"
                ]
            for ifname in interfaces:
                try:
                    ip = get_interface_ip(ifname)
                    break
                except IOError:
                    pass
        print "Returning IP", ip
        return ip
    except socket.gaierror:
      print "*******************************"
      print "get_lan_ip gaierror"
      print ""
      traceback.print_exc()
      print ""
      traceback.print_stack()
      print "*******************************"

      attempts += 1
      time.sleep(timeout)

    return "127.0.0.1"

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
