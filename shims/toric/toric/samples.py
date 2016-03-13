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
            fp, pathname, description = imp.find_module('_samples', [dirname(__file__)])
        except ImportError:
            import _samples
            return _samples
        if fp is not None:
            try:
                _mod = imp.load_module('_samples', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _samples = swig_import_helper()
    del swig_import_helper
else:
    import _samples
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


import __init__
class TargetOOBB(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, TargetOOBB, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, TargetOOBB, name)
    __repr__ = _swig_repr
    __swig_setmethods__["position"] = _samples.TargetOOBB_position_set
    __swig_getmethods__["position"] = _samples.TargetOOBB_position_get
    if _newclass:
        position = _swig_property(_samples.TargetOOBB_position_get, _samples.TargetOOBB_position_set)
    __swig_setmethods__["orientation"] = _samples.TargetOOBB_orientation_set
    __swig_getmethods__["orientation"] = _samples.TargetOOBB_orientation_get
    if _newclass:
        orientation = _swig_property(_samples.TargetOOBB_orientation_get, _samples.TargetOOBB_orientation_set)
    __swig_setmethods__["dimension"] = _samples.TargetOOBB_dimension_set
    __swig_getmethods__["dimension"] = _samples.TargetOOBB_dimension_get
    if _newclass:
        dimension = _swig_property(_samples.TargetOOBB_dimension_get, _samples.TargetOOBB_dimension_set)

    def getVantageVector(self, hAngle, vAngle):
        return _samples.TargetOOBB_getVantageVector(self, hAngle, vAngle)

    def GetVisualFeaturesFromViewpoint(self, cam):
        return _samples.TargetOOBB_GetVisualFeaturesFromViewpoint(self, cam)

    def __init__(self):
        this = _samples.new_TargetOOBB()
        try:
            self.this.append(this)
        except:
            self.this = this
    __swig_destroy__ = _samples.delete_TargetOOBB
    __del__ = lambda self: None
TargetOOBB_swigregister = _samples.TargetOOBB_swigregister
TargetOOBB_swigregister(TargetOOBB)

class TargetOOBS(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, TargetOOBS, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, TargetOOBS, name)
    __repr__ = _swig_repr
    __swig_setmethods__["position"] = _samples.TargetOOBS_position_set
    __swig_getmethods__["position"] = _samples.TargetOOBS_position_get
    if _newclass:
        position = _swig_property(_samples.TargetOOBS_position_get, _samples.TargetOOBS_position_set)
    __swig_setmethods__["orientation"] = _samples.TargetOOBS_orientation_set
    __swig_getmethods__["orientation"] = _samples.TargetOOBS_orientation_get
    if _newclass:
        orientation = _swig_property(_samples.TargetOOBS_orientation_get, _samples.TargetOOBS_orientation_set)
    __swig_setmethods__["radius"] = _samples.TargetOOBS_radius_set
    __swig_getmethods__["radius"] = _samples.TargetOOBS_radius_get
    if _newclass:
        radius = _swig_property(_samples.TargetOOBS_radius_get, _samples.TargetOOBS_radius_set)

    def getVantageVector(self, hAngle, vAngle):
        return _samples.TargetOOBS_getVantageVector(self, hAngle, vAngle)

    def GetDistanceFromScreenHeight(self, fovX, aspect, screenHeight):
        return _samples.TargetOOBS_GetDistanceFromScreenHeight(self, fovX, aspect, screenHeight)

    def GetScreenHeightFromDistance(self, fovX, aspect, distance):
        return _samples.TargetOOBS_GetScreenHeightFromDistance(self, fovX, aspect, distance)

    def GetVisualFeaturesFromViewpoint(self, cam):
        return _samples.TargetOOBS_GetVisualFeaturesFromViewpoint(self, cam)

    def __init__(self):
        this = _samples.new_TargetOOBS()
        try:
            self.this.append(this)
        except:
            self.this = this
    __swig_destroy__ = _samples.delete_TargetOOBS
    __del__ = lambda self: None
TargetOOBS_swigregister = _samples.TargetOOBS_swigregister
TargetOOBS_swigregister(TargetOOBS)

class TwoSphereTargetProblem(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, TwoSphereTargetProblem, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, TwoSphereTargetProblem, name)
    __repr__ = _swig_repr
    Target1 = _samples.TwoSphereTargetProblem_Target1
    Target2 = _samples.TwoSphereTargetProblem_Target2

    def __init__(self, fovX, screenAspect, target1, target2, sposTarget1, sposTarget2):
        this = _samples.new_TwoSphereTargetProblem(fovX, screenAspect, target1, target2, sposTarget1, sposTarget2)
        try:
            self.this.append(this)
        except:
            self.this = this

    def ComputeViewpointFromDistance(self, distance, whichOne):
        return _samples.TwoSphereTargetProblem_ComputeViewpointFromDistance(self, distance, whichOne)

    def ComputeViewpointFromScreenHeight(self, screenHeight, whichOne):
        return _samples.TwoSphereTargetProblem_ComputeViewpointFromScreenHeight(self, screenHeight, whichOne)

    def ComputeViewpointFromVantage(self, hAngle, vAngle, whichOne):
        return _samples.TwoSphereTargetProblem_ComputeViewpointFromVantage(self, hAngle, vAngle, whichOne)
    __swig_destroy__ = _samples.delete_TwoSphereTargetProblem
    __del__ = lambda self: None
TwoSphereTargetProblem_swigregister = _samples.TwoSphereTargetProblem_swigregister
TwoSphereTargetProblem_swigregister(TwoSphereTargetProblem)

class SingleSphereTargetProblem(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SingleSphereTargetProblem, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SingleSphereTargetProblem, name)
    __repr__ = _swig_repr

    def __init__(self, fovX, screenAspect, target, screen_pos):
        this = _samples.new_SingleSphereTargetProblem(fovX, screenAspect, target, screen_pos)
        try:
            self.this.append(this)
        except:
            self.this = this

    def ComputeViewpointFromScreenHeightAndVantage(self, screen_height, hAngle, vAngle):
        return _samples.SingleSphereTargetProblem_ComputeViewpointFromScreenHeightAndVantage(self, screen_height, hAngle, vAngle)
    __swig_destroy__ = _samples.delete_SingleSphereTargetProblem
    __del__ = lambda self: None
SingleSphereTargetProblem_swigregister = _samples.SingleSphereTargetProblem_swigregister
SingleSphereTargetProblem_swigregister(SingleSphereTargetProblem)

class SingleBoxTargetProblem(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SingleBoxTargetProblem, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SingleBoxTargetProblem, name)
    __repr__ = _swig_repr

    def __init__(self, fovX, screenAspect, target, screen_pos, screen_height):
        this = _samples.new_SingleBoxTargetProblem(fovX, screenAspect, target, screen_pos, screen_height)
        try:
            self.this.append(this)
        except:
            self.this = this

    def ComputeViewpointFromVantage(self, hAngle, vAngle):
        return _samples.SingleBoxTargetProblem_ComputeViewpointFromVantage(self, hAngle, vAngle)
    __swig_destroy__ = _samples.delete_SingleBoxTargetProblem
    __del__ = lambda self: None
SingleBoxTargetProblem_swigregister = _samples.SingleBoxTargetProblem_swigregister
SingleBoxTargetProblem_swigregister(SingleBoxTargetProblem)

# This file is compatible with both classic and new-style classes.


