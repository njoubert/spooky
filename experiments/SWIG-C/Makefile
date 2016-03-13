
# INPUTS
SOURCES := example.c
SWIG_INTERFACE := example.i

# OUTPUTS
TARGET := _example.so
SWIG_OUTPUT := example_wrap.c


# SETTINGS
INCLUDE := -I/Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/include/python2.7/
LIBS    := -L/Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/lib/ -lpython2.7 -dynamiclib

# AUTOGEN
OBJECTS = $(SOURCES:.c=.o) example_wrap.o

all:
	swig -python $(SWIG_INTERFACE)
	gcc -c $(SOURCES) $(SWIG_OUTPUT) $(INCLUDE) 
	gcc $(LIBS) $(OBJECTS) -o $(TARGET)
