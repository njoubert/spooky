#################################################
# IMPORTS
#################################################

# Globally useful stuff
import os, inspect, sys
from sets import Set


# "Flashlight" quadrotor stuff
def add_import_search_dir(path):
  cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],path)))
  if cmd_subfolder not in sys.path:
   sys.path.insert(0, cmd_subfolder)

add_import_search_dir('../../src/spooky')
from coords import *

add_import_search_dir('../../../Frankencopter/Code/')
add_import_search_dir('../../../Frankencopter/Code/flashlight')
from splineutils import *
from curveutils import *
from quadrotorcamera3d import *

add_import_search_dir('../../../Frankencopter/Code/HorusApp/app')
import trajectoryAPI

add_import_search_dir('../../shims/toric')
import toric

add_import_search_dir('../')
import toricinterpolation

add_import_search_dir('../trajectories')
import optimized_spherical_paths as osp
import numpy as np


PA = np.array([0, 0, 0])
PB = np.array([2, 0, 0])

C0 = np.array([0, 2, 0])
C1 = np.array([2, 2, 0])

params = {
  'minDist': 1
}

sigma, wA, sigmaAvg, sigmaA, sigmaB, t = osp.calculate_position_trajectory_as_optimized_blend_of_spherical_trajectories(
  PA, PB, C0, C1, osp.real_optimizer_unconstrained_at_endpoints, params)

print "Parameterizing returned sigma trajectory over time..."

P_cameraPose = sigma

print "P: "
print P_cameraPose
T_cameraPose = c_[t, t, t]
P_positionSpline = trajectoryAPI.compute_easing_spline_trajectory(P_cameraPose, T_cameraPose)

print P_positionSpline

