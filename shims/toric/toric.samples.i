// toric.samples.i - SWIG interface for ToricCam Samples

%module samples

// See http://www.swig.org/Doc1.3/Modules.html
%import "toric.i"

%{

#include "TargetOOBB.h"
#include "TargetOOBS.h"
#include "TwoTargets.h"
#include "SingleTarget.h"

using namespace toric::samples;

%}

%include "TargetOOBB.h"
%include "TargetOOBS.h"
%include "TwoTargets.h"
%include "SingleTarget.h"