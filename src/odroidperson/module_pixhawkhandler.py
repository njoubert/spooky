# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#
#Globally useful stuff
import time, socket, sys, os, sys, inspect, traceback
import json, binascii, struct, logging
import collections

# Threading-related:
import threading, Queue
from contextlib import closing

# PIXHAWK-related
from pymavlink import mavutil

# SPOOKY-related
import spooky, spooky.ip, spooky.modules

#
# SEE THE MAVLINK SPEC HERE https://pixhawk.ethz.ch/mavlink/
#

class PixhawkHandler(spooky.modules.SpookyModule):
  '''
  Responsible for all interaction with Pixhawk.


  # ATTITUDE: The attitude in the aeronautical frame (right-handed, Z-down, X-front, Y-right).
  # GLOBAL_POSITION_INT: The filtered global position (e.g. fused GPS and accelerometers). The position is in GPS-frame (right-handed, Z-up)
  # GPS_RAW_INT:
  # AHRS2: 

  >>> dir(msg)
  ['__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_crc', '_fieldnames', '_header', '_msgbuf', '_payload', '_posted', '_timestamp', '_type', 'array_lengths', 'crc_extra', 'fieldnames', 'format', 'get_crc', 'get_fieldnames', 'get_header', 'get_msgId', 'get_msgbuf', 'get_payload', 'get_seq', 'get_srcComponent', 'get_srcSystem', 'get_type', 'id', 'lengths', 'name', 'native_format', 'ordered_fieldnames', 'orders', 'pack', 'time_usec', 'to_dict', 'to_json', 'xacc', 'xgyro', 'xmag', 'yacc', 'ygyro', 'ymag', 'zacc', 'zgyro', 'zmag']

  '''

  def __init__(self, main, mav_port, mav_streamrate, server_ip, mav_server_port):
    self.mav_port = mav_port
    self.mav_streamrate = mav_streamrate
    self.server_ip = server_ip
    self.mav_server_port = mav_server_port
    self.listen_for_mav = ['ATTITUDE','GLOBAL_POSITION_INT', 'GPS_RAW_INT', 'AHRS2']
    self.report_packet_loss_threshold =  30.0
    spooky.modules.SpookyModule.__init__(self, main, "pixhawkhandler", singleton=True)

  def run(self):
    master=None
    dest_mav_udp=None
    try:
      print "Firing up PIXHAWK Handler on %s" % self.mav_port
      master = mavutil.mavlink_connection(self.mav_port)
      
      print("PIXHAWK: Waiting for heartbeat")
      master.wait_heartbeat()
      print("PIXHAWK: Heartbeat from APM (system %u component %u)" 
        % (master.target_system, master.target_system))

      print("PIXHAWK: Sending all stream request for rate %u" % self.mav_streamrate)
      for i in range(0, 3):
        master.mav.request_data_stream_send(master.target_system, master.target_component,
                                              mavutil.mavlink.MAV_DATA_STREAM_ALL, self.mav_streamrate, 1)

      dest_mav_udp = mavutil.mavlink_connection('udpout:%s:%d' % (self.server_ip, self.mav_server_port))

      # Hook up master to the destination.
      # Any message we receive, we pipe to the destination as well.
      # TODO(njoubert): we might want to filter messages first before sending them!
      master.logfile_raw = dest_mav_udp
      
      self.ready()

      while not self.stopped():
        msg = master.recv_match(type=self.listen_for_mav, blocking=True)
        if not msg or msg is None:
          pass
        if msg.get_type() == 'BAD_DATA':
          continue
        else:
          if master.packet_loss() > self.report_packet_loss_threshold:
            print "PIXHAWK: Incoming packet loss exceeding %.2f%%" % self.report_packet_loss_threshold
          ''' We've already hooked up the sockets to each other up above'''

      print "Exiting!"
      
    except:
      traceback.print_exc()  
    finally:
      print "Shutting down..."
      if master:
        print "Closing Master..."
        master.close()
      if dest_mav_udp:
        print "Closing UDP..."
        dest_mav_udp.close()


def init(main, instance_name=None):
  module = PixhawkHandler(main, 
      main.config.get_my('mav-port'), 
      main.config.get_my('mav-streamrate'), 
      main.server_ip,
      main.mav_server_port)
  module.start()
  return module
