import time, socket, sys
import random
from contextlib import closing

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class SimpleScheduler:

  def __init__(self):
    self.tasks = []
    self.lastMs = time.time() * 1e3
    self.avgSleepMs = 0
    self.addTask(1000, self.monitor)

  def addTask(self, run_every_ms, fnct):
    self.tasks.append({'f':fnct, 'run_every': run_every_ms, 'last_run': 0})

  def tick(self):
    currentMs = time.time() * 1e3
    
    for task in self.tasks:
      if currentMs - task['last_run'] > task['run_every']:
        task['last_run'] = currentMs
        task['f']()

    currentMs = time.time() * 1e3
    minUntilNext = 1000
    for task in self.tasks:
      stillWaiting = max(task['run_every'] - (currentMs - task['last_run']), 0)
      minUntilNext = min(minUntilNext, stillWaiting)

    self.avgSleepMs = self.avgSleepMs * 0.7 + minUntilNext * 0.3
    time.sleep(minUntilNext / 1e3)

  def monitor(self):
    print "Scheduler sleeping around", self.avgSleepMs, "ms between tasks"


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