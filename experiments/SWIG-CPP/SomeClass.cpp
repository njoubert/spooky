#include "SomeClass.h"

SomeClass::SomeClass() {
	mValA = 0;
	mValB = 0;
};

SomeClass::SomeClass(int a, int b) {
	mValA = a;
	mValB = b;
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