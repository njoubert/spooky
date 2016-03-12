#ifndef _OTHER_CLASS_H_
#define _OTHER_CLASS_H_

#include <cstdint>

class OtherClass
{
public:

    double    alpha;
    double    theta;
    double    gamma;

    OtherClass();
    OtherClass(double alpha, double theta, double gamma);
    virtual ~OtherClass();
    static OtherClass FromWorldPos(double x, double y, double z);
    static double ToWorldPos(OtherClass& o);
};

#endif  // _OTHER_CLASS_H_