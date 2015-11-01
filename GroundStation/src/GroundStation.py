import time, socket, sys, os, sys, inspect
from contextlib import closing

def add_relative_to_current_source_file_path_to_sys_path(relpath):
    path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],relpath)))
    if path not in sys.path:
        sys.path.insert(0,path)
add_relative_to_current_source_file_path_to_sys_path("../../")

from spooky import *

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

#=====================================================================#

import threading
from Queue import Queue

class GroundStationThreaded:
  def __init__(self):
    self.dying = False
    self.multicast = Multicast()
    self._udp_send_sbp_TRD  = threading.Thread(target=self._udp_send_sbp_thread)
    self._udp_send_sbp_TRD.daemon = True
    self._udp_recv_TRD      = threading.Thread(target=self._ubp_recv_thread)
    self._udp_recv_TRD.daemon = True

  def _ubp_recv_thread(self):
    try:
      while True:
        data, addr = self.udp.recvfrom(1024)
        self.multicast.addRecipient(addr)
        print data, addr
    except socket.error as (errno, msg):
      if self.dying:
        return
      raise

  def _udp_send_sbp_thread(self):
    try:
      while True:
        self.multicast.sendto(self.udp, "SBP")
        time.sleep(0.1)
    except socket.error:
      if self.dying:
        return
      raise

  def stop(self):
    print ""
    print "Shutting down"
    print ""
    self.dying = True
    self._udp_send_sbp_TRD.join(0.1)
    self._udp_recv_TRD.join(0.1)

  def mainloop(self):
    try:

      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp:
        udp.setblocking(1)
        udp.settimeout(None)
        udp.bind((UDP_SERVER_IP, UDP_SERVER_PORT))
        self.udp = udp

        self._udp_send_sbp_TRD.start()
        self._udp_recv_TRD.start()

        while True:
          time.sleep(1)

    except KeyboardInterrupt:
      self.stop()


#=====================================================================#

class GroundStationNonblocking:
  def __init__(self):
    self.multicast = Multicast()
    self.scheduler = SimpleScheduler()
  
  def udp_recv_nonblocking(self):
    try:
      data, addr = self.udp.recvfrom(1024)
      self.multicast.addRecipient(addr)
      print data, addr
    except socket.error as (errno, msg):
      if errno == 35:
        pass
      else:
        raise

  def udp_send_sbp(self):
    self.multicast.sendto(self.udp, "SBP")

  def mainloop(self):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp:
      udp.setblocking(0)
      udp.settimeout(0)
      udp.bind((UDP_SERVER_IP, UDP_SERVER_PORT))
      self.udp = udp

      self.scheduler.addTask(100, self.udp_send_sbp)
      self.scheduler.addTask(20, self.udp_recv_nonblocking)

      try:
        while True:
          self.scheduler.tick()
      except KeyboardInterrupt:
        pass

#=====================================================================#

def main():
  print "GroundStation"
  gs = GroundStationThreaded()
  gs.mainloop()

if __name__ == '__main__':
  main()