// toric.i - SWIG interface for ToricCam Source

%module __init__
%{

#include "toric/Camera.h"
#include "toric/Euler.h"
#include "toric/Matrix.h"
#include "toric/ProjectionMatrix.h"
#include "toric/Quaternion.h"
#include "toric/Vector.h"
#include "toric/Toric.h"

using namespace toric;

%}

%include "toric/Camera.h"
%include "toric/Euler.h"
%include "toric/Matrix.h"
%include "toric/ProjectionMatrix.h"
%include "toric/Quaternion.h"
%include "toric/Vector.h"
%include "toric/Toric.h"
