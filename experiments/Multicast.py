

#====================================================================#

class Multicast:
  """
  Multicast provides a homebrewed and inefficient but simple multicast solution
  Multicast simply repeats a packet to all registered sockets. 
  """
  def __init__(self):
    self.recipients = set([])

  def sendto(self, udp, data):
    for addr in self.recipients:
      udp.sendto(data, addr)

  def addRecipient(self, addr):
    self.recipients = self.recipients.union([addr])

  def __str__(self):
    print self.recipients