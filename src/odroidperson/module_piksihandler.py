# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#
#Globally useful stuff
import time, socket, sys, os, sys, inspect, traceback
import argparse, json, binascii
import struct
import logging

#Threading-related:
import threading, Queue
from contextlib import closing

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.ip, spooky.modules

from sbp.client.drivers.base_driver import BaseDriver
from sbp.client.loggers.json_logger import JSONLogger
from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS_LLH, MsgObs
from sbp.navigation import SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME, SBP_MSG_DOPS, SBP_MSG_VEL_NED, SBP_MSG_BASELINE_NED
from sbp.acquisition import SBP_MSG_ACQ_RESULT
from sbp.settings import SBP_MSG_SETTINGS_WRITE, MsgSettingsWrite, SBP_MSG_SETTINGS_SAVE, SBP_MSG_SETTINGS_READ_REQ, SBP_MSG_SETTINGS_READ_RESP, SBP_MSG_SETTINGS_READ_BY_INDEX_REQ, SBP_MSG_SETTINGS_READ_BY_INDEX_RESP, SBP_MSG_SETTINGS_READ_BY_INDEX_DONE
from sbp.piksi import SBP_MSG_RESET, MsgReset
from sbp.system import SBP_MSG_STARTUP, SBP_MSG_HEARTBEAT

class PiksiHandler(spooky.modules.SpookyModule):
  '''
  Responsible for all interaction with Piksi.
  To send data TO piksi, call send_to_piksi() with data.
  Any data received FROM piksi, is transmitted on given UDP socket.

  '''

  def __init__(self, main, port, baud, bind_ip, sbp_bind_port, server_ip, sbp_server_port, raw_sbp_logs_prefix):
    import serial
    spooky.modules.SpookyModule.__init__(self, main, "piksihandler", instance_name=None)
    self.daemon              = True
    self.main                = main
    self.port                = port
    self.baud                = baud
    self.bind_ip             = bind_ip
    self.sbp_bind_port       = sbp_bind_port
    self.server_ip           = server_ip
    self.sbp_server_port     = sbp_server_port
    self.raw_sbp_logs_prefix = raw_sbp_logs_prefix
    self.raw_sbp_log_filename = spooky.find_next_log_filename(
      raw_sbp_logs_prefix + "_" + self.main.ident + "_")

    self._reader_thread = threading.Thread(target=self._reader, name="Reader")
    self._reader_thread.daemon = True

    self._sendToPiksi   = Queue.Queue()
    self._recvFromPiksi = Queue.Queue()

    self.listen_to_sbp_msg = [SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME, SBP_MSG_DOPS, SBP_MSG_VEL_NED, SBP_MSG_SETTINGS_WRITE, SBP_MSG_SETTINGS_SAVE, SBP_MSG_SETTINGS_READ_REQ, SBP_MSG_SETTINGS_READ_RESP, SBP_MSG_SETTINGS_READ_BY_INDEX_REQ, SBP_MSG_SETTINGS_READ_BY_INDEX_RESP, SBP_MSG_SETTINGS_READ_BY_INDEX_DONE, SBP_MSG_STARTUP, SBP_MSG_HEARTBEAT, SBP_MSG_OBS, SBP_MSG_BASELINE_NED]

  def handle_incoming(self, msg, **metadata):
    '''
    Callback for handling incoming SBP messages
    '''
    try:
      self._recvFromPiksi.put(msg.pack(), True, 0.05)
    except Queue.Full:
      print "_recvFromPiksi Queue is full!"
          
  def _reader(self):
    with BaseDriver(self.handle) as driver:
      with Handler(Framer(driver.read, None, verbose=True)) as source:
        with JSONLogger(self.raw_sbp_log_filename) as logger:
          source.add_callback(self.handle_incoming)
          source.add_callback(logger)

          try:
            while not self.wait_on_stop(1.0):
              # Sleep until we get killed. The callback above handles actual stuff.
              # This is very nice for clean shutdown.
              pass

          except (OSError, serial.SerialException):
            print("Piksi disconnected")
            raise SystemExit          
          except Exception:
            traceback.print_exc()

  def disable_piksi_sim(self):
    print 'DISABLING SIM'
    section = "simulator"
    name    = "enabled"
    value   = "False"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
    self.send_to_piksi(msg.to_binary())

  def enable_piksi_sim(self):
    print 'ENABLING SIM'
    section = "simulator"
    name    = "enabled"
    value   = "True"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
    self.send_to_piksi(msg.to_binary())

  def reset_piksi(self):
    print 'RESET PIKSI'
    msg = MsgReset()
    self.send_to_piksi(msg.to_binary())

  def send_to_piksi(self, data):
    '''
    Call from an external thread to enqueue data
    for this thread to upload to Piksi.

    This might block!
    '''
    self._sendToPiksi.put(data, True)

  def run(self):
    import serial 

    try:
      self.handle = serial.Serial(self.port, self.baud, timeout=1)
      self._reader_thread.start()
    except (OSError, serial.SerialException):
      print("Serial device '%s' not found" % self.port)
      print("The following serial devices were detected:")
      import serial.tools.list_ports
      for (name, desc, _) in serial.tools.list_ports.comports():
        if desc[0:4] == "ttyS":
          continue
        if name == desc:
          print("\t%s" % name)
        else:
          print("\t%s (%s)" % (name, desc))
      self.ready()
      
    try:
      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sbp_udp:
        sbp_udp.setblocking(1)
        sbp_udp.settimeout(0.05)
        sbp_udp.bind((self.bind_ip, self.sbp_bind_port))
        print "Module %s bound to %s : %d and sending on to %s : %d" % (self, self.bind_ip, self.sbp_bind_port, self.server_ip, self.sbp_server_port)
        self.sbp_udp = sbp_udp

        self.ready()

        while not self.stopped():

          # Repeating SBP data to Piksi
          try:
            while True:
              data, addr = sbp_udp.recvfrom(4096)
              self.send_to_piksi(data)
          except socket.timeout:
            pass
          except socket.error:
            traceback.print_exc()
            pass

          # Uploading data TO Piksi
          try:
            while not self._sendToPiksi.empty():
              data = self._sendToPiksi.get(False)
              self.handle.write(data)
          except (Queue.Empty, serial.SerialException):
            pass

          # Repeating data FROM Piksi
          try:
            while not self._recvFromPiksi.empty():
              data = self._recvFromPiksi.get(False)
              n = sbp_udp.sendto(data, (self.server_ip, self.sbp_server_port))  
              if len(data) != n:
                print("Piksi->UDP relay, did not send all data!")
              else:
                #print("Piksi->UDP sent %d bytes" % n)
                pass
          except (Queue.Empty):
            pass
          except (socket.error, socket.timeout):
            traceback.print_exc()
            pass



    except (OSError, serial.SerialException):
      print("Piksi disconnected")
      raise SystemExit    

def init(main, instance_name=None):
  module = PiksiHandler(main, 
      main.config.get_my('sbp-port'), 
      main.config.get_my('sbp-baud'), 
      main.bind_ip,
      main.sbp_bind_port,
      main.server_ip,
      main.sbp_server_port,
      main.config.get_my('raw-sbp-logs-prefix'))
  module.start()
  return module
