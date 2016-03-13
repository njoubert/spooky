# C++ to Python Shim for ToricCam

Built by Niels Joubert

This shim uses SWIG to auto-generate python bindings for the ToricCam library by Christophe Lino.

See [Christophe's Website](https://sites.google.com/site/christophelino/libraries) for details about ToricCam

## USAGE

This builds a **Python Package** in the ```toric/``` subdirectory (aka one level DOWN from this directory)


	python
	>>> import toric
	>>> import toric.samples

You must copy this **ENTIRE** directory (including the shared object files) to wherever you want to use it, or include the *current* directory in your python path as follows:

	$PYTHONPATH=<PATH_TO_SPOOKY>/shims/toric:$PYTHONPATH

### Accessing Static Methods in Python

Note that Python does not have an equivalent to Static Member Functions in C++. Swig autogenerates this to module-level functions by concantenating the Class and Function name.

So, for exampe, in C++

	Toric3::FromWorldPosition()

becomes

	Toric3_FromWorldPosition()

## RUN A TEST

Included is a simple test that the library is working

	python toric_test.py

## Build Instructions for Mac OS X


### Dependencies

Building this shim requires SWIG

	brew install swig

### Building Shim

Please edit the top section of ```Makefile``` to ensure platform compatibility.

run ```make```

## List of bugs found in Toric:

Quaternion.h defines ```normalise()``` but this is not implemented anywhere.

Toric.h defines ```Vector3 computePosition(const Toric2 & t) const;``` but this is not implemented anywhere