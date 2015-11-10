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