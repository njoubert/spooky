TARGET := main
SOURCES := $(wildcard ./Source/*.cpp) Samples/main.cpp

#Necessary declarations follow:
INCLUDE := -I./Include
LIBRARY := 
FRAMEWORK :=
MACROS :=
PLATFORM :=
LDFLAGS :=
CXXFLAGS :=


CC := gcc
CXX := g++
MACROS += 
CXXFLAGS += -Wall -O2 -fmessage-length=0 -std=c++11 $(INCLUDE) $(MACROS)
LDFLAGS += $(FRAMEWORK) $(LIBRARY) $(MACROS)

%.o : %.cpp
	@echo "Compiling .cpp to .o for $(PLATFORM) Platform: $< " 
	$(CXX) -c -Wall $(CXXFLAGS) $< -o $@

OBJECTS = $(SOURCES:.cpp=.o)

$(TARGET): $(OBJECTS)
	$(CXX) $(LDFLAGS) $(OBJECTS) -o $(TARGET)

clean:
	@echo "Removing compiled files."
	/bin/rm -f $(OBJECTS) $(TARGET) $(TESTOBJECTS) $(TESTTARGETS) 