# coding=utf-8
# Copyright (2016) Stanford University
# Niels Joubert

import numpy as np
import toric
import toric.samples

'''

toricshims.py

  This module collects useful shims to work with the toric swig bindings.

'''


###
### Monkey Patching SWIG Classes. 
###   We can likely do this in a nicer way, inside the SWIG include file.
###

''' Add string output to Vector3 '''
def Vector3__str__(self):
  return "(%.2f, %.2f, %.2f)" % (self.x(), self.y(), self.z())

toric.Vector3.__str__ = Vector3__str__
toric.__init__.Vector3.__str__ = Vector3__str__

''' Add numpy output to Vector3 '''
def Vector3__np__(self):
  return np.array([self.x(),self.y(),self.z()])

toric.Vector3.np = Vector3__np__
toric.__init__.Vector3.np = Vector3__np__

''' Add string output to Vector2 '''
def Vector2__str__(self):
  return "(%.2f, %.2f)" % (self.x(), self.y())

toric.Vector2.__str__ = Vector2__str__
toric.__init__.Vector2.__str__ = Vector2__str__

''' Add numpy output to Vector3 '''
def Vector2__np__(self):
  return np.array([self.x(),self.y()])

toric.Vector2.np = Vector2__np__
toric.__init__.Vector2.np = Vector2__np__

''' Add string output to Toric3 '''
def Toric3__str__(self):
  return "(a = %.2f°, t = %2.f°, p = %.2f°)" % (self.getAlpha().valueDegrees(), self.getTheta().valueDegrees(), self.getPhi().valueDegrees())

toric.Toric3.__str__ = Toric3__str__
toric.__init__.Toric3.__str__ = Toric3__str__

''' Add numpy output to Vector3_ToWorldPosition '''
def Toric3_ToWorldPositionNP(t, PA, PB):
  c = toric.Toric3_ToWorldPosition(t, PA, PB)
  return c.np()

toric.Toric3_ToWorldPositionNP = Toric3_ToWorldPositionNP
