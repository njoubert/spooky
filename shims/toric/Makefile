#### PLEASE ENSURE THE FOLLOWING VARIABLES ARE CORRECT FOR YOUR ENVIRONMENT. ####
# ----------------------------------------------------------------------------- #

# SETTINGS
PYTHON_INCLUDE_DIR := /Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/include/python2.7/
PYTHON_LIB_DIR     := /Applications/Canopy.app/appdata/canopy-1.5.1.2730.macosx-x86_64/Canopy.app/Contents/lib/
PYTHON_LIB         := python2.7

#### EVERYTHING BELOW IS CONFIGURATION FOR THIS LIBRARY. ####
# --------------------------------------------------------- #

TORIC_DIR     := ../../lib/ToricCam-1.0.0
TORIC_INCLUDE := -I$(TORIC_DIR)/Include
TORIC_SOURCES := $(wildcard $(TORIC_DIR)/Source/*.cpp)

TORIC_SAMPLES_INCLUDE := $(TORIC_INCLUDE) -I$(TORIC_DIR)/Samples
TORIC_SAMPLES_SOURCES := $(filter-out $(TORIC_DIR)/Samples/main.cpp, $(wildcard $(TORIC_DIR)/Samples/*.cpp))

# INPUTS
SWIG_INTERFACE := toric.i
SWIG_INTERFACE_SAMPLES := toric.samples.i

# OUTPUTS
TARGET := ___init__.so
SWIG_OUTPUT := toric_wrap.cpp
SWIG_MODULE := __init__.py

TARGET_SAMPLES := _samples.so
SWIG_OUTPUT_SAMPLES := toric_samples_wrap.cpp
SWIG_MODULE_SAMPLES := samples.py


# C++ INCLUDES AND LIBS
CXX     := g++
CXXOPTS := -Wall -fPIC -std=c++11
INCLUDE := -I$(PYTHON_INCLUDE_DIR) $(TORIC_SAMPLES_INCLUDE)
LIBS    := -L$(PYTHON_LIB_DIR) -l$(PYTHON_LIB) -dynamiclib

#### EVERYTHING BELOW IS BUILD COMMANDS. ####
# ----------------------------------------- #

.PHONY: all clean
.DEFAULT_GOAL := all


# AUTOGEN
OBJECTS = $(TORIC_SOURCES:.cpp=.o) $(SWIG_OUTPUT:.cpp=.o)
SAMPLES_OBJECTS = $(TORIC_SAMPLES_SOURCES:.cpp=.o) $(SWIG_OUTPUT_SAMPLES:.cpp=.o)

%.o : %.cpp
	$(CXX) $(CXXOPTS) $(INCLUDE) -c -Wall $(CXXFLAGS) $< -o $@

$(SWIG_OUTPUT): $(SWIG_INTERFACE)
	@echo "***"
	@echo "*** Generating Python and C++ Wrappers for SOURCE"
	@echo "***"
	swig -Wall -c++ -python $(TORIC_INCLUDE) -o $(SWIG_OUTPUT) $(SWIG_INTERFACE)
	@echo "***"
	@echo "*** DONE"
	@echo "***"
	
$(SWIG_OUTPUT_SAMPLES): $(SWIG_SAMPLES_INTERFACE)
	@echo "***"
	@echo "*** Generating Python and C++ Wrappers for SAMPLES"
	@echo "***"
	swig -Wall -c++ -python $(TORIC_SAMPLES_INCLUDE) -o $(SWIG_OUTPUT_SAMPLES) $(SWIG_INTERFACE_SAMPLES)
	@echo "***"
	@echo "*** DONE"
	@echo "***"


$(TARGET): $(SWIG_OUTPUT) $(TORIC_SOURCES) $(OBJECTS)
	@echo "***"
	@echo "*** Linking SOURCE"
	@echo "***"
	$(CXX) $(LIBS) $(OBJECTS) -o $(TARGET)

$(TARGET_SAMPLES): $(SWIG_OUTPUT_SAMPLES) $(TORIC_SAMPLES_SOURCES) $(OBJECTS) $(SAMPLES_OBJECTS)
	@echo "***"
	@echo "*** Linking SAMPLES"
	@echo "***"
	$(CXX) $(LIBS) $(OBJECTS) $(SAMPLES_OBJECTS) -o $(TARGET_SAMPLES)

all: $(TARGET) $(TARGET_SAMPLES)

clean:
	rm -f $(OBJECTS) $(SAMPLES_OBJECTS) $(SWIG_OUTPUT) $(SWIG_OUTPUT_SAMPLES) $(SWIG_MODULE) $(SWIG_MODULE_SAMPLES) *.o *.so *.pyc
