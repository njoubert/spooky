# C++ to Python Shim for ToricCam

Built by Niels Joubert

This shim uses SWIG to auto-generate python bindings for the ToricCam library by Christophe Lino.

See [Christophe's Website](https://sites.google.com/site/christophelino/libraries) for details about ToricCam

## USAGE

This builds a **Python Package** in the ```toric/``` subdirectory (aka one level DOWN from this directory)


	python
	>>> import toric
	>>> import toric.samples

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