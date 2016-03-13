#include "SomeClass.h"

SomeClass::SomeClass() {
	mValA = 0;
	mValB = 0;
};

SomeClass::SomeClass(const OtherClass & other) {
	mValA = other.alpha;
	mValB = other.theta;
}

SomeClass::~SomeClass() {

}

void SomeClass::MethodA() {
	return;
}

void SomeClass::MethodB(int a) {
	mValA = a;
}

int SomeClass::GetValA() {
	return mValA;
}