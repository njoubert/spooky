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

add_import_search_dir('../../../Frankencopter/Code/flashlight')
add_import_search_dir('../../src/spooky')

from coords import *
from splineutils import *
from curveutils import *
from quadrotorcamera3d import *


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

  P_cameraPose = c_[cameraPose_lat_list, cameraPose_lng_list, cameraPose_alt_list]
  C_cameraPose,T_cameraPose,sd_cameraPose,dist_cameraPose = trajectoryAPI.compute_spatial_trajectory_and_arc_distance(P_cameraPose, inNED=False)
  
  data = {
    'cameraPoseCoeff': C_cameraPose.tolist(),
    'cameraPoseTvals': T_cameraPose.tolist(),
    'cameraPoseDist' : dist_cameraPose.tolist(),
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