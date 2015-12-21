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
import spooky, spooky.ip
from spooky import Daemon
from spooky.modules import ModuleHandler

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

class OdroidPerson:

  def __init__(self,  config, ident):
    self.ident  = ident
    self.dying  = False
    self.config = config
    self.send_id = 0
    
    print "ODRIOD launching as '%s'" % ident

    self.modules = ModuleHandler(self, 'odroidperson')

    self.bind_ip           = self.config.get_my("my-ip")
    self.server_id         = self.config.get_network("server")
    self.server_ip         = self.config.get_foreign(self.server_id, "my-ip")
    self.cc_local_port     = self.config.get_my("cc-local-port")
    self.cc_server_port    = self.config.get_my("cc-server-port")
    self.sbp_server_port   = self.config.get_my("sbp-server-port")
    self.sbp_bind_port     = self.config.get_my("sbp-bind-port")
    self.mav_server_port   = self.config.get_my("mav-server-port")
        
    logger.info("Launching with Config:")
    logger.info(self.config)

  def stop(self):
    logger.info("Shutting down!")
    self.dying = True
    self.modules.unload_all_modules()

  def send_cc(self, msgtype, payload=None):
    try:
      msg = {'msgtype':msgtype}
      if payload is not None:
        msg['payload'] = payload
      msg['__ID__'] = self.send_id
      self.send_id += 1
      #print "sending message %s to %s, %s" % (msgtype, self.server_ip, self.cc_server_port)
      self.cc_udp.sendto(json.dumps(msg), (self.server_ip, self.cc_server_port))
    except socket.error as e:
      if e.errno == 65:
        print "SEND_CC: No route to %s:%d" % (self.server_ip, self.cc_server_port)
      else:
        traceback.print_exc()

  def handle_cc(self, cc_data, cc_addr):
    msg = json.loads(cc_data)

    msg_handler = {
      'ACK':         self.cc_ack,
      'NACK':        self.cc_nack,
      'malformed':   self.cc_unrecognized,
      'unsupported': self.cc_unsupported,

      'simulator':   self.cc_simulator,
      'reset_piksi': self.cc_reset_piksi,
      'shutdown':    self.cc_shutdown,
      'restart':     self.cc_restart,
      'update':      self.cc_update,     
    }

    if not 'msgtype' in msg:
      self.send_cc('malformed', {'msg': 'message contains to \'msgtype\' field.'})
      return

    if not msg['msgtype'] in msg_handler:
      self.send_cc('unsupported', {'msg': 'message type \'%s\' not supported.' % msg['msgtype']})
      return

    #print "Handling message type %s: %s" % (msg['msgtype'], str(msg))
    success = msg_handler[msg['msgtype']](msg)
    if not ('ACK' in msg['msgtype'] or 'NACK' in msg['msgtype']):
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
        self.modules.trigger('enable_piksi_sim')
      else:
        print 'DISABLING PIKSI'
        self.modules.trigger('disable_piksi_sim')
        pass
      return True
    except:
      traceback.print_exc()
      return False

  def cc_reset_piksi(self, msg):
    try:
      self.modules.trigger('reset_piksi')
      return True
    except:
      traceback.print_exc()
      return False

  def cc_update(self, msg):
    print "Updating now..."
    os.system("git pull")
    self.send_cc('restarting')
    os.system("systemctl restart spooky.service")

  def cc_unrecognized(self, msg):
    pass

  def cc_unsupported(self, msg):
    pass

  def send_heartbeat(self):
    self.send_cc('heartbeat', payload={'git-describe': spooky.get_version(), 'UID': os.getuid()})

  def mainloop(self):

    if self.config.get_my("be-the-basestation"):
      print "I AM THE BASE STATION"
      self.modules.load_module('SBPUDPBroadcast')
    else:
      print "I AM NOT THE BASE STATION"
      piksi       = self.modules.load_module('piksihandler')
      bcastmodule = self.modules.load_module('sbpbroadcastlistener')
      bcastmodule.set_data_callback(piksi.send_to_piksi)
      pixhawk     = self.modules.load_module('pixhawkhandler')

    try:

      # Here we do UDP command and control
      with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as cc_udp:
        cc_udp.setblocking(1)
        cc_udp.settimeout(0.1) # run this at 10hz
        cc_udp.bind((self.bind_ip, self.cc_local_port))
        self.cc_udp = cc_udp

        print "CC bound to %s : %d" % (self.bind_ip, self.cc_local_port)
            
        heartbeat = spooky.DoPeriodically(lambda: self.send_heartbeat(), 1.0)
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
        time.sleep(5.0)
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
  main()
