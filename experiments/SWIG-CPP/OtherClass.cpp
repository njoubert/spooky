#include "OtherClass.h"

OtherClass::OtherClass() {
	alpha = 0.0;
	theta = 0.0;
	gamma = 0.0;
}

OtherClass::OtherClass(double a, double t, double g) {
	alpha = a;
	theta = t;
	gamma = g;
}

OtherClass::~OtherClass() {

}

OtherClass OtherClass::FromWorldPos(double x, double y, double z) {
	return OtherClass(x + y + z, x - y - z, x + y - z);
}

double OtherClass::ToWorldPos(OtherClass& o) {
	return o.alpha + o.theta + o.gamma;
}