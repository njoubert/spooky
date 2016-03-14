# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.7
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_toric', [dirname(__file__)])
        except ImportError:
            import _toric
            return _toric
        if fp is not None:
            try:
                _mod = imp.load_module('_toric', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _toric = swig_import_helper()
    del swig_import_helper
else:
    import _toric
del version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr_nondynamic(self, class_type, name, static=1):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    if (not static):
        return object.__getattr__(self, name)
    else:
        raise AttributeError(name)

def _swig_getattr(self, class_type, name):
    return _swig_getattr_nondynamic(self, class_type, name, 0)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object:
        pass
    _newclass = 0


class Camera(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Camera, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Camera, name)
    __repr__ = _swig_repr
    __swig_setmethods__["fovX"] = _toric.Camera_fovX_set
    __swig_getmethods__["fovX"] = _toric.Camera_fovX_get
    if _newclass:
        fovX = _swig_property(_toric.Camera_fovX_get, _toric.Camera_fovX_set)
    __swig_setmethods__["aspect"] = _toric.Camera_aspect_set
    __swig_getmethods__["aspect"] = _toric.Camera_aspect_get
    if _newclass:
        aspect = _swig_property(_toric.Camera_aspect_get, _toric.Camera_aspect_set)
    __swig_setmethods__["position"] = _toric.Camera_position_set
    __swig_getmethods__["position"] = _toric.Camera_position_get
    if _newclass:
        position = _swig_property(_toric.Camera_position_get, _toric.Camera_position_set)
    __swig_setmethods__["orientation"] = _toric.Camera_orientation_set
    __swig_getmethods__["orientation"] = _toric.Camera_orientation_get
    if _newclass:
        orientation = _swig_property(_toric.Camera_orientation_get, _toric.Camera_orientation_set)

    def __init__(self):
        this = _toric.new_Camera()
        try:
            self.this.append(this)
        except:
            self.this = this

    def setFovY(self, fovY):
        return _toric.Camera_setFovY(self, fovY)

    def getFOVy(self):
        return _toric.Camera_getFOVy(self)
    __swig_destroy__ = _toric.delete_Camera
    __del__ = lambda self: None
Camera_swigregister = _toric.Camera_swigregister
Camera_swigregister(Camera)

class RadianPi(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, RadianPi, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, RadianPi, name)
    __repr__ = _swig_repr
    __swig_setmethods__["ZERO"] = _toric.RadianPi_ZERO_set
    __swig_getmethods__["ZERO"] = _toric.RadianPi_ZERO_get
    if _newclass:
        ZERO = _swig_property(_toric.RadianPi_ZERO_get, _toric.RadianPi_ZERO_set)

    def __init__(self, r=0.0):
        this = _toric.new_RadianPi(r)
        try:
            self.this.append(this)
        except:
            self.this = this

    def valueRadians(self):
        return _toric.RadianPi_valueRadians(self)

    def valueDegrees(self):
        return _toric.RadianPi_valueDegrees(self)

    def __neg__(self):
        return _toric.RadianPi___neg__(self)

    def __mul__(self, val):
        return _toric.RadianPi___mul__(self, val)

    def __div__(self, val):
        return _toric.RadianPi___div__(self, val)
    __swig_destroy__ = _toric.delete_RadianPi
    __del__ = lambda self: None
RadianPi_swigregister = _toric.RadianPi_swigregister
RadianPi_swigregister(RadianPi)
cvar = _toric.cvar

class Radian2Pi(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Radian2Pi, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Radian2Pi, name)
    __repr__ = _swig_repr
    __swig_setmethods__["ZERO"] = _toric.Radian2Pi_ZERO_set
    __swig_getmethods__["ZERO"] = _toric.Radian2Pi_ZERO_get
    if _newclass:
        ZERO = _swig_property(_toric.Radian2Pi_ZERO_get, _toric.Radian2Pi_ZERO_set)

    def __init__(self, r=0.0):
        this = _toric.new_Radian2Pi(r)
        try:
            self.this.append(this)
        except:
            self.this = this

    def valueRadians(self):
        return _toric.Radian2Pi_valueRadians(self)

    def valueDegrees(self):
        return _toric.Radian2Pi_valueDegrees(self)
    __swig_destroy__ = _toric.delete_Radian2Pi
    __del__ = lambda self: None
Radian2Pi_swigregister = _toric.Radian2Pi_swigregister
Radian2Pi_swigregister(Radian2Pi)


def cos(r):
    return _toric.cos(r)
cos = _toric.cos

def sin(r):
    return _toric.sin(r)
sin = _toric.sin

def tan(r):
    return _toric.tan(r)
tan = _toric.tan

def acos(r):
    return _toric.acos(r)
acos = _toric.acos

def asin(r):
    return _toric.asin(r)
asin = _toric.asin

def atan(r):
    return _toric.atan(r)
atan = _toric.atan
class Matrix3(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Matrix3, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Matrix3, name)
    __repr__ = _swig_repr

    def __init__(self):
        this = _toric.new_Matrix3()
        try:
            self.this.append(this)
        except:
            self.this = this

    def at(self, i, j):
        return _toric.Matrix3_at(self, i, j)

    def __call__(self, *args):
        return _toric.Matrix3___call__(self, *args)

    def getColumn(self, j):
        return _toric.Matrix3_getColumn(self, j)

    def getRow(self, i):
        return _toric.Matrix3_getRow(self, i)

    def swapColumn(self, j, col):
        return _toric.Matrix3_swapColumn(self, j, col)

    def swapRow(self, i, row):
        return _toric.Matrix3_swapRow(self, i, row)

    def getDeterminant(self):
        return _toric.Matrix3_getDeterminant(self)

    def __mul__(self, v):
        return _toric.Matrix3___mul__(self, v)
    __swig_destroy__ = _toric.delete_Matrix3
    __del__ = lambda self: None
Matrix3_swigregister = _toric.Matrix3_swigregister
Matrix3_swigregister(Matrix3)

class ProjectionMatrix(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ProjectionMatrix, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ProjectionMatrix, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _toric.new_ProjectionMatrix(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def setFieldOfView(self, *args):
        return _toric.ProjectionMatrix_setFieldOfView(self, *args)

    def setPosition(self, p):
        return _toric.ProjectionMatrix_setPosition(self, p)

    def setOrientation(self, q):
        return _toric.ProjectionMatrix_setOrientation(self, q)

    def screenProjection(self, worldCoords):
        return _toric.ProjectionMatrix_screenProjection(self, worldCoords)

    def getSx(self):
        return _toric.ProjectionMatrix_getSx(self)

    def getSy(self):
        return _toric.ProjectionMatrix_getSy(self)
    __swig_getmethods__["ComputeScale"] = lambda x: _toric.ProjectionMatrix_ComputeScale
    if _newclass:
        ComputeScale = staticmethod(_toric.ProjectionMatrix_ComputeScale)
    __swig_getmethods__["GetVectorInCameraSpace"] = lambda x: _toric.ProjectionMatrix_GetVectorInCameraSpace
    if _newclass:
        GetVectorInCameraSpace = staticmethod(_toric.ProjectionMatrix_GetVectorInCameraSpace)
    __swig_destroy__ = _toric.delete_ProjectionMatrix
    __del__ = lambda self: None
ProjectionMatrix_swigregister = _toric.ProjectionMatrix_swigregister
ProjectionMatrix_swigregister(ProjectionMatrix)

def ProjectionMatrix_ComputeScale(*args):
    return _toric.ProjectionMatrix_ComputeScale(*args)
ProjectionMatrix_ComputeScale = _toric.ProjectionMatrix_ComputeScale

def ProjectionMatrix_GetVectorInCameraSpace(*args):
    return _toric.ProjectionMatrix_GetVectorInCameraSpace(*args)
ProjectionMatrix_GetVectorInCameraSpace = _toric.ProjectionMatrix_GetVectorInCameraSpace

class Quaternion(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Quaternion, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Quaternion, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _toric.new_Quaternion(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def set(self, *args):
        return _toric.Quaternion_set(self, *args)

    def FromAxes(self, xAxis, yAxis, zAxis):
        return _toric.Quaternion_FromAxes(self, xAxis, yAxis, zAxis)

    def ToAxes(self, xAxis, yAxis, zAxis):
        return _toric.Quaternion_ToAxes(self, xAxis, yAxis, zAxis)

    def FromRotationMatrix(self, mRot):
        return _toric.Quaternion_FromRotationMatrix(self, mRot)

    def ToRotationMatrix(self, mRot):
        return _toric.Quaternion_ToRotationMatrix(self, mRot)

    def xAxis(self):
        return _toric.Quaternion_xAxis(self)

    def yAxis(self):
        return _toric.Quaternion_yAxis(self)

    def zAxis(self):
        return _toric.Quaternion_zAxis(self)

    def s(self, *args):
        return _toric.Quaternion_s(self, *args)

    def v(self, *args):
        return _toric.Quaternion_v(self, *args)

    def w(self):
        return _toric.Quaternion_w(self)

    def x(self):
        return _toric.Quaternion_x(self)

    def y(self):
        return _toric.Quaternion_y(self)

    def z(self):
        return _toric.Quaternion_z(self)

    def __mul__(self, *args):
        return _toric.Quaternion___mul__(self, *args)

    def inverse(self):
        return _toric.Quaternion_inverse(self)

    def norm2(self):
        return _toric.Quaternion_norm2(self)

    def norm(self):
        return _toric.Quaternion_norm(self)

    def dotProduct(self, q):
        return _toric.Quaternion_dotProduct(self, q)
    __swig_destroy__ = _toric.delete_Quaternion
    __del__ = lambda self: None
Quaternion_swigregister = _toric.Quaternion_swigregister
Quaternion_swigregister(Quaternion)
Quaternion.ZERO = _toric.cvar.Quaternion_ZERO
Quaternion.IDENTITY = _toric.cvar.Quaternion_IDENTITY

class Vector2(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Vector2, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Vector2, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _toric.new_Vector2(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def x(self):
        return _toric.Vector2_x(self)

    def y(self):
        return _toric.Vector2_y(self)

    def rotate90(self):
        return _toric.Vector2_rotate90(self)

    def rotate180(self):
        return _toric.Vector2_rotate180(self)

    def rotate270(self):
        return _toric.Vector2_rotate270(self)

    def rotate(self, theta):
        return _toric.Vector2_rotate(self, theta)

    def rotated90(self):
        return _toric.Vector2_rotated90(self)

    def rotated180(self):
        return _toric.Vector2_rotated180(self)

    def rotated270(self):
        return _toric.Vector2_rotated270(self)
    __swig_destroy__ = _toric.delete_Vector2
    __del__ = lambda self: None
Vector2_swigregister = _toric.Vector2_swigregister
Vector2_swigregister(Vector2)

class Vector3(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Vector3, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Vector3, name)
    __repr__ = _swig_repr
    __swig_setmethods__["ZERO"] = _toric.Vector3_ZERO_set
    __swig_getmethods__["ZERO"] = _toric.Vector3_ZERO_get
    if _newclass:
        ZERO = _swig_property(_toric.Vector3_ZERO_get, _toric.Vector3_ZERO_set)
    __swig_setmethods__["UNIT_X"] = _toric.Vector3_UNIT_X_set
    __swig_getmethods__["UNIT_X"] = _toric.Vector3_UNIT_X_get
    if _newclass:
        UNIT_X = _swig_property(_toric.Vector3_UNIT_X_get, _toric.Vector3_UNIT_X_set)
    __swig_setmethods__["UNIT_Y"] = _toric.Vector3_UNIT_Y_set
    __swig_getmethods__["UNIT_Y"] = _toric.Vector3_UNIT_Y_get
    if _newclass:
        UNIT_Y = _swig_property(_toric.Vector3_UNIT_Y_get, _toric.Vector3_UNIT_Y_set)
    __swig_setmethods__["UNIT_Z"] = _toric.Vector3_UNIT_Z_set
    __swig_getmethods__["UNIT_Z"] = _toric.Vector3_UNIT_Z_get
    if _newclass:
        UNIT_Z = _swig_property(_toric.Vector3_UNIT_Z_get, _toric.Vector3_UNIT_Z_set)

    def __init__(self, *args):
        this = _toric.new_Vector3(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def x(self):
        return _toric.Vector3_x(self)

    def y(self):
        return _toric.Vector3_y(self)

    def z(self):
        return _toric.Vector3_z(self)

    def projectX(self):
        return _toric.Vector3_projectX(self)

    def projectY(self):
        return _toric.Vector3_projectY(self)

    def projectZ(self):
        return _toric.Vector3_projectZ(self)

    def crossProduct(self, v):
        return _toric.Vector3_crossProduct(self, v)

    def __xor__(self, v):
        return _toric.Vector3___xor__(self, v)

    def perpendicular(self):
        return _toric.Vector3_perpendicular(self)

    def directedAngle(self, vec, normal):
        return _toric.Vector3_directedAngle(self, vec, normal)
    __swig_destroy__ = _toric.delete_Vector3
    __del__ = lambda self: None
Vector3_swigregister = _toric.Vector3_swigregister
Vector3_swigregister(Vector3)

class ToricManifold(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ToricManifold, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ToricManifold, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _toric.new_ToricManifold(*args)
        try:
            self.this.append(this)
        except:
            self.this = this
    __swig_getmethods__["BuildFromAlpha"] = lambda x: _toric.ToricManifold_BuildFromAlpha
    if _newclass:
        BuildFromAlpha = staticmethod(_toric.ToricManifold_BuildFromAlpha)

    def computePosition(self, theta, phi):
        return _toric.ToricManifold_computePosition(self, theta, phi)

    def computeOrientation(self, position):
        return _toric.ToricManifold_computeOrientation(self, position)

    def getAlpha(self):
        return _toric.ToricManifold_getAlpha(self)

    def getPositionA(self):
        return _toric.ToricManifold_getPositionA(self)

    def getPositionB(self):
        return _toric.ToricManifold_getPositionB(self)

    def getZero(self):
        return _toric.ToricManifold_getZero(self)

    def getMaxTheta(self):
        return _toric.ToricManifold_getMaxTheta(self)

    def getMaximumDistanceToTargets(self):
        return _toric.ToricManifold_getMaximumDistanceToTargets(self)

    def getDistance(self, point):
        return _toric.ToricManifold_getDistance(self, point)

    def getThetasFromDistanceToA(self, d):
        return _toric.ToricManifold_getThetasFromDistanceToA(self, d)

    def getThetasFromDistanceToB(self, d):
        return _toric.ToricManifold_getThetasFromDistanceToB(self, d)

    def getPositionFromVantageToA(self, vectorFromA):
        return _toric.ToricManifold_getPositionFromVantageToA(self, vectorFromA)

    def getPositionFromVantageToB(self, vectorFromB):
        return _toric.ToricManifold_getPositionFromVantageToB(self, vectorFromB)

    def getPositionFromVantageToMiddleAB(self, vectorFromMiddle):
        return _toric.ToricManifold_getPositionFromVantageToMiddleAB(self, vectorFromMiddle)

    def getThetaFromRatio(self, thetaRatio):
        return _toric.ToricManifold_getThetaFromRatio(self, thetaRatio)
    __swig_destroy__ = _toric.delete_ToricManifold
    __del__ = lambda self: None
ToricManifold_swigregister = _toric.ToricManifold_swigregister
ToricManifold_swigregister(ToricManifold)

def ToricManifold_BuildFromAlpha(*args):
    return _toric.ToricManifold_BuildFromAlpha(*args)
ToricManifold_BuildFromAlpha = _toric.ToricManifold_BuildFromAlpha

class Toric2(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Toric2, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Toric2, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _toric.new_Toric2(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def getTheta(self):
        return _toric.Toric2_getTheta(self)

    def getPhi(self):
        return _toric.Toric2_getPhi(self)
    __swig_destroy__ = _toric.delete_Toric2
    __del__ = lambda self: None
Toric2_swigregister = _toric.Toric2_swigregister
Toric2_swigregister(Toric2)

class Toric3(Toric2):
    __swig_setmethods__ = {}
    for _s in [Toric2]:
        __swig_setmethods__.update(getattr(_s, '__swig_setmethods__', {}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Toric3, name, value)
    __swig_getmethods__ = {}
    for _s in [Toric2]:
        __swig_getmethods__.update(getattr(_s, '__swig_getmethods__', {}))
    __getattr__ = lambda self, name: _swig_getattr(self, Toric3, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _toric.new_Toric3(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def getAlpha(self):
        return _toric.Toric3_getAlpha(self)

    def setTheta(self, theta):
        return _toric.Toric3_setTheta(self, theta)

    def setPhi(self, phi):
        return _toric.Toric3_setPhi(self, phi)

    def setAlpha(self, alpha):
        return _toric.Toric3_setAlpha(self, alpha)

    def getThetaRatio(self):
        return _toric.Toric3_getThetaRatio(self)

    def set(self, alpha, theta, phi):
        return _toric.Toric3_set(self, alpha, theta, phi)

    def __eq__(self, t):
        return _toric.Toric3___eq__(self, t)

    def __ne__(self, t):
        return _toric.Toric3___ne__(self, t)
    __swig_getmethods__["FromWorldPosition"] = lambda x: _toric.Toric3_FromWorldPosition
    if _newclass:
        FromWorldPosition = staticmethod(_toric.Toric3_FromWorldPosition)
    __swig_getmethods__["ToWorldPosition"] = lambda x: _toric.Toric3_ToWorldPosition
    if _newclass:
        ToWorldPosition = staticmethod(_toric.Toric3_ToWorldPosition)
    __swig_getmethods__["ComputeThetaRatio"] = lambda x: _toric.Toric3_ComputeThetaRatio
    if _newclass:
        ComputeThetaRatio = staticmethod(_toric.Toric3_ComputeThetaRatio)
    __swig_getmethods__["ComputeTheta"] = lambda x: _toric.Toric3_ComputeTheta
    if _newclass:
        ComputeTheta = staticmethod(_toric.Toric3_ComputeTheta)
    __swig_getmethods__["Scale"] = lambda x: _toric.Toric3_Scale
    if _newclass:
        Scale = staticmethod(_toric.Toric3_Scale)
    __swig_getmethods__["ComputeOrientationForOneTarget"] = lambda x: _toric.Toric3_ComputeOrientationForOneTarget
    if _newclass:
        ComputeOrientationForOneTarget = staticmethod(_toric.Toric3_ComputeOrientationForOneTarget)
    __swig_getmethods__["ComputeOrientationForTwoTargets"] = lambda x: _toric.Toric3_ComputeOrientationForTwoTargets
    if _newclass:
        ComputeOrientationForTwoTargets = staticmethod(_toric.Toric3_ComputeOrientationForTwoTargets)

    def _getBeta(self):
        return _toric.Toric3__getBeta(self)
    __swig_getmethods__["_ComputeOrientationForOneTarget"] = lambda x: _toric.Toric3__ComputeOrientationForOneTarget
    if _newclass:
        _ComputeOrientationForOneTarget = staticmethod(_toric.Toric3__ComputeOrientationForOneTarget)
    __swig_getmethods__["_ComputeOrientationForTwoTargets"] = lambda x: _toric.Toric3__ComputeOrientationForTwoTargets
    if _newclass:
        _ComputeOrientationForTwoTargets = staticmethod(_toric.Toric3__ComputeOrientationForTwoTargets)
    __swig_destroy__ = _toric.delete_Toric3
    __del__ = lambda self: None
Toric3_swigregister = _toric.Toric3_swigregister
Toric3_swigregister(Toric3)

def Toric3_FromWorldPosition(*args):
    return _toric.Toric3_FromWorldPosition(*args)
Toric3_FromWorldPosition = _toric.Toric3_FromWorldPosition

def Toric3_ToWorldPosition(*args):
    return _toric.Toric3_ToWorldPosition(*args)
Toric3_ToWorldPosition = _toric.Toric3_ToWorldPosition

def Toric3_ComputeThetaRatio(theta, alpha):
    return _toric.Toric3_ComputeThetaRatio(theta, alpha)
Toric3_ComputeThetaRatio = _toric.Toric3_ComputeThetaRatio

def Toric3_ComputeTheta(thetaRatio, alpha):
    return _toric.Toric3_ComputeTheta(thetaRatio, alpha)
Toric3_ComputeTheta = _toric.Toric3_ComputeTheta

def Toric3_Scale(reference, new_alpha):
    return _toric.Toric3_Scale(reference, new_alpha)
Toric3_Scale = _toric.Toric3_Scale

def Toric3_ComputeOrientationForOneTarget(campos, spos, wpos, fovX, fovY):
    return _toric.Toric3_ComputeOrientationForOneTarget(campos, spos, wpos, fovX, fovY)
Toric3_ComputeOrientationForOneTarget = _toric.Toric3_ComputeOrientationForOneTarget

def Toric3_ComputeOrientationForTwoTargets(campos, sposA, sposB, wposA, wposB, fovX, fovY):
    return _toric.Toric3_ComputeOrientationForTwoTargets(campos, sposA, sposB, wposA, wposB, fovX, fovY)
Toric3_ComputeOrientationForTwoTargets = _toric.Toric3_ComputeOrientationForTwoTargets

def Toric3__ComputeOrientationForOneTarget(*args):
    return _toric.Toric3__ComputeOrientationForOneTarget(*args)
Toric3__ComputeOrientationForOneTarget = _toric.Toric3__ComputeOrientationForOneTarget

def Toric3__ComputeOrientationForTwoTargets(*args):
    return _toric.Toric3__ComputeOrientationForTwoTargets(*args)
Toric3__ComputeOrientationForTwoTargets = _toric.Toric3__ComputeOrientationForTwoTargets

# This file is compatible with both classic and new-style classes.

