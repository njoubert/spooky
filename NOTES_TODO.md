# Tuesday February 23rd

0) Set up base station. DO NOT MOVE once it’s powered on, and power cycle if you move it!

1) Set up and power on all hardware
base-survey-status: "Survey done. 37.43098611, -122.17310206, 12.44307 (601/600)", UID: "0"

[FIXED] 2) SSH into each odroid, run sudo systemctl restart spooky

3) Connect groundstation laptop to network, 192.168.2.1, and to SoloLink, 10.1.1.100
4) Open groundstation on laptop, confirm that CC, SBP and MAV are receiving packets for each user
— mav isnt receiving on 51. WTF. Reboot
—— auto-reload stuck modules, or remote-reload stuck modules
5) Run mavproxy to connect to drone: mavproxy.py --master=0.0.0.0:14550 --out=192.168.2.1:14551 --out=192.168.2.1:14552

6) Start up piksi consoles to check:
cd ~/Code/THIRD_PARTY/swift-nav/piksi_tools/
python piksi_tools/console/console.py -p 192.168.2.1:19214

7) Start up solo SBP pump ./bin/solo_sbo_pump
8) groundstation solo connect: solo connect

8) Start up piksi consoles to check
python piksi_tools/console/console.py -p 192.168.2.1:18002



- HOW DOES PIKSI HOME GET SET? REVERT TO ORIGINAL SETTINGS!

- IS UNALIGNED OBS (cause base is running at a higher rate) OK?

- RECORDING DATA? GOTTA BE ABLE TO SPLIT FILES / HAVE MARKERS

Notice Alt: 0.5 to 1.0 meters too high?



# WEBNESDAY March 2

- SBP Injection over MAVLink is really splotchy. Switch to over-UDP.

- Piksi solo relay dies??
--- looks like main.py on solo crashes

- POWER is a MUST


state0000907 is just walking (no flying)

- Needs 3D Fix with Piksi having 7 sats. (1:02pm) (1:08pm reboot)

