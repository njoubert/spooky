# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

'''

This python module is based on Notebook 24, found in spooky/experiments/ipython/

It calculates a path that respects a minimum distance constraint to two people,
by optimizing a blend function between two spherically-interpolated paths.


EXAMPLE USAGE:

    
import numpy as np
import optimized_spherical_paths as osp

PA = np.array([-98.2,-40.6,-1.6])     # person A position
PB = np.array([-98.2,-38.6,-1.6])     # person B position
C0 = np.array([-92.9,-39.6,-0.8])
C1 = np.array([-96.5,-42.6,-1.3])


params = {
  'min_dist':1, 
  'nsamples':50, 
}

position_trajectories = osp.calculate_position_trajectory_as_optimized_blend_of_spherical_trajectories(
    PA, PB, C0, C1, osp.real_optimizer_unconstrained_at_endpoints, params)

## sigma is the resulting 3D trajectory.
sigma, wA, sigmaAvg, sigmaA, sigmaB = position_trajectories


'''

import time

import numpy as np
import scipy.sparse as sp
import numpy.linalg as la

from scipy import interpolate
from scipy.special import expit

from optimize.snopt7 import SNOPT_solver



def slerp(p0, p1, t):
    omega = np.arccos(np.dot(p0/np.linalg.norm(p0), p1/np.linalg.norm(p1)))
    so = np.sin(omega)
    return np.sin((1.0-t)*omega) / so * p0 + np.sin(t*omega)/so * p1


###############################################################################
# This is an entrypoint with customizable optimizers
###############################################################################
def calculate_position_trajectory_as_optimized_blend_of_spherical_trajectories(A, B, C0, C1, blendOptimizer, params):
    '''
    This function finds a trajectory from C0 to C1, 
    given A and B and a minimum distance constraint supplied as a parameter.

    It does this by optimizing a blend between two spherically interpolated function

    This function sets up the problem, and passes in the individual trajectories
    to the given blendOptimizer function. Thus, you can use different optimization 
    approaches to find a path from C0 to C1.

    The blendOptimizer function must return a blended trajectory as well as a blending function.
    
    Returns:
    All the trajectories it calculates
    
    '''
    nsamples = params['nsamples'] if 'nsamples' in params else 50
    min_dist = params['min_dist'] if 'min_dist' in params else 1
    
    # Set up interpolation vector
    u = np.c_[np.linspace(0,1,num=nsamples)]

    # Set up the distance components of sigmaA, sigmaB
    dA0 = la.norm(C0 - A)
    dA1 = la.norm(C1 - A)
    dB0 = la.norm(C0 - B)
    dB1 = la.norm(C1 - B)

    dA = np.linspace(dA0, dA1,num=nsamples)
    dB = np.linspace(dB0, dB1,num=nsamples)

    # Set up the vantage vector components of sigmaA, sigmaB
    vA0 = (C0 - A) / dA0
    vA1 = (C1 - A) / dA1
    vB0 = (C0 - B) / dB0
    vB1 = (C1 - B) / dB1

    vA = np.apply_along_axis(lambda u : slerp(vA0,vA1,u), axis=1, arr=u)
    vB = np.apply_along_axis(lambda u : slerp(vB0,vB1,u), axis=1, arr=u)

    # Set up sigmaA, sigmaB, sigma
    sigmaA = A + dA[:,np.newaxis] * vA
    sigmaB = B + dB[:,np.newaxis] * vB

    sigmaAvg = (sigmaA + sigmaB)/2
    wA, sigmaBlended = blendOptimizer(u, sigmaA, sigmaB, A, B, min_dist, min_dist, params)

    return sigmaBlended, wA, sigmaAvg, sigmaA, sigmaB 


###############################################################################
# Here is a blend optimization
###############################################################################
def optimize_blending_function_between_two_distance_sigmas(sigmaA, sigmaB, personA, personB, min_distA, min_distB, params, constrain_at_endpoints=False):
    '''
    This function finds a blend between two trajectories that respect two minimum distance constraints.
    '''
    # Some important parameters here
    nsamples = params['nsamples']
    ndims    = 6
    
    dt = 0.01
    xdot5_limit = 0.001

    inf = 1.0e20

    lambda_snap = 1#(1/dt)**4 # snap must be scaled down to be comparable to position.
    lambda_pos = 1

    # A few derived quantities
    nvars = ndims*nsamples
    nconstraints_continuity = (ndims-1)*nsamples
    nconstraints_obstacles = 2*nsamples
    nconstraints = 1 + nconstraints_continuity + nconstraints_obstacles

    # Solver configuration
    snopt = SNOPT_solver()
    snopt.setOption('Verbose',False)
    snopt.setOption('Solution print',False)
    snopt.setOption('Print file','test5.out')
    snopt.setOption('Iteration limit',8000)
    snopt.setOption('Print level',3)
    snopt.setOption('Major optimality',2e-6)
    snopt.setOption('Verify level',3) # Turn to 3 to carefully check gradiants


    # 1. Set up decision variables
    x     = np.array([0.5]*nsamples) # Initialize to 0.5
    xdot1 = np.array([0.0]*nsamples)
    xdot2 = np.array([0.0]*nsamples)
    xdot3 = np.array([0.0]*nsamples)
    xdot4 = np.array([0.0]*nsamples)
    v     = np.array([0.0]*nsamples) # C4 Continuity Control Variable

    x0 = np.matrix(np.c_[x,xdot1,xdot2,xdot3,xdot4,v]).A1 # Interleave [x[0],xdot1[0],xdot2[0]...]

    # 2. Set up the bounds on x
    low_x     = np.array([ 0.0] *nsamples) # X must be greater or equal to 0
    low_xdot1 = np.array([ -inf]*nsamples)
    low_xdot2 = np.array([ -inf]*nsamples)
    low_xdot3 = np.array([ -inf]*nsamples)
    low_xdot4 = np.array([ -inf]*nsamples)
    low_v     = np.array([ -xdot5_limit]*nsamples) # Bound control variable arbitrarily
    if constrain_at_endpoints:
        low_x[0] = 0.5
        low_x[nsamples-1] = 0.5    
    xlow = np.matrix(np.c_[low_x,low_xdot1,low_xdot2,low_xdot3,low_xdot4,low_v]).A1 # Interleave [x[0],xdot1[0],xdot2[0]...]

    upp_x     = np.array([ 1.0] *nsamples) # X must be greater or equal to 0
    upp_xdot1 = np.array([ inf]*nsamples)
    upp_xdot2 = np.array([ inf]*nsamples)
    upp_xdot3 = np.array([ inf]*nsamples)
    upp_xdot4 = np.array([ inf]*nsamples)
    upp_v     = np.array([ xdot5_limit]*nsamples) # Bound control variable arbitrarily
    if constrain_at_endpoints:
        upp_x[0] = 0.5
        upp_x[nsamples-1] = 0.5
    xupp = np.matrix(np.c_[upp_x,upp_xdot1,upp_xdot2,upp_xdot3,upp_xdot4,upp_v]).A1 # Interleave [x[0],xdot1[0],xdot2[0]...]

    # 3. Set up the objective function
    M = np.array([
            [0,1,0,0,0],
            [0,0,1,0,0],
            [0,0,0,1,0],
            [0,0,0,0,1],
            [0,0,0,0,0]
        ])

    N = np.array([0,0,0,0,1])

    def grad_function(xM, compute_nonzero_only=False, compute_linear=False):
        G = np.zeros((nconstraints, nvars))

        # Set up the jacobian structure of the cost function. 
        # This only impacts the w_i and wdot4_i variables 
        obj_col = G[0,:]
        if not compute_nonzero_only:
            obj_col[::6] = 2*dt*lambda_pos*(xM[:,0] - 0.5)
            obj_col[4::6] = 2*dt*lambda_snap*xM[:,4]
        elif not compute_linear:
            obj_col[::6] = 1
            obj_col[4::6] = 1        

        if compute_linear:
            # The C4 continuity constraint is linear
            stupidcounter = 0
            add_to_fi = 0    
            for fi in range(1,nconstraints_continuity-5): # Looping over the objective function
                fi_row = G[fi,:]

                fi += add_to_fi

                fi_row[fi-1] = 1
                fi_row[fi]   = dt
                fi_row[fi+5] = -1

                stupidcounter += 1
                if stupidcounter == 5:
                    add_to_fi += 1
                    stupidcounter = 0

        return G    

    def calc_obj(xM):
        # our objective is the sum of
        # the L2 norm of our position error away from 0.5
        # the L2 norm of our 4th derivative error away from 0
        obj_pos  = dt * np.sum( (xM[:,0] - 0.5)**2)
        obj_snap = dt * np.sum( (xM[:,4]      )**2)  
        objective = lambda_pos * obj_pos + lambda_snap * obj_snap
        return (objective, obj_pos, obj_snap)

    def calc_obstacle_constraints(xM):
        blend = xM[:,0]
        sigmaBlended = (blend[:,np.newaxis]*sigmaA + (1-blend)[:,np.newaxis]*sigmaB)
        constraintA = la.norm(sigmaBlended - personA, axis=1) - min_distA
        constraintB = la.norm(sigmaBlended - personB, axis=1) - min_distB
        return np.r_[constraintA, constraintB]

    def blend_test3_objFG(status,x,needF,needG,cu,iu,ru):

        xM = x.reshape(nsamples,ndims)

        objective, obj_pos, obj_snap = calc_obj(xM)

        # Evaluate the current continuity constraints
        continuity_x = np.zeros((nsamples, 5))
        for i in range(nsamples-1):
            si  = xM[i,0:5]
            vi  = xM[i,5  ]
            si1 = xM[i+1,0:5]
            continuity_x[i] = si + (M.dot(si) + N.dot(vi))*dt - si1
        continuity_x = np.matrix(continuity_x).A1

        obstacles = calc_obstacle_constraints(xM)

        F = np.concatenate(
            ([objective],
             continuity_x,
             obstacles))

        #G = grad_function(xM)

        return status, F#, G[G_nonzero_inds]

    # 4. Set up bounds on F
    # [ objectivec can be anything, equal-to-zero for continuity, greater-than-0 for obstacles along traj]
    low_F    = np.concatenate(([-inf], np.array([0,0,0,0,0]*nsamples), [0  , 0]*nsamples))
    upp_F    = np.concatenate(([ inf], np.array([0,0,0,0,0]*nsamples), [inf, inf]*nsamples))

    # Matrix uses fortran numbering or something
    ObjRow = 1

    # Set up the linear and nonlinear structure of the jacobian matrix
    xM = x0.reshape(nsamples,ndims)
    G = grad_function(xM,compute_nonzero_only=True, compute_linear=False)
    G_nonzero_inds           = G.nonzero()
    A = grad_function(xM,compute_nonzero_only=True, compute_linear=True)

    # Now we solve
    a = time.time()

    snopt.snopta(name='blend_test3',usrfun=blend_test3_objFG,x0=x0,xlow=xlow,xupp=xupp,
                 Flow=low_F,Fupp=upp_F,ObjRow=ObjRow)
    b = time.time()

    print "Solved in %.4fs" % (b - a)

    print "Value of objective function: %.8f" % snopt.F[0]
    print "   lambda_pos: %f, lambda_snap: %f, " % (lambda_pos, lambda_snap)
    print "   objective: %f, obj_pos: %f, obj_snap: %f" % calc_obj(xM)
    
    xM = snopt.x.reshape(nsamples, ndims)
    return (xM, snopt)


###############################################################################
# Here is a wrapper function around optimize_blending_function_between_two_distance_sigmas
###############################################################################
def real_optimizer_unconstrained_at_endpoints(u, sigma_i, sigma_j, i, j, min_dist_i, min_dist_j, params):

    xM, snopt = optimize_blending_function_between_two_distance_sigmas(
        sigma_i, sigma_j, i, j, min_dist_i, min_dist_j, params, constrain_at_endpoints=False)
    blend = xM[:,0]
    sigmaBlended = (blend[:,np.newaxis]*sigma_i + (1-blend)[:,np.newaxis]*sigma_j)
    
    return (blend, sigmaBlended)

###############################################################################
# Here is a wrapper function around optimize_blending_function_between_two_distance_sigmas
###############################################################################
def real_optimizer_constrained_at_endpoints(u, sigma_i, sigma_j, i, j, min_dist_i, min_dist_j, params):

    xM, snopt = optimize_blending_function_between_two_distance_sigmas(
        sigma_i, sigma_j, i, j, min_dist_i, min_dist_j, params, constrain_at_endpoints=True)
    blend = xM[:,0]
    sigmaBlended = (blend[:,np.newaxis]*sigma_i + (1-blend)[:,np.newaxis]*sigma_j)
    
    return (blend, sigmaBlended)

