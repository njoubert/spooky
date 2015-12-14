# Spooky Action at a Distance

WARNING: EXPERIMENTAL AND UNTESTED CODE

A Library and Toolkit for Wireless Distributed State Estimation and Control of Multiple Drones and Subjects. Named after the Quantum Entanglement phenomenon.

This code runs a wireless multi-node sensor networks, powering our wireless cinematography system.
It currently assumes a python-compatible Linux computers at each node. (In our case, ODROID XU4 running Ubuntu and Python 2.7)

## Dependencies and Submodules

**[This project uses git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)**

After checkout:

	git submodule init
	git submodule update

These are the dependencies, and how to install them on a node:

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



## Contents

- `bin/groundstation(-local).sh`: Launch an instance of the grounstation.
- `bin/groundstation(-local).sh`: Launch an instance of the odroidperson.
- `bin/install.sh`: For nodes: Installs "spooky" systemctl daemon to start odroidperson.sh on boot.
- `bin/update-and-restart.sh`: For nodes: Pulls the latest git repo and relaunches daemon.
- `src/groundstation`: Main controller, single instance on your Laptop
- `src/odroidperson`: Multiple Instances, One Per Odroid On Person
- `src/spooky`: Underlying shared library used by both parts

## Archtecture

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

