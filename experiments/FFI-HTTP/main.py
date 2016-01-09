# Copyright (C) 2016 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#

from flask import Flask
from flask import jsonify, request, url_for, redirect, render_template, abort
server = Flask(__name__)
server.config.from_object('config')

@server.route('/')
def hello():
  return "Hello"

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

  # P_cameraPose = c_[cameraPose_lat_list, cameraPose_lng_list, cameraPose_alt_list]
  # C_cameraPose,T_cameraPose,sd_cameraPose,dist_cameraPose = trajectoryAPI.compute_spatial_trajectory_and_arc_distance(P_cameraPose, inNED=False)
  
  # data = {
  #   'cameraPoseCoeff': C_cameraPose.tolist(),
  #   'cameraPoseTvals': T_cameraPose.tolist(),
  #   'cameraPoseDist' : dist_cameraPose.tolist(),
  # }

  data = {
    'cameraPoseCoeff': [[0]],
    'cameraPoseTvals': [0],
    'cameraPoseDist' : [0],
  }

  return jsonify(data)


def main():
  print "Launching Python Foreign Function Interface over HTTP"
  server.run(debug = True)

if __name__ == "__main__":
  main()