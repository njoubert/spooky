# Spooky Action at a Distance

WARNING: EXPERIMENTAL AND UNTESTED CODE

A Library and Toolkit for Wireless Distributed State Estimation and Control of Multiple Drones and Subjects. Named after the Quantum Entanglement phenomenon.

This code runs a wireless multi-node sensor networks, powering our wireless cinematography system.
It currently assumes a python-compatible Linux computers at each node. (In our case, ODROID XU4 running Ubuntu and Python 2.7)

## TL;DR: Replay a Log!

What a great place to start!

	./bin/replay logs/state0000356.pickle

Now, use your favorite port monitoring tool, or just run mine! In a different window:

	python experiments/simple_udp_listener --port 19001

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

## Contents

- `bin/groundstation(-local).sh`: Launch an instance of the grounstation.
- `bin/groundstation(-local).sh`: Launch an instance of the odroidperson.
- `bin/install.sh`: For nodes: Installs "spooky" systemctl daemon to start odroidperson.sh on boot.
- `bin/update-and-restart.sh`: For nodes: Pulls the latest git repo and relaunches daemon.
- `src/groundstation`: Main controller, single instance on your Laptop
- `src/odroidperson`: Multiple Instances, One Per Odroid On Person
- `src/spooky`: Underlying shared library used by both parts

## Architecture

We do a UNIX-style "many-independent-small-applications" approach, but wrapped behind a single python CLI (similar to MAVProxy)

- PRO: If something crashes, we can just restart that section
- PRO: Good way to think about problems!
- PRO: Can still restart individual chunks, etc
- CON: Have to do all that management myself.

Components are engineered to depend on as few other parts of the system as possible. Different components can be rebooted on-the-fly without crashing anything.

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

### Firing up Solo Simulator

First, [set up Virtualbox and Vagrant](http://python.dronekit.io/guide/sitl_setup.html)

Then, to fire up the simulator:

	vagrant up
	vagrant ssh
	./sitl.sh
	param load ../Tools/autotest/copter_params.parm
	param set ARMING_CHECK 0

This will start transmitting data on `0.0.0.0:14550`

## Integrating with the Swift Binary Protocol

[The documentation and protocol spec lives here.](http://docs.swift-nav.com/wiki/SBP)

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

