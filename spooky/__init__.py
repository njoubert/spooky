import time, socket, sys
from contextlib import closing


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