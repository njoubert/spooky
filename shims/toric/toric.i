// toric.i - SWIG interface for ToricCam

%module toric
%{

#include "toric/Camera.h"
#include "toric/Euler.h"
#include "toric/Matrix.h"
#include "toric/ProjectionMatrix.h"
#include "toric/Quaternion.h"
#include "toric/Toric.h"
#include "toric/Vector.h"

using namespace toric;

%}

%include "toric/Camera.h"
%include "toric/Euler.h"
%include "toric/Matrix.h"
%include "toric/ProjectionMatrix.h"
%include "toric/Quaternion.h"
%include "toric/Toric.h"
%include "toric/Vector.h"
