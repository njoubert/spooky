# Spooky Action at a Distance

WARNING: EXPERIMENTAL AND UNTESTED CODE AHEAD

Code for our wireless cinematography data system

## Contents

- "GroundStation" Single Instance on your Laptop
- "OdroidPerson" Multiple Instances, One Per Odroid On Person

## Current Architecture:

- Odroid launches, sends heartbeats to Ground Station. 
- Ground Station holds list of Odroids in MultiCast object. Whenever a heartbeat arrives, it gets added to this list.
- Ground Station sends SBP data to the entire list of Multicast recipients.

## TODO:


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

## IDEAS ON ARCHITECTURE:

UNIX-style many-small-applications versus single monolothic app?

- PRO: If something crashes, we can just restart that section
- PRO: Good way to think about problems!
- CON: I'll have to fire up and run a whole bunch of applications, cumbersome

Can we do UNIX-style, but wrapped behind a single UI the way MAVProxy does it?

- PRO: Can still restart individual chunks, etc
- CON: Have to do all that management myself.

Let's try to do that!


## OTHER RESOURCES 

I am not using, but am curious about:

- [Twisted](https://twistedmatrix.com/trac/), "an event-driven networking engine written in Python"
- NodeJS, why why why didn't I do this in NodeJS??? Sigh, all the UAV libraries are in python...