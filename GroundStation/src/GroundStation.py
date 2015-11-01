import time, socket, sys
from contextlib import closing

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 19250

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


class Multicast:
  def __init__(self):
    self.recipients = set([])

  def sendto(self, udp, data):
    for addr in self.recipients:
      udp.sendto(data, addr)

  def addRecipient(self, addr):
    self.recipients = self.recipients.union([addr])

  def __str__(self):
    print self.recipients


class GroundStation:
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


def main():
  print "GroundStation"
  gs = GroundStation()
  gs.mainloop()

if __name__ == '__main__':
  main()