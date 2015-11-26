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
from sbp.observation import SBP_MSG_OBS, SBP_MSG_BASE_POS, MsgObs
from sbp.settings import SBP_MSG_SETTINGS_WRITE, MsgSettingsWrite

# This must be run from the src directory, 
# to correctly have all imports relative to src/
import spooky, spooky.ip
from spooky.Daemon import Daemon

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
    self.handle = spooky.BufferedUDPBroadcastSocket(port=bind_port)
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
              print "Received %i" % len(msg.pack())
              self.data_callback(msg.pack())
            except Queue.Full:
              logger.warn("_recvFromPiksi Queue is full!")
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

  def send_disable_sim_to_piksi(self):
    section = "simulator"
    name    = "enabled"
    value   = "False"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
    self.send_to_piksi(msg.to_binary())

  def send_enable_sim_to_piksi(self):
    section = "simulator"
    name    = "enabled"
    value   = "True"
    msg = MsgSettingsWrite(setting='%s\0%s\0%s\0' % (section, name, value))
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
      logger.error("Serial device '%s' not found" % self.port)
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

    try:
      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sbp_udp:
        sbp_udp.setblocking(0)
        sbp_udp.settimeout(0.0)
        self.sbp_udp = sbp_udp

        while True:

          # Uploading data TO Piksi
          try:
            data = self._sendToPiksi.get(True, 0.01)
            self.handle.write(data)
            while not self._sendToPiksi.empty():
              data = self._sendToPiksi.get(False)
              self.handle.write(data)
          except (Queue.Empty, serial.SerialException):
            pass

          # Repeating data FROM Piksi
          try:
            data = self._recvFromPiksi.get(True, 0.05)
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

  def __init__(self,  config, ident):
    self.ident  = ident
    self.dying  = False
    self.config = config
    self.send_id = 0
    
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

  def send_cc(self, msgtype, payload=None):
    try:
      msg = {'msgtype':msgtype}
      if payload is not None:
        msg['payload'] = payload
      msg['__ID__'] = self.send_id
      self.send_id += 1
      #print "sending message %s to %s, %s" % (msgtype, self.server_ip, self.cc_server_port)
      self.cc_udp.sendto(json.dumps(msg), (self.server_ip, self.cc_server_port))
    except socket.error:
      traceback.print_exc()
      raise

  def handle_cc(self, cc_data, cc_addr):
    msg = json.loads(cc_data)

    msg_handler = {
      'ACK':         self.cc_ack,
      'NACK':        self.cc_nack,
      'malformed':   self.cc_unrecognized,
      'unsupported': self.cc_unsupported,

      'simulator':   self.cc_simulator,
      'shutdown':    self.cc_shutdown       
    }

    if not 'msgtype' in msg:
      self.send_cc('malformed', {'msg': 'message contains to \'msgtype\' field.'})
      return

    if not msg['msgtype'] in msg_handler:
      self.send_cc('unsupported', {'msg': 'message type \'%s\' not supported.' % msg['msgtype']})
      return

    #print "Handling message type %s: %s" % (msg['msgtype'], str(msg))
    success = msg_handler[msg['msgtype']](msg)
    if msg['msgtype'] is not 'ACK' and msg['msgtype'] is not 'NACK':
      if success:
        self.send_cc('ACK', {'__ACK_ID__': msg['__ID__']})
      else:
        self.send_cc('NACK', {'__ACK_ID__': msg['__ID__']})


  def cc_ack(self, msg):
    print "ACK RECEIVED for %s" % msg['payload']

  def cc_nack(self, msg):
    print "NACK RECEIVED for %s" % msg['payload']

  def cc_shutdown(self, msg):
    os.system("shutdown now -h")
    return True

  def cc_restart(self, msg):
    os.system("reboot")
    return True

  def cc_simulator(self, msg):
    try:
      payload = msg['payload']
      if payload == 'True':
        print 'ENABLING PIKSI'
        self.PiksiHandler.send_enable_sim_to_piksi()
      else:
        print 'DISABLING PIKSI'
        self.PiksiHandler.send_disable_sim_to_piksi()
        pass
      return True
    except:
      traceback.print_exc()
      return False

  def cc_unrecognized(self, msg):
    pass

  def cc_unsupported(self, msg):
    pass

  def mainloop(self):

    self.sbpBroadcastListenerThread.start()
    self.PiksiHandler.start()

    try:
      
      # Here we do UDP command and control
      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
        cc_udp.setblocking(1)
        cc_udp.settimeout(0.01) # run this at 100hz
        cc_udp.bind((self.bind_ip, self.cc_local_port))
        self.cc_udp = cc_udp

        print "CC bound to %s : %d" % (self.bind_ip, self.cc_local_port)

        heartbeat = spooky.DoEvery(lambda: self.send_cc('heartbeat', payload=os.getuid()), 1.0)
        while True:
          try:
            # For command and control, we're going to use JSON over UDP
            # UDP *already* has a simple checksum and delivers a complete packet at a time.
            # It also returns exactly one datagram per recv() call, so it's all good!
            # Our only requirement is, a cc message consists of at the very least:
            # {'msgtype': 'something', 'payload': {}}
            heartbeat.tick()
            cc_data, cc_addr = cc_udp.recvfrom(4096)
            self.handle_cc(cc_data, cc_addr)
          except (socket.error, socket.timeout) as e:
            pass    

    except KeyboardInterrupt:
      self.stop()

#=====================================================================#

class OdroidPersonDaemon(Daemon):

  def __init__(self, args, config):
    self.args = args
    self.config = config
    Daemon.__init__(self, '/tmp/odroidperson.pid', 
        stdin='/dev/null', 
        stdout='/logs/odroidperson.stdout', 
        stderr='/logs/odroidperson.stderr')

  def run(self):
    config = self.config
    args = self.args
    op = OdroidPerson(config, args.ident[0])
    op.mainloop()

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
    parser.add_argument("-n", "--network",
                        default=['NETWORK'], nargs=1,
                        help="spoof a custom network, by default uses 'NETWORK'")
    parser.add_argument("-d", "--daemon", 
                        default=[''], nargs=1,
                        help="control daemon. use start/stop/restart")
    args = parser.parse_args()

    #Fill out default args
    if args.ident[0] == '':
      args.ident[0] = spooky.ip.get_lan_ip()

    network_ident = args.network[0]
    config = spooky.Configuration(args.config[0], args.ident[0], network_ident)

    daemon = OdroidPersonDaemon(args, config)

    if args.daemon[0] != '':
      if args.daemon[0] == 'start':
        daemon.start()
      elif args.daemon[0] == 'stop':
        daemon.stop()
      elif args.daemon[0] == 'restart':
        daemon.restart()
      else:
        print "usage: %s --daemon start|stop|restart" % sys.argv[0]
    else:
      daemon.run()

  except socket.gaierror:
    logger.critical("No internet connection")
    return -1

if __name__ == '__main__':
  time.sleep(1)
  main()
