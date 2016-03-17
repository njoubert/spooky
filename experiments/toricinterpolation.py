import os, inspect, sys

import numpy as np
import numpy.linalg as la

def add_import_search_dir(path):
  cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],path)))
  if cmd_subfolder not in sys.path:
   sys.path.insert(0, cmd_subfolder)

add_import_search_dir('../shims/toric')
import toric
import toric.shims

#
# Helper functions for the toric libary
#

def vector3_to_str(v):
    return "(%.2f, %.2f, %.2f)" % (v.x(), v.y(), v.z())
    
def toric_to_str(t):
    return "(a = %.2f, t = %2.f, p = %.2f)" % (t.getAlpha().valueDegrees(), t.getTheta().valueDegrees(), t.getPhi().valueDegrees())

def vector3_to_np3(v):
    return np.array([v.x(),v.y(),v.z()])

def np3_to_vector3(v):
    return toric.Vector3(v[0],v[1],v[2])

def vector3_to_np2(v):
    return np.array([v.x(),v.y()])

def toric_to_cam_np(t, PA, PB):
    c = toric.Toric3_ToWorldPosition(t, PA, PB)
    return vector3_to_np3(c)

def slerp(p0, p1, t):
    omega = np.arccos(np.dot(p0/np.linalg.norm(p0), p1/np.linalg.norm(p1)))
    so = np.sin(omega)
    return np.sin((1.0-t)*omega) / so * p0 + np.sin(t*omega)/so * p1

# Returns the angle in radians between vectors 'v1' and 'v2' 
def py_ang(v1, v2):
    cosang = np.dot(v1, v2)
    sinang = la.norm(np.cross(v1, v2))
    return np.arctan2(sinang, cosang)

#
# Convert from world to visual features
#

def world_to_visualfeatures(C, PA, PB):
    # convert to toric for alpha
    C_toric = toric.Toric3_FromWorldPosition(C,PA,PB)
    alpha = C_toric.getAlpha().valueRadians()
    print C_toric

    # calculate distance and vantage vectors
    C_PA = vector3_to_np3(C) - vector3_to_np3(PA)
    C_PB = vector3_to_np3(C) - vector3_to_np3(PB)
    C_distance_A = la.norm(C_PA)
    C_distance_B = la.norm(C_PB)
    C_vantage_A = C_PA / C_distance_A
    C_vantage_B = C_PB / C_distance_B

    return {'alpha':alpha, 'dist_A':C_distance_A, 'dist_B':C_distance_B, 'vant_A':C_vantage_A, 'vant_B':C_vantage_B}

#
# Convert back to Cartesian
#

def visualfeatures_to_world(a):
    alpha = a[0]
    dist_A = a[1]
    dist_B = a[2]
    vant_A = np.array([a[3], a[4], a[5]])
    vant_A /= np.linalg.norm(vant_A)
    vant_B = np.array([a[6], a[7], a[8]])
    vant_B /= np.linalg.norm(vant_B)
    PA = np.array([a[9], a[10], a[11]])
    PB = np.array([a[12], a[13], a[14]])
    PAB = PA - PB

    # manifold surface generated by interpolated alpha ??
    # intersect manifold with vantage vectors
    # calculate distance
    dist_A_alpha = dist_A
    dist_B_alpha = dist_B
    
    # calculate lambda
    # sinusoid taking as input the angle between vantage and line AB (separating the two targets)
    line_AB = np3_to_vector3(PAB).perpendicular()
    angle_A = py_ang(vector3_to_np3(line_AB), vant_A) #line_AB.directedAngle(line_AB, np3_to_vector3(vant_A))
    angle_B = py_ang(vector3_to_np3(line_AB), vant_B)
    lambda_A = np.sin(angle_A)
    lambda_B = np.sin(angle_B)
    
    F = PA + PB
    F += (vant_A * (dist_A + dist_A_alpha * lambda_A) / (1 + lambda_A))
    F += (vant_B * (dist_B + dist_B_alpha * lambda_B) / (1 + lambda_B))
    F *= 0.5
    return F

#
# Interpolate visual features
#

def toric_interpolation(C_1, PA_1, PB_1, C_2, PA_2, PB_2):
    # convert to visual features
    visualfeatures_1 = world_to_visualfeatures(C_1, PA_1, PB_1)
    C_1_alpha = visualfeatures_1['alpha']
    C_1_distance_A = visualfeatures_1['dist_A']
    C_1_distance_B = visualfeatures_1['dist_B']
    C_1_vantage_A = visualfeatures_1['vant_A']
    C_1_vantage_B = visualfeatures_1['vant_B']

    visualfeatures_2 = world_to_visualfeatures(C_2, PA_2, PB_2)
    C_2_alpha = visualfeatures_2['alpha']
    C_2_distance_A = visualfeatures_2['dist_A']
    C_2_distance_B = visualfeatures_2['dist_B']
    C_2_vantage_A = visualfeatures_2['vant_A']
    C_2_vantage_B = visualfeatures_2['vant_B']

    # interpolate (lerp alpha and distance, slerp vantage)
    t = np.c_[np.linspace(0,1)]

    PA_x = np.linspace(PA_1.x(),PA_1.x())#np.apply_along_axis(lambda t : slerp(vector3_to_np3(PA_1),vector3_to_np3(PA_1),t), axis=1, arr=t) # temporary, change this
    PA_y = np.linspace(PA_1.y(),PA_1.y())
    PA_z = np.linspace(PA_1.z(),PA_1.z())
    PB_x = np.linspace(PB_1.x(),PB_1.x())#alpha_lin = np.linspace(C_1_toric.getAlpha().valueRadians(),C_2_toric.getAlpha().valueRadians())
    PB_y = np.linspace(PB_1.y(),PB_1.y())
    PB_z = np.linspace(PB_1.z(),PB_1.z())
    alpha_lin = np.linspace(C_1_alpha,C_2_alpha)
    distance_A_lin = np.linspace(C_1_distance_A,C_2_distance_A)
    distance_B_lin = np.linspace(C_1_distance_B,C_2_distance_B)
    vantage_A_slerp = np.apply_along_axis(lambda t : slerp(C_1_vantage_A,C_2_vantage_A,t), axis=1, arr=t)
    vantage_B_slerp = np.apply_along_axis(lambda t : slerp(C_1_vantage_B,C_2_vantage_B,t), axis=1, arr=t)

    # convert back to world space
    V = np.c_[alpha_lin, distance_A_lin, distance_B_lin, vantage_A_slerp, vantage_B_slerp, PA_x, PA_y, PA_z, PB_x, PB_y, PB_z]
    F = np.apply_along_axis(visualfeatures_to_world, axis=1, arr=V)

    # for different PA_1, PB_1 and PA_2, PB_2
    # compute second trajectory around PA_2 and PB_2 and combine through non-linear interpolation (p(t))

    return {'F':F, 't':t}

#
# Basic Test
#

# let's set a minimum distance of 0.9m
min_dist = 1

# starting people positons
PA_1 = toric.Vector3(0,0,0)
PB_1 = toric.Vector3(2,0,0)

# ending people positions: for the moment the positions are the same
PA_2 = toric.Vector3(0,0,0)
PB_2 = toric.Vector3(2,0,0)

# Starting camera position is *outside* of PA_1:
C_1 = toric.Vector3(-1,-0.5,0)
C_2 = toric.Vector3( 3,-1,0)

toric_interpolation(C_1, PA_1, PB_1, C_2, PA_2, PB_2)

