from pylab import *
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches

from matplotlib import gridspec

import numpy as np

def add_relative_to_current_source_file_path_to_sys_path(relpath):
    import os, sys, inspect
    path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],relpath)))
    if path not in sys.path:
        sys.path.insert(0,path)

add_relative_to_current_source_file_path_to_sys_path("../trajectories")   
import optimized_spherical_paths as osp

PA = np.array([-98.2,-40.6,-1.6])     # person A position
PB = np.array([-98.2,-38.6,-1.6])     # person B position
C0 = np.array([-92.9,-39.6,-0.8])
C1 = np.array([-96.5,-42.6,-1.3])


params = {
  'min_dist':1, 
  'nsamples':50, 
  'coord':'NED_mm',
  'force_paths_only_go_up':True
}

# position_trajectories = osp.calculate_position_trajectory_as_optimized_blend_of_spherical_trajectories(
#     PA, PB, C0, C1, osp.real_optimizer_constrained_at_endpoints, params)

# ## sigma is the resulting 3D trajectory.
# sigma, wA, sigmaAvg, sigmaA, sigmaB, u = position_trajectories


######################################
### DRAW "SETUP" - AKA THE PROBLEM INPUTS
######################################

    
def drawSetup(subfig, A, B, C0, C1, min_dist, fudgeX=2, fudgeY_pos=2,fudgeY_neg=8):
    subfig.set_aspect('equal')
    fig = subfig
    
    # Set up plot size
    subfig.set_xlim((np.min([A[0], B[0], C0[0], C1[0]])-fudgeX,np.max([A[0], B[0], C0[0], C1[0]])+fudgeX))
    subfig.set_ylim((np.min([A[1], B[1], C0[1], C1[1]])-fudgeY_neg,np.max([A[1], B[1], C0[1], C1[1]])+fudgeY_pos))

    # Draw People Positions
    subfig.scatter([A[0], B[0]],[A[1], B[1]],c="red",linewidths=0)
    line_AB = plt.Line2D([A[0], B[0]],[A[1], B[1]], c="black",alpha=0.3)
    subfig.add_artist(line_AB)

    # Draw Circles    
    circle_PA_1=plt.Circle(A,min_dist,color='g',alpha=0.3)
    circle_PB_1=plt.Circle(B,min_dist,color='g',alpha=0.3)
    
    subfig.add_artist(circle_PA_1)
    subfig.add_artist(circle_PB_1)

    subfig.annotate(s="A", xy=A[0:2],xytext=(3,4),textcoords="offset points")
    subfig.annotate(s="B", xy=B[0:2],xytext=(3,4),textcoords="offset points")
    
    # Draw Camera positions
    subfig.scatter([C0[0],C1[0]],[C0[1],C1[1]],c="blue",linewidths=0)
    subfig.annotate(s="C0", xy=C0[0:2],xytext=(3,4),textcoords="offset points")
    subfig.annotate(s="C1", xy=C1[0:2],xytext=(3,4),textcoords="offset points")



# ######################################
# ### DRAW TRAJECTORIES
# ######################################

rcParams['figure.figsize'] = 20, 3.5
gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 1], height_ratios=[1]) 
fig = plt.figure()

# fig.suptitle("", fontsize=18)

f1 = fig.add_subplot(gs[0])
f2 = fig.add_subplot(gs[1])
f3 = fig.add_subplot(gs[2])
f4 = fig.add_subplot(gs[3])
  
savefig("optimization_plot.png")
# #drawWorldTrajectoryGivenSubfigures(f1, f2, people, camera, position_trajectories, params)


  
