# Copyright (C) 2016 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

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
  
  print "get_trajectory: Response from trajectoryAPI", P_interpolatedSpline

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
    personA: [x, y, z]
    personB: [x, y, z]
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

  # SA_1, SA_2
  screen_x_list = parsed_json['screenSpaceX']
  screen_y_list = parsed_json['screenSpaceY']
  person_n_list = parsed_json['personN']
  person_e_list = parsed_json['personE']
  person_d_list = parsed_json['personD']
  fov_list = parsed_json['fov']
  numTargets_list = parsed_json['numTargets']

  print "get_toric_trajectory: Calling trajectoryAPI now..."

  # toric interpolation

  # starting people positons
  PA_1 = toric.Vector3(personA_list[0],personA_list[1],personA_list[2])
  PB_1 = toric.Vector3(personB_list[0],personB_list[1],personB_list[2])

  # ending people positions: for the moment the positions are the same
  PA_2 = toric.Vector3(personA_list[0],personA_list[1],personA_list[2])
  PB_2 = toric.Vector3(personB_list[0],personB_list[1],personB_list[2])

  # Starting camera position is *outside* of PA_1:
  C_1 = toric.Vector3(cameraPose_n_list[0], cameraPose_e_list[0], cameraPose_d_list[0])
  C_2 = toric.Vector3(cameraPose_n_list[1], cameraPose_e_list[1], cameraPose_d_list[1])
  interpolated = toricinterpolation.toric_position_interpolation(C_1, PA_1, PB_1, C_2, PA_2, PB_2)

  print C_1
  print C_2

  P_cameraPose = interpolated['F']
  P_cameraOrient = toricinterpolation.toric_orientation_interpolation(P_cameraPose, SA_1, SB_1, SA_2, SB_2, PA_1, PB_1, PA_2, PB_2)

  print "P: ", P_cameraPose

  # scale
  P_cameraPose[:,0] *= 1000.0;
  P_cameraPose[:,1] *= 1000.0;
  P_cameraPose[:,2] *= -1000.0; 
  P_cameraOrient[:,0] *= 1000.0;
  P_cameraOrient[:,1] *= 1000.0;
  P_cameraOrient[:,2] *= -1000.0; 
  T_cameraPose = c_[interpolated['t'], interpolated['t'], interpolated['t']]

  P_positionSpline = trajectoryAPI.compute_easing_spline_trajectory(P_cameraPose, T_cameraPose)
  P_orientationSpline = trajectoryAPI.compute_easing_spline_trajectory(P_cameraOrient, T_cameraPose)
  
  print "get_toric_trajectory (position): Response from trajectoryAPI", P_positionSpline
  print "get_toric_trajectory (orientation): Response from trajectoryAPI", P_orientationSpline

  data = {
    'positionSpline': P_positionSpline.tolist(),
    'orientationSpline': P_orientationSpline.tolist(),
  }
  return jsonify(data)

@server.route('/get_orientation', methods = ['POST'])
def get_orientation():
  '''
  Send a POST request to this URL.

  Input: a JSON object as follows:
  {
    cameraPoseN: [0, ...],
    cameraPoseE: [0, ...],
    cameraPoseD: [0, ...],
    screenSpaceX: [0, ...],
    screenSpaceY: [0, ...],
    personN: [0, ...],
    personE: [0, ...],
    personD: [0, ...],
    fovX: [0, ...],
    fovY: [0, ...],
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

  # camera_list = parsed_json['camera']
  # screenA_list = parsed_json['screenSpaceA']
  # screenB_list = parsed_json['screenSpaceB']
  # personA_list = parsed_json['personA']
  # personB_list = parsed_json['personB']
  # fov_list = parsed_json['fov']
  cameraPose_n_list = parsed_json['cameraPoseN'] #y
  cameraPose_e_list = parsed_json['cameraPoseE'] #x
  cameraPose_d_list = parsed_json['cameraPoseD'] #z
  screen_x_list = parsed_json['screenSpaceX']
  screen_y_list = parsed_json['screenSpaceY']
  person_n_list = parsed_json['personN']
  person_e_list = parsed_json['personE']
  person_d_list = parsed_json['personD']
  fov_x_list = parsed_json['fovX']
  fov_y_list = parsed_json['fovY']

  print "get_toric_trajectory: Calling trajectoryAPI now..."

  # toric interpolation
  C = toric.Vector3(cameraPose_n_list[0],cameraPose_e_list[0],cameraPose_d_list[0])
  SA = toric.Vector2(screen_x_list[0],screen_y_list[0])
  PA = toric.Vector3(person_n_list[0],person_e_list[0],person_d_list[0])
  numTargets = len(screen_x_list)
  if (numTargets > 1):
    SB = toric.Vector2(screen_x_list[1],screen_y_list[1])
    PB = toric.Vector3(person_n_list[1],person_e_list[1],person_d_list[1])
  fovX = toric.RadianPi(fov_x_list[0])
  fovY = toric.RadianPi(fov_y_list[0])

  print "numTargets", numTargets

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