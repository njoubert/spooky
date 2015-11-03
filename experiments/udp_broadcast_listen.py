# Send UDP broadcast packets

MYPORT = 50000

import sys, time
from socket import *

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

while 1:
    data, addr = s.recvfrom(1024)
    print data, addr   
    time.sleep(0.1)