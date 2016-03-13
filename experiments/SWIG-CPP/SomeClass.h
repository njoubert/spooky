#ifndef _SOME_CLASS_H_
#define _SOME_CLASS_H_

#include "OtherClass.h"

class SomeClass
{
private:
    int     mValA;
    int     mValB;
public:
    SomeClass();
    SomeClass(const OtherClass & other);
    virtual ~SomeClass();
    void MethodA();
    void MethodB(int a = 5);
    int GetValA();
};

#endif  // _SOME_CLASS_H_