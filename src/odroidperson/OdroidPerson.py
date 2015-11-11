import time, socket, sys, os, sys, inspect
from contextlib import closing

from .spooky import *

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

#=====================================================================#

import threading
from Queue import Queue

class OdroidPersonThreadedBlocking:
  def __init__(self):
    self.dying = False
    self._udp_heartbeat_TRD = threading.Thread(target=self._udp_heartbeat_thread)
    self._udp_heartbeat_TRD.daemon = True
    self._udp_recv_TRD      = threading.Thread(target=self._udp_recv_thread)
    self._udp_recv_TRD.daemon = True

  def _udp_heartbeat_thread(self):
    while True:
      try:
        self.udp.sendto("HEARTBEAT", (UDP_SERVER_IP, UDP_SERVER_PORT))
        time.sleep(0.1)
      except socket.error:
        if self.dying:
          return
        raise

  def _udp_recv_thread(self):
    while True:    
      try:
        data, addr = self.udp.recvfrom(1024)
        print data, addr   
      except socket.error:
        if self.dying:
          return
        raise 

  def stop(self):
    print ""
    print "Shutting down"
    print ""
    self.dying = True
    self._udp_heartbeat_TRD.join(0.1)
    self._udp_recv_TRD.join(0.1)

  def mainloop(self):
    try:

      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp:
        udp.setblocking(1)
#        udp.settimeout(None)
        udp.bind((UDP_IP, UDP_PORT))
        self.udp = udp

        self._udp_heartbeat_TRD.start()
        self._udp_recv_TRD.start()

        while True:
          time.sleep(1)

    except KeyboardInterrupt:
      self.stop()


#=====================================================================#

class OdroidPersonNonblocking:
  def __init__(self):
    self.scheduler = SimpleScheduler()

  def udp_send_heartbeat(self):
    self.udp.sendto("HEARTBEAT", (UDP_SERVER_IP, UDP_SERVER_PORT))

  def udp_recv(self):
    try:
      data, addr = self.udp.recvfrom(1024)
      print data, addr
    except socket.timeout:
      pass    

  def mainloop(self):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp:
      udp.setblocking(1)
      udp.settimeout(0.005)
      udp.bind((UDP_IP, UDP_PORT))
      self.udp = udp

      self.scheduler.addTask(500, self.udp_send_heartbeat)
      self.scheduler.addTask(20, self.udp_recv)

      try:
        while True:
          self.scheduler.tick()
      except KeyboardInterrupt:
        pass

#=====================================================================#

def main():
  print "OdroidPerson"
  op = OdroidPersonThreadedBlocking()
  op.mainloop()

if __name__ == '__main__':
  main()