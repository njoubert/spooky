# Spooky Action at a Distance

*EXPERIMENTAL AND UNTESTED CODE RESEARCH CODE! THAR BE DRAGONS AHEAD LADDY!*

A Library and Toolkit for Wireless Distributed State Estimation and Control of Multiple Drones and Subjects. Named after the Quantum Entanglement phenomenon.

This code runs a wireless multi-node sensor networks, powering our wireless cinematography system.
It currently assumes a python-compatible Linux computers at each node. (In our case, ODROID XU4 running Ubuntu and Python 2.7)

## Before we start

The tools does not make the master. A master chooses great tools for his craft. I am far from full mastery, but at this stage of my journey, here's the tools I choose for my craft:

- Macbook Pro, OS X 10.10 Yosemite
- [Git](https://git-scm.com/) and [Github](http://www.github.com/njoubert)
	- [SourceTree](https://www.sourcetreeapp.com/) for visualizing Git repositories.
- Markdown for documentation 
- Sublime Text 3
	- [Material theme](https://equinusocio.github.io/material-theme/)
	- [GitGutter](https://github.com/jisaacks/GitGutter)
	- [Full usage of keyboard and mouse shortcuts](https://gist.github.com/4062168)
- BASH
	 - [with git configuration](https://github.com/njoubert/spooky/blob/master/bash_profile)
- [Dropbox](www.dropbox.com) stores *all* my files.
- [Divvy](http://mizage.com/divvy/), with reasonable keyboard shortcuts to push windows around.
- [Quicksilver](https://qsapp.com/) app launcher
- [Caffeine](http://lightheadsw.com/caffeine/) for power control
- [f.lux](https://justgetflux.com/) for nighttime coding

## Contents

### bin/

- `groundstation(-local).sh`: Launch an instance of the grounstation.
- `groundstation(-local).sh`: Launch an instance of the odroidperson.
- `install.sh`: For nodes: Installs "spooky" systemctl daemon to start odroidperson.sh on boot.
- `update-and-restart.sh`: For nodes: Pulls the latest git repo and relaunches daemon.

### src/

- `groundstation`: Main controller, single instance on your Laptop
- `odroidperson`: Multiple Instances, One Per Odroid On Person
- `replay`: Script to replay recorded data, as if live sensors are playing
- `piksibase`: Helper executable, if you want to run only a ONLY a piksi SBP Broadcaster 
- `spooky`: Underlying shared library used by both parts

## TL;DR: Replay a Log!

What a great place to start! **[See all the available logfiles here!](https://github.com/njoubert/spooky/blob/master/logs/README.md)**

	./bin/replay logs/state0000356.pickle

Now, use your favorite port monitoring tool, or just run mine! In a different window:

	python experiments/simple_udp_listener.py --port 19001

**Check out `./bin/replay --help` for more commands!**

## TL;DR: Running

Fire up a local debug odroidperson instance:

	./bin/odroidperson-local.sh

Fire up a local groundstation instance:

	./bin/groundstation-local.sh

Fire up a UDP listener to check your output:

	python experiments/simple_udp_listener.py --port 19000

Start playing with the CLI from `groundstation`:

	>>> help
	>>> status
	
**Alt Compensation**

We include a manual altitude compensation / calibration routine:

	solo up <mm>
	solo set_alt_comp <mm>


## Dependencies and Submodules

**[This project uses git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)**

After checkout:

	git submodule init
	git submodule update

These are the dependencies, and how to install them:

- libsbp https://github.com/swift-nav/libsbp

	```
	git clone https://github.com/swift-nav/libsbp
	cd libsbp
	sudo python setup.py install
	```

- pymavlink https://github.com/mavlink/mavlink

	```
	sudo apt-get install python-dev
	git clone https://github.com/mavlink/mavlink
	cd mavlink/pymavlink
	sudo python setup.py install
	```

- dronekit https://github.com/dronekit/dronekit-python

	```
	sudo pip install dronekit
	```


## Integration with Piksi Console:

The Ground Station relays messages from Piksi Console to each individual Piksi in the field.

Point Piksi Console to **listen** for SBP messages on:

	<GroundStation IP>:<sbp-relay-send-port> 

Piksi Console can **send** SBP messages to:

	<GroundStation IP>:<sbp-relay-recv-port>

## Integrating with the Swift Binary Protocol

[The documentation and protocol spec lives here.](http://docs.swift-nav.com/wiki/SBP)


## Integration with 3DR Solo:

Solo creates a wireless network. The controller, Solo, and any connected devices are on the same network subnet. The network layout is:

	10.1.1.1    - Controller
	10.1.1.10   - Solo
	10.1.1.100+ - Connected Devices

Connect to your solo's wifi: `SSID = SoloLink_XXX` and `password = sololink`.

Ping your device:

	ping -c 3 10.1.1.1
	ping -c 3 10.1.1.10

Install [solo cli](https://github.com/3drobotics/solo-cli) and check out [docs](http://dev.3dr.com/starting-utils.html):

	pip install -UI git+https://github.com/3drobotics/solo-cli

Update and provision Solo:

	solo flash both latest --clean
	solo wifi --name="wifi ssid" --password="wifi password"
	solo resize
	<restart by hand>
	solo resize
	solo info	
	solo provision

Get started with [dronekit from the ground station](http://python.dronekit.io/guide/getting_started.html):

	sudo pip install dronekit

Attempt to connect from your laptop in `python`:

```
from dronekit import connect
vehicle = connect('0.0.0.0:14550', wait_ready=True)
print "Vehicle state:"
print " Global Location: %s" % vehicle.location.global_frame
print " Global Location (relative altitude): %s" % vehicle.location.global_relative_frame
print " Local Location: %s" % vehicle.location.local_frame
print " Attitude: %s" % vehicle.attitude
print " Velocity: %s" % vehicle.velocity
print " Battery: %s" % vehicle.battery
print " Last Heartbeat: %s" % vehicle.last_heartbeat
print " Heading: %s" % vehicle.heading
print " Groundspeed: %s" % vehicle.groundspeed
print " Airspeed: %s" % vehicle.airspeed
print " Mode: %s" % vehicle.mode.name
print " Is Armable?: %s" % vehicle.is_armable
print " Armed: %s" % vehicle.armed
```

or

```
from pymavlink import mavutil
c = mavutil.mavlink_connection("10.1.1.10:14550")
```

Check out all the [sweet examples!](https://github.com/dronekit/dronekit-python/tree/master/examples)

### Integrating Piksi with 3DR Solo's PIXHAWK Driver

This section of the Piksi integration enables Solo to fly using RTK and Piksi in Pseudo-Absolute mode.

This assumes you're using the [3DR Accessory Port](http://dev.3dr.com/hardware-accessorybay.html)

We're going to set up ```SERIAL2``` (uartD) as ```GPS1```, and ```SERIAL3``` (uart?) as ```GPS2```. ```SERIAL2``` is on the Accessory Port, so we will plumb this to Piksi. ```SERIAL3``` is wired to the internal ublox GPS, so we will leave that as is. uartE aka ```SERIAL4``` is wired to the Gimbal.

Here's the mapping of serial ports on Pixhawk(2):

| HAL         | System       | Params  | Pixhawk | Solo         |
|-------------|--------------|---------|---------|--------------|
| px4io/sbus? | /dev/ttyS0   |         |         |              |
| uartA       | /dev/ttyACM0 |         | USB     |              |
| uartB       | /dev/ttyS3   | SERIAL3 | GPS     | Internal GPS |
| uartC       | /dev/ttyS1   | SERIAL1 | Telem1  |              |
| uartD       | /dev/ttyS2   | SERIAL2 | Telem2  | Acc. Port    |
| uartE       | /dev/ttyS6   | SERIAL4 | Serial4 | Gimbal       |
| nsh console | /dev/ttyS5   |         | Serial5 | Acc. Port    |

**Setup Piksi:**

Choose which UART will connect to Solo. I used UARTA for it's position. Configure the following Piksi settings. Make sure you're producing solutions at 5Hz, not the default 10Hz! 

| Section      | Setting                  | Value  |
|--------------|--------------------------|--------|
| UART A       | mode                     | SBP    |
| UART A       | sbp message mask         | 65280  |
| UART A       | conigure telemetry radio | False  |
| UART A       | baudrate                 | 115200 |
| Solution     | soln freq                | 5      |

Also set up a surveyed base station. The PIXHAWK driver requires pseudo-absolute positioning (```POS_LLH``` messages with a flag indicating RTK lock). This can only be generated if the base station also transmits a ```BASE_POS``` message containing a surveyed location.

| Section | Setting                  | Value        |
|---------|--------------------------|--------------|
|         | surveyed lat             | *measure it* |
|         | surveyed lon             | *measure it* |
|         | surveyed alt             | *measure it* |

On the base station, ensure that the OBS messages are small enough to fit into MAVLink:

| Section | Setting                  | Value  |
|---------|--------------------------|--------|
| SBP     | obs msg max size         | 102    |

Connect Piksi to the Accessory Port as follows:

| Piksi | Accessory Port |
|-------|----------------|
| GND   | GND     |
| RX    | SER2_TX |
| TX    | SER2_RX |
| VCC   | ?       |
	

**Setup Pixhawk**

Connect to the solo using mavproxy:
	
	mavproxy.py --master udp:0.0.0.0:14550

Now, set up the necessary parameters:

	param set GPS_TYPE 1
	param set GPS_TYPE2 1
	param set SERIAL2_BAUD 115
	param set SERIAL2_PROTOCOL 5
	param set SERIAL3_BAUD 38
	param set SERIAL3_PROTOCOL 5
	param set EKF_POSNE_NOISE 0.1
	
To enable GPS Altitude, set the following params. (Thanks to Paul Riseborough for this!)
This enables the secondary EKF, and runs multiple instances for redundancy.

	param set EK2_ENABLE  1
	param set EKF_ENABLE  0
	param set AHRS_EKF_TYPE  2
	param set EK2_IMU_MASK  3


Turn on the Piksi's simulation mode, and in mavproxy, run:

	status

You should see:

	GPS_RAW_INT {time_usec : 642108000, fix_type : 5, lat : 374292190, lon : -1221738005, alt : 69740, eph : 160, epv : 65535, vel : 396, cog : 12748, satellites_visible : 9}
	GPS2_RAW {time_usec : 0, fix_type : 1, lat : 373625480, lon : -1221125932, alt : -208190, eph : 9999, epv : 65535, vel : 0, cog : 0, satellites_visible : 0, dgps_numch : 0, dgps_age : 0}

### Creating a SBP Relay from Solo to the Ground Station

This section demonstrates how to create a bi-directional relay of SBP data from Piksi, via sololink to your ground staton.

**Setup iMX6**

[Follow these directions](http://dev.3dr.com/starting-utils.html) to setup libsbp on Python. Mirrored here:

	pip install -UI git+https://github.com/3drobotics/solo-cli
	solo wifi --name=<ssid> --password=<password>
	solo install-smart
	solo install-runit
	solo install-pip
	solo resize

**Download Logs**

Do this periodically

	cd spooky/logs
	solo logs download

**Connect the Piksi USB to the Solo USB**

See [this discussion.](https://discuss.dronekit.io/t/peripherals-mapping-between-accessory-port-pixhawk2-and-arducopter-parameters-to-connect-secondary-rtk-gps/198/3)

Use an OTG USB cable, such as [this](https://store.3drobotics.com/products/micro-usb-cable-2) or [this](http://www.amazon.com/Micro-USB-OTG-Adapter-Cable/dp/B00D8YZ2SA) one. Connect the host side (blue) to the iMX6 (that is, solo).

Put the iMX6 USB into host mode. By default it exposes a serial port. Use or make a jumper and connect ```GND``` to ```3DRID```. 

SSH into solo, and check that Piksi is available on Solo:

	ssh 10.1.1.10
	cd /dev/serial/by-id
	ls -lah

and you should see something like

	drwxr-xr-x    2 root     root          60 Jan  2 09:05 ./
	drwxr-xr-x    4 root     root          80 Jan  1  1970 ../	
	lrwxrwxrwx    1 root     root          13 Jan  1  1970 usb-FTDI_Single_RS232-HS-if00-port0 -> ../../ttyUSB0

Notice the FTDI driver - that's Piksi!

**Install libsbp**

Time to get busy! Install [libsbp](https://swift-nav.github.io/libsbp/) on Solo and check out the [libsbp docs](https://swift-nav.github.io/libsbp/python/docs/build/html/):

	ssh 10.1.1.10
	pip install sbp
	mkdir /home/root/Code

**Install solo sbp relay**

Copy the ```src/solo/main.py``` file to your solo:

	rsync -avz src/solo/main.py root@10.1.1.10:/home/root/Code

Create a service to auto-start ```main.py```. Copy-paste this into the shell:

	mkdir -p /etc/solo-services/spooky/
	cat <<'EOF' | tee /etc/solo-services/spooky/run
	#!/bin/bash
	cd /home/root/Code && exec python main.py
	EOF
	chmod +x /etc/solo-services/spooky/run


### Firing up Solo Simulator

First, [set up Virtualbox and Vagrant](http://python.dronekit.io/guide/sitl_setup.html)

Then, to fire up the simulator:

	vagrant up
	vagrant ssh
	./sitl.sh
	param load ../Tools/autotest/copter_params.parm
	param set ARMING_CHECK 0

This will start transmitting data on `0.0.0.0:14550`

## Configuring ODROID-XU4

The Odroid XU-4 is (as of end-2015) the most popular companion computer for sUAS research [source: Niels' Urban Dictionary]. It comes equipped with a suite of features that makes it amazingly well-suited for high performace computing on a flying platform: an eight-core processor (Arm A15 and A9 processors), USB3.0, and GPIO pins.

### Flashing

Flash Odroids with [Ubuntu 15.04 image](http://odroid.com/dokuwiki/doku.php?id=en:xu3_release_linux_ubuntu) onto MicroSD card using [these instructions](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)

### Initial ODROID Configuration and Installation

I'm assuming you've got your ODROID plugged into an HDMI screen, mouse and keyboard. You just booted and you're staring at an Ubuntu desktop.

- Connect your odroid to a wired internet connection
- Double-click "ODROID Utility" on the desktop, and enter the SU password 'odroid' (things install...)
- Resize the root partition
- Set a better hostname
- reboot!

Now it's time to install things for us:

	sudo apt-get install python-setuptools python-pip
	mkdir ~/Code
	cd Code
	git clone https://github.com/njoubert/spooky.git
	cd spooky
	git submodule init
	git submodule update
	
From here on, look to the rest of this document :)

### Configure Static IP

**GUI Way:**

Open System -> Preferences -> Network Connections


## SSHing in:

	username: odroid
	password: odroid

### Resizing the root partition:

Use the supplied odroid-utility

	sudo odroid-utility.sh

## Architecture

We do a UNIX-style "many-independent-small-applications" approach, but wrapped behind a single python CLI (similar to MAVProxy)

- PRO: If something crashes, we can just restart that section
- PRO: Good way to think about problems!
- PRO: Can still restart individual chunks, etc
- CON: Have to do all that management myself.

Components are engineered to depend on as few other parts of the system as possible. Different components can be rebooted on-the-fly without crashing anything.


## Using PyFTDI:

https://pylibftdi.readthedocs.org/en/latest/troubleshooting.html

	sudo kextunload -bundle-id com.apple.driver.AppleUSBFTDI

## OTHER RESOURCES 

I am not using, but am curious about:

- [Twisted](https://twistedmatrix.com/trac/), "an event-driven networking engine written in Python"
- NodeJS, why why why didn't I do this in NodeJS??? Sigh, all the UAV libraries are in python...



# DEAD KITTENS




### TODO:


Required Features:
- Piksi Obs, GS to Person (One To Many)
	- GS: Initially, just build a UDP forwarder
		- Read Obs message from ground station Piksi
		- Send Obs message over UDP to destination UDP port
			- Try out Broadcast, Try out List, Try out having remote dynamically register with us.
	- OD: Initially, UDP to Piksi bridge
		- Listen for UDP packet on specific port
		- Relay packet from UDP to Piksi
- Piksi Location, Person to GS (Many To One)
- Pixhawk Data, Person to GS (Just build a MAVLink Repeater)
	- "Arms" Pixhawk or whatever is necessary to get correct data 


- GS: Listen to Heartbeats for all odroids
- GS: Using "select" to handle multiple requests in single thread
- OD: Startup script to launch python.
- OD: Startup script to relaunch python if crashes.
- OD: Main Python script "scheduler":
	- OD: Main thread just sends heartbeat packets to GS
	- OD: Secondary thread does all the work. In case of death, main error sends data 
- System: Provisioning script, logs into odroids and sets up with latest code.


- Start using “with” everywhere, open the socket inside run()
- Make sure we’re closing sockets when we destroy thread
- 

Q1: How do we structure modules with many threads so they cleanly shut down? currently odroidperson module is ugly and leaves orphaned threads.
[DONE] - Each thread is its own module!

Q2: How do we inject modules into one another, so odroidthread has the state vector thread?
— can’t do it “statically” or “during runtime init” since we might reload that module.
— can have it call to main every time.
— can have adapter object that process everything for you
[WE DID THIS] — alternatively, do a message-passing style where you inject a message into the message layer, and a different module registers to listen for that.

TODO:
[DONE] - split odroidperson into a module for each currently logical thread
[DONE] - have the state space register itself with main, and have all the odroidperson threads send updates to state space through main (so an indirect reference can be replaced)


## Stuff

- [Behind Gates Lawn](https://www.google.com/maps/@37.430614,-122.1720352,17.57z)
- [Clark Center Lawn](https://www.google.com/maps/@37.4309214,-122.1750064,556a,20y,13.38h/data=!3m1!1e3)
- [Stanford IM Fields](https://www.google.com/maps/@37.4303889,-122.1570218,696m/data=!3m1!1e3)
- [Sunnyvale Baylands](https://www.google.com/maps/@37.4113185,-121.9979602,612m/data=!3m1!1e3)
- [Russian Ridge](https://www.google.com/maps/@37.290743,-122.1882513,2571a,20y,353.95h,53.05t/data=!3m1!1e3)
- [Rancho San Antonio Flying Field](https://www.google.com/maps/@37.3320445,-122.0854063,341a,20y,74.55h/data=!3m1!1e3)
- [Montebello Open Space](https://www.google.com/maps/place/Montebello+Open+Space+Preserve+Parking+Lot/@37.3266989,-122.1794326,2052a,20y,23.89h/data=!3m1!1e3!4m2!3m1!1s0x0000000000000000:0x71b110aa96b5b016!6m1!1e1)
