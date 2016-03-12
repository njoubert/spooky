
# INPUTS
SOURCES := $(wildcard *.cpp)
SWIG_INTERFACE := mymodule.i

# OUTPUTS
TARGET := _mymodule.so
SWIG_OUTPUT := mymodule_wrap.cpp
SWIG_MODULE := mymodule.py

# SETTINGS
INCLUDE := -I/Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/include/python2.7/
LIBS    := -L/Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/lib/ -lpython2.7 -dynamiclib

# AUTOGEN
OBJECTS = $(SOURCES:.cpp=.o)

all:
	swig -Wall -c++ -python -o $(SWIG_OUTPUT) $(SWIG_INTERFACE)
	g++ -fPIC -c $(SOURCES) $(SWIG_OUTPUT) $(INCLUDE) 
	g++ $(LIBS) $(OBJECTS) -o $(TARGET)

clean:
	rm -f $(OBJECTS) $(SWIG_OUTPUT) $(SWIG_MODULE)