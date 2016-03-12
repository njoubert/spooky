#### PLEASE ENSURE THE FOLLOWING VARIABLES ARE CORRECT FOR YOUR ENVIRONMENT. ####
# ----------------------------------------------------------------------------- #

# SETTINGS
PYTHON_INCLUDE_DIR := /Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/include/python2.7/
PYTHON_LIB_DIR     := /Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/lib/
PYTHON_LIB         := python2.7

#### EVERYTHING BELOW IS CONFIGURATION FOR THIS LIBRARY. ####
# --------------------------------------------------------- #

TORIC_DIR     := ../../lib/ToricCam-1.0.0
TORIC_INCLUDE := $(TORIC_DIR)/Include
TORIC_SOURCES := $(wildcard $(TORIC_DIR)/Source/*.cpp)

# INPUTS
SOURCES := $(TORIC_SOURCES)
SWIG_INTERFACE := toric.i

# OUTPUTS
TARGET := _toric.so
SWIG_OUTPUT := toric_wrap.cpp
SWIG_MODULE := toric.py

# C++ INCLUDES AND LIBS
CXX     := g++
CXXOPTS := -Wall -fPIC -std=c++11
INCLUDE := -I$(PYTHON_INCLUDE_DIR) -I$(TORIC_INCLUDE)
LIBS    := -L$(PYTHON_LIB_DIR) -l$(PYTHON_LIB) -dynamiclib

#### EVERYTHING BELOW IS BUILD COMMANDS. ####
# ----------------------------------------- #

.PHONY: all clean
.DEFAULT_GOAL := $(TARGET)


# AUTOGEN
OBJECTS = $(SOURCES:.cpp=.o) $(SWIG_OUTPUT:.cpp=.o)

$(SWIG_OUTPUT):
	@echo "***"
	@echo "*** Generating Python and C++ Wrappers"
	@echo "***"
	swig -Wall -c++ -python -I$(TORIC_INCLUDE) -o $(SWIG_OUTPUT) $(SWIG_INTERFACE)
	@echo "***"
	@echo "*** DONE"
	@echo "***"
	
%.o : %.cpp
	$(CXX) $(CXXOPTS) $(INCLUDE) -c -Wall $(CXXFLAGS) $< -o $@

$(TARGET): $(SWIG_OUTPUT) $(OBJECTS)
	@echo "***"
	@echo "*** Linking"
	@echo "***"
	$(CXX) $(LIBS) $(OBJECTS) -o $(TARGET)

all: $(TARGET)

clean:
	rm -f $(OBJECTS) $(SWIG_OUTPUT) $(SWIG_MODULE) *.o *.so




# TARGET := main
# SOURCES := $(wildcard ./Source/*.cpp) Samples/main.cpp

# #Necessary declarations follow:
# INCLUDE := -I./Include
# LIBRARY := 
# FRAMEWORK :=
# MACROS :=
# PLATFORM :=
# LDFLAGS :=
# CXXFLAGS :=


# CC := gcc
# CXX := g++
# MACROS += 
# CXXFLAGS += -Wall -O2 -fmessage-length=0 -std=c++11 $(INCLUDE) $(MACROS)
# LDFLAGS += $(FRAMEWORK) $(LIBRARY) $(MACROS)

# %.o : %.cpp
# 	@echo "Compiling .cpp to .o for $(PLATFORM) Platform: $< " 
# 	$(CXX) -c -Wall $(CXXFLAGS) $< -o $@

# OBJECTS = $(SOURCES:.cpp=.o)

# $(TARGET): $(OBJECTS)
# 	$(CXX) $(LDFLAGS) $(OBJECTS) -o $(TARGET)

# clean:
# 	@echo "Removing compiled files."
# 	/bin/rm -f $(OBJECTS) $(TARGET) $(TESTOBJECTS) $(TESTTARGETS) 

