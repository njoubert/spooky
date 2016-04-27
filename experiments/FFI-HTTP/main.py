#################################################
# IMPORTS
#################################################

# Globally useful stuff
import os, inspect, sys
from sets import Set

# Web server stuff
from flask import Flask
from flask import jsonify, request, url_for, redirect, render_template, abort
server = Flask(__name__)
server.config.from_object('config')

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

#################################################
# WEB SERVER ENDPOINTS
#################################################

@server.route('/')
def hello():
  return "Hello"

@server.route('/test_post', methods = ['POST'])
def test_post():
  parsed_json = request.get_json()

  print parsed_json

  return jsonify({
      'result':'happy',
      'your_post': parsed_json
    })

@server.route('/get_spline', methods = ['POST'])
def get_spline():
  '''
  Send a POST request to this URL.

  Input: a JSON object as follows:
    {
      cameraPoseN: [0, ...],
      cameraPoseE: [0, ...],
      cameraPoseD: [0, ...],
    }

  Returns: a JSON object as follows:
  {
    cameraPoseCoeff: [[c0, c1,...], [c0, c1, ...]],
    cameraPoseTvals: [...],
    cameraPoseDist:  [...],
  }
  '''
  parsed_json = request.get_json()
  if parsed_json is None:
    return abort(400)

  cameraPose_lat_list = parsed_json['cameraPoseLats']
  cameraPose_lng_list = parsed_json['cameraPoseLngs']
  cameraPose_alt_list = parsed_json['cameraPoseAlts']

  print "get_spline: Calling trajectoryAPI now..."
  
  P_cameraPose = c_[cameraPose_lat_list, cameraPose_lng_list, cameraPose_alt_list]
  C_cameraPose,T_cameraPose,sd_cameraPose,dist_cameraPose = trajectoryAPI.compute_spatial_trajectory_and_arc_distance(P_cameraPose, inNED=False)
  
  print "get_spline: Response from trajectoryAPI", C_cameraPose

  data = {
    'cameraPoseCoeff': C_cameraPose.tolist(),
    'cameraPoseTvals': T_cameraPose.tolist(),
    'cameraPoseDist' : dist_cameraPose.tolist(),
  }

  return jsonify(data)


@server.route('/get_trajectory', methods = ['POST'])
def get_trajectory():
  '''
  Send a POST request to this URL.

  Input: a JSON object as follows:
  {
    cameraPoseN: [0, ...],
    cameraPoseE: [0, ...],
    cameraPoseD: [0, ...],
    cameraPoseT: [0, ...],
  }

  Returns: a JSON object as follows:
  {
    interpolatedSpline: [...],
  }
  '''
  parsed_json = request.get_json()
  if parsed_json is None:
    return abort(400)

  cameraPose_n_list = parsed_json['cameraPoseN']
  cameraPose_e_list = parsed_json['cameraPoseE']
  cameraPose_d_list = parsed_json['cameraPoseD']
  cameraPose_t_list = parsed_json['cameraPoseT']

  print "get_trajectory: Calling trajectoryAPI now..."
  
  P_cameraPose = c_[cameraPose_n_list, cameraPose_e_list, cameraPose_d_list]
  T_cameraPose = c_[cameraPose_t_list, cameraPose_t_list, cameraPose_t_list]

  print "P: ", P_cameraPose

  P_interpolatedSpline = trajectoryAPI.compute_easing_spline_trajectory(P_cameraPose, T_cameraPose)
  
  #print "get_trajectory: Response from trajectoryAPI", P_interpolatedSpline

  data = {
    'interpolatedSpline': P_interpolatedSpline.tolist(),
  }
  return jsonify(data)

@server.route('/get_toric_trajectory', methods = ['POST'])
def get_toric_trajectory():
  '''
  Send a POST request to this URL.

  Input: a JSON object as follows:
  {
    cameraPoseN: [0, ...],
    cameraPoseE: [0, ...],
    cameraPoseD: [0, ...],
    cameraPoseT: [0, ...],
    personA: [x, y, z, ...]
    personB: [x, y, z, ...]
    screenSpaceA : [x, y, ...]
    screenSpaceB : [x, y, ...]
  }

  Returns: a JSON object as follows:
  {
    interpolatedSpline: [...],
  }
  '''
  parsed_json = request.get_json()
  if parsed_json is None:
    return abort(400)

  cameraPose_n_list = parsed_json['cameraPoseN'] #y
  cameraPose_e_list = parsed_json['cameraPoseE'] #x
  cameraPose_d_list = parsed_json['cameraPoseD'] #z
  cameraPose_t_list = parsed_json['cameraPoseT']
  personA_list = parsed_json['personA']
  personB_list = parsed_json['personB']
  screenSpaceA_list = parsed_json['screenSpaceA']
  screenSpaceB_list = parsed_json['screenSpaceB']

  print "get_toric_trajectory: Calling trajectoryAPI now..."

  # toric interpolation

  # people positons
  PA_1 = toric.Vector3(personA_list[0],personA_list[1],personA_list[2])
  PB_1 = toric.Vector3(personB_list[0],personB_list[1],personB_list[2])
  PA_2 = toric.Vector3(personA_list[0],personA_list[1],personA_list[2]) # ending people positions: for the moment the positions are the same
  PB_2 = toric.Vector3(personB_list[0],personB_list[1],personB_list[2])

  # camera positions
  C_1 = toric.Vector3(cameraPose_n_list[0], cameraPose_e_list[0], cameraPose_d_list[0])
  C_2 = toric.Vector3(cameraPose_n_list[1], cameraPose_e_list[1], cameraPose_d_list[1])

  # screen space positions
  SA_1 = toric.Vector2(screenSpaceA_list[0], screenSpaceA_list[1])
  SB_1 = toric.Vector2(screenSpaceB_list[0], screenSpaceB_list[1])
  SA_2 = toric.Vector2(screenSpaceA_list[2], screenSpaceA_list[3])
  SB_2 = toric.Vector2(screenSpaceB_list[2], screenSpaceB_list[3])

  interpolated = toricinterpolation.toric_position_interpolation(C_1, PA_1, PB_1, C_2, PA_2, PB_2)

  print C_1
  print C_2

  P_cameraPose = interpolated['F']
  #orientInterpolated = toricinterpolation.toric_orientation_interpolation(P_cameraPose, SA_1, SB_1, SA_2, SB_2, PA_1, PB_1, PA_2, PB_2)

  print "P: ", P_cameraPose
  T_cameraPose = c_[interpolated['t'], interpolated['t'], interpolated['t']]
  P_positionSpline = trajectoryAPI.compute_easing_spline_trajectory(P_cameraPose, T_cameraPose)
  
  #print "get_toric_trajectory (position): Response from trajectoryAPI", P_positionSpline
  #print "get_toric_trajectory (orientation): Response from trajectoryAPI", P_orientationSpline

  data = {
    'positionSpline': P_positionSpline.tolist(),
    #'orientationSpline': P_orientationSpline.tolist(),
  }
  return jsonify(data)

@server.route('/get_optimized_blended_spherical_trajectory', methods = ['POST'])
def get_optimized_blended_spherical_trajectory():
  '''
  Send a POST request to this URL.

  Input: a JSON object as follows:
  {
    cameraPoseN: [0, ...],
    cameraPoseE: [0, ...],
    cameraPoseD: [0, ...],
    cameraPoseT: [0, ...],
    personA: [x, y, z, ...],
    personB: [x, y, z, ...],
    screenSpaceA : [x, y, ...],
    screenSpaceB : [x, y, ...],
    params: {
      minDist: 1
    }
  }

  Returns: a JSON object as follows:
  {
    positionSpline: [...],
  }
  '''

  parsed_json = request.get_json()
  if parsed_json is None:
    return abort(400)

  cameraPose_n_list = parsed_json['cameraPoseN'] #y
  cameraPose_e_list = parsed_json['cameraPoseE'] #x
  cameraPose_d_list = parsed_json['cameraPoseD'] #z
  cameraPose_t_list = parsed_json['cameraPoseT']
  screenSpaceA_list = parsed_json['screenSpaceA']
  screenSpaceB_list = parsed_json['screenSpaceB']

  PA = np.array(parsed_json['personA'])
  PB = np.array(parsed_json['personB'])

  C0 = np.array([cameraPose_n_list[0], cameraPose_e_list[0], cameraPose_d_list[0]])
  C1 = np.array([cameraPose_n_list[1], cameraPose_e_list[1], cameraPose_d_list[1]])

  params = parsed_json['params']

  print "get_optimized_blended_spherical_trajectory: Calling optimizer now..."
  print "  PA is", PA
  print "  PB is", PB
  print "  C0 is", C0
  print "  C1 is", C1
  print "  params is:", params

  
  sigma, wA, sigmaAvg, sigmaA, sigmaB, t = osp.calculate_position_trajectory_as_optimized_blend_of_spherical_trajectories(
    PA, PB, C0, C1, osp.real_optimizer_unconstrained_at_endpoints, params)

  print "Parameterizing returned sigma trajectory over time..."

  P_cameraPose = sigma

  print "P: ", P_cameraPose
  T_cameraPose = c_[t, t, t]
  P_positionSpline = trajectoryAPI.compute_easing_spline_trajectory(P_cameraPose, T_cameraPose, num_timesteps=100)

  data = {
    'positionSpline': P_positionSpline.tolist(),
  }
  return jsonify(data)
  

@server.route('/get_orientation', methods = ['POST'])
def get_orientation():
  '''
  Send a POST request to this URL.

  Input: a JSON object as follows:
  {
    camera: [x, y, z]
    screenSpaceA: [x, y]
    screenSpaceB: [x, y]
    personA: [x, y, z]
    personB: [x, y, z]
    fov: [x, y]
    numTargets: 1 or 2
  }

  Returns: a JSON object as follows:
  {
    'w': w
    'x': x
    'y': y
    'z': z
  }
  '''
  parsed_json = request.get_json()
  if parsed_json is None:
    return abort(400)

  camera_list = parsed_json['camera']
  screenA_list = parsed_json['screenSpaceA']
  screenB_list = parsed_json['screenSpaceB']
  personA_list = parsed_json['personA']
  personB_list = parsed_json['personB']
  fov_list = parsed_json['fov']
  numTargets_list = parsed_json['numTargets']

  print "get_toric_trajectory: Calling trajectoryAPI now..."

  # toric interpolation

  numTargets = numTargets_list[0]
  C = toric.Vector3(camera_list[0],camera_list[1],camera_list[2])
  SA = toric.Vector2(screenA_list[0],screenA_list[1])
  PA = toric.Vector3(personA_list[0],personA_list[1],personA_list[2])
  SB = toric.Vector2(screenB_list[0],screenB_list[1])
  PB = toric.Vector3(personB_list[0],personB_list[1],personB_list[2])
  fovX = toric.RadianPi(fov_list[0])
  fovY = toric.RadianPi(fov_list[1])

  q = toricinterpolation.toric_orientation(C, SA, SB, PA, PB, fovX, fovY, numTargets)
  
  print "get_orientation: Response from trajectoryAPI [w: ", q['w'], ", x: ", q['x'], ", y: ", q['y'], ", z: ", q['z']

  data = {
    'w': q['w'],
    'x': q['x'],
    'y': q['y'],
    'z': q['z']
  }

  return jsonify(data)

#################################################
# OTHER STUFF
#################################################

def main():
  print "Launching Python Foreign Function Interface over HTTP"
  server.run(debug = True)

if __name__ == "__main__":
  main()