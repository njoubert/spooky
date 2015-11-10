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

  def _sbp_to_udp_bridge_thread(self):
    with PySerialDriver(args.serial_port[0], args.baud[0]) as driver:
      with Handler(Framer(driver.read, driver.write)) as handler:
        try:
          for msg, metadata in source.filter(SBP_MSG_OBS):
            print msg, metadata
        except:
          pass

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


