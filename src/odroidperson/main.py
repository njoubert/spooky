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

from sbp.client.drivers.base_driver import BaseDriver
from sbp.client import Handler, Framer
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS, MsgObs
from sbp.navigation import SBP_MSG_POS_LLH, MsgPosLLH
from sbp.acquisition import SBP_MSG_ACQ_RESULT

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.ip

#====================================================================#

logger = logging.getLogger("odriodperson")

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

#====================================================================#

class SBPUDPBroadcastDriver(BaseDriver):

  def __init__(self, bind_port):
    self.bind_port = bind_port
    self.handle = spooky.BufferedUDPBroadcastSocket()
    self.last_addr = None
    BaseDriver.__init__(self, self.handle)

  def read(self, size):
    '''
    Invariant: will return size or less bytes.
    Invariant: will read and buffer ALL available bytes on given handle.
    '''
    data, addr = self.handle.recvfrom(size)
    self.last_addr = addr
    return data

  def flush(self):
    pass

  def write(self, s):
    raise IOError

class SBPUDPBroadcastListenerHandlerThread(threading.Thread):
  '''
  Very simple repeater:
    Listens for broadcast data coming in on given port
    Send this data to the given data_callback.
  '''

  def __init__(self, main, data_callback, port=5000):
    threading.Thread.__init__(self)
    self.port = port
    self.data_callback = data_callback
    self.daemon = True
    self.dying = False

  def run(self):
    with SBPUDPBroadcastDriver(self.port) as driver:
      with Handler(Framer(driver.read, None, verbose=True)) as source:
        try:
          for msg, metadata in source:
            if self.dying:
              return
            try:
              self.self.data_callback(msg.pack())
            except Queue.Full:
              logger.warn("_recvFromPiksi Queue is full!")
        except (OSError, serial.SerialException):
          logger.error("Piksi disconnected")
          raise SystemExit          
        except Exception:
          traceback.print_exc()

  def stop(self):
    self.dying = True
    self.udp.setblocking(0)

class PiksiHandler(threading.Thread):
  '''
  Responsible for all interaction with Piksi.
  To send data TO piksi, call send_to_piksi() with data.
  Any data received FROM piksi, is transmitted on given UDP socket.

  '''

  def __init__(self, main, port, baud, server_ip, sbp_server_port):
    import serial
    threading.Thread.__init__(self)
    self.daemon          = True
    self.main            = main
    self.port            = port
    self.baud            = baud
    self.server_ip       = server_ip
    self.sbp_server_port = sbp_server_port

    self._reader_thread = threading.Thread(target=self._reader, name="Reader")
    self._reader_thread.daemon = True

    self._sendToPiksi   = Queue.Queue()
    self._recvFromPiksi = Queue.Queue()

    try:
      self.handle = serial.Serial(port, baud, timeout=1)
      self._reader_thread.start()
    except (OSError, serial.SerialException):
      logger.error("Serial device '%s' not found" % port)
      logger.error("The following serial devices were detected:")
      import serial.tools.list_ports
      for (name, desc, _) in serial.tools.list_ports.comports():
        if desc[0:4] == "ttyS":
          continue
        if name == desc:
          logger.error("\t%s" % name)
        else:
          logger.error("\t%s (%s)" % (name, desc))
      print
      raise SystemExit

  def _reader(self):
    with BaseDriver(self.handle) as driver:
      with Handler(Framer(driver.read, None, verbose=True)) as source:
        try:
          for msg, metadata in source:
            try:
              self._recvFromPiksi.put(msg.pack(), True, 0.05)
            except Queue.Full:
              logger.warn("_recvFromPiksi Queue is full!")
        except (OSError, serial.SerialException):
          logger.error("Piksi disconnected")
          raise SystemExit          
        except Exception:
          traceback.print_exc()


  # def _reader(self):
  #   import serial
  #   while True:
  #     try:
  #       data = self.handle.read(1)
  #       n = self.handle.inWaiting()
  #       if n:
  #         data = data + self.handle.read(n)
  #       if data:
  #         try:
  #           self._recvFromPiksi.put(data, True, 0.05)
  #         except Queue.Full:
  #           pass # Drop it like it's hot!
  #     except (OSError, serial.SerialException):
  #       print
  #       print "Piksi disconnected"
  #       print
  #       raise SystemExit
  #     except Exception:
  #       #CRUCIAL! This prevents death from exception
  #       traceback.print_exc()
  #       pass

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
      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sbp_udp:
        sbp_udp.setblocking(0)
        sbp_udp.settimeout(0.0)
        self.sbp_udp = sbp_udp

        while True:

          # Uploading data TO Piksi
          try:
            data = self._sendToPiksi.get(False)
            self.handle.write(data)
          except (Queue.Empty, serial.SerialException):
            pass

          # Repeating data FROM Piksi
          try:
            data = self._recvFromPiksi.get(False)
            n = sbp_udp.sendto(data, (self.server_ip, self.sbp_server_port))
            if len(data) != n:
              logger.warn("Piksi->UDP relay, did not send all data!")
            else:
              logger.debug("Piksi->UDP, %s bytes sent" % str(n))
          except (Queue.Empty):
            pass
          except (socket.error, socket.timeout):
            traceback.print_exc()
            pass


    except (OSError, serial.SerialException):
      logger.error("Piksi disconnected")
      raise SystemExit


#====================================================================#    

class OdroidPerson:

  def __init__(self,  config_file, ident):
    self.ident  = ident
    self.dying  = False
    self.config = spooky.Configuration(config_file, ident)
    
    print "ODRIOD launching as '%s'" % ident

    self.bind_ip           = self.config.get_my("my-ip")
    self.server_id         = self.config.get_network("server")
    self.server_ip         = self.config.get_foreign(self.server_id, "my-ip")
    self.cc_local_port     = self.config.get_my("cc-local-port")
    self.cc_server_port    = self.config.get_my("cc-server-port")
    self.sbp_server_port   = self.config.get_my("sbp-server-port")
    self.mav_server_port   = self.config.get_my("mav-server-port")
    
    self.PiksiHandler = PiksiHandler(self, 
      self.config.get_my('sbp-port'), 
      self.config.get_my('sbp-baud'), 
      self.server_ip,
      self.sbp_server_port)
    
    self.sbpBroadcastListenerThread = SBPUDPBroadcastListenerHandlerThread(self, 
      self.PiksiHandler.send_to_piksi, 
      port=self.config.get_my('sbp-udp-bcast-port'))
    
    logger.info("Launching with Config:")
    logger.info(self.config)

  def stop(self):
    logger.info("Shutting down!")
    self.dying = True
    self.sbpBroadcastListenerThread.join(1)
    self.PiksiHandler.join(1)

  def handle_cc(self, cc_data, cc_addr, cc_udp):
    #print "Handling cc from '%s':'%s'" % (cc_addr, cc_data)
    pass

  def mainloop(self):

    self.sbpBroadcastListenerThread.start()
    self.PiksiHandler.start()

    try:
      
      # Here we do UDP command and control
      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
        cc_udp.setblocking(0)
        cc_udp.settimeout(0.0)
        cc_udp.bind((self.bind_ip, self.cc_local_port))
        self.cc_udp = cc_udp

        while True:
          try:

            # '''
            # CC PACKET STRUCTURE:
            # head (32 bits): 0xBEADBEEF
            # len (16 bits): 0xFFFF (length of data)
            # cmd (16 bits): 0xFFFF
            # data (len bits): [...]
            # tail (32 bits): 0xDEADBEEF

            # COMMANDS:
            # 0x0001 - heartbeat
            # '''

            # payload = ''
            # length = len(payload)
            # msg = struct.pack("<IHH", 0xBEADBEEF, length, 0x0001)
            # msg += payload
            # msg += struct.pack("<I", 0xDEADBEEF)
            # cc_udp.sendto(msg, (self.server_ip, self.cc_server_port))
            
            cc_udp.sendto("heartbeat", (self.server_ip, self.cc_server_port))
            cc_data, cc_addr = cc_udp.recvfrom(4096)
            self.handle_cc(cc_data, cc_addr, cc_udp)
          except (socket.error, socket.timeout) as e:
            pass    
          time.sleep(1)

    except KeyboardInterrupt:
      self.stop()

#=====================================================================#

def main():
  try:
    logger.info("OdroidPerson Launching!")

    #All arguments should live in a config file!
    parser = argparse.ArgumentParser(description="Spooky Action at a Distance! Ground Station")
    parser.add_argument("-c", "--config",
                        default=['../config.json'], nargs=1,
                        help="specify the configuration file")
    parser.add_argument("-i", "--ident",
                        default=[''], nargs=1,
                        help="spoof a custom identifier, by default uses IP")
    args = parser.parse_args()

    #Fill out default args
    if args.ident[0] == '':
      args.ident[0] = spooky.ip.get_lan_ip()

    op = OdroidPerson(args.config[0], args.ident[0])
    op.mainloop()

  except socket.gaierror:
    logger.critical("No internet connection")
    return -1

if __name__ == '__main__':
  main()
