
'''

'''

device = '/dev/tty.usbmodem1'
streamrate = 15

from pymavlink import mavutil
import sys

# create a mavlink serial instance
master = mavutil.mavlink_connection(device)

print("waiting for heartbeat")
master.wait_heartbeat()
print("Heartbeat from APM (system %u component %u)" % (master.target_system, master.target_system))


print("Sending all stream request for rate %u" % streamrate)
for i in range(0, 3):
  print "Sending..."
  master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, streamrate, 1)

print("Receiving messages")
while True:
    msg = master.recv_match(type='ATTITUDE', blocking=True)
    if not msg:
        break
    if msg.get_type() == "BAD_DATA":
        if mavutil.all_printable(msg.data):
            sys.stdout.write(msg.data)
            sys.stdout.flush()
    else:
        print(msg)