%module mymodule

%{

#include "OtherClass.h"
#include "SomeClass.h"
#include "Euler.h"
#include "Vector.h"
#include "Toric.h"

using namespace toric;

%}

%include "OtherClass.h"
%include "SomeClass.h"

%include "Vector.h"
%include "Euler.h"
%include "Toric.h"
