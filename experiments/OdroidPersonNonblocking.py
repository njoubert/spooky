import time, socket, sys, os, sys, inspect
from contextlib import closing

from .spooky import *

#====================================================================#

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

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
