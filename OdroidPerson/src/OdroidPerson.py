import time, socket, sys, os, sys, inspect
from contextlib import closing

def add_relative_to_current_source_file_path_to_sys_path(relpath):
    path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],relpath)))
    if path not in sys.path:
        sys.path.insert(0,path)
add_relative_to_current_source_file_path_to_sys_path("../../")

from spooky import *


UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class OdroidPerson:

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


def main():
  print "OdroidPerson"
  op = OdroidPerson()
  op.mainloop()

if __name__ == '__main__':
  main()