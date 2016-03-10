# Copyright (C) 2016 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#


'''

Produces graphs of 

'''

import matplotlib
matplotlib.use('Agg') # Makes it save to files

import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from matplotlib import gridspec

import numpy as np

import cPickle as pickle
import json
import copy
import pprint

from os import listdir
from os.path import join, splitext, isfile


'''
Setting up Tableau Colors. 
http://tableaufriction.blogspot.ca/2012/11/finally-you-can-use-tableau-data-colors.html
'''
t10 = np.array([[31,119,180],[255,127,14],[44,160,44],[214,39,40],[148,103,189]])
t10 = t10/255.0

t10l = np.array([[174,199,232],[255,187,120],[152,223,138],[255,152,150],[197,176,213]])
t10l = t10l/255.0

# =============================================================================

def loadLog(logfile, startTime=0.0, endTime=-1.0):
    '''
    Load a logfile into an array of json objects.
    '''
    log = []
    with open(logfile, 'rb') as f:
        
        try:
            if startTime > 0.0:
                state = pickle.load(f)
                firstStamp = state['_timestamp']
                while (state['_timestamp'] - firstStamp) <= startTime:
                    state = pickle.load(f)
        except EOFError:
            print "Specified start point beyond end of file"
            sys.exit(0)

        try:
            while True:
                state = pickle.load(f)
                if state['_timestamp'] <= 0.0:
                    print "Faulty timestamp, ignoring"
                elif endTime > 0.0 and state['_timestamp'] - firstStamp > endTime:
                    return log
                else:
                    log.append(state)
        except EOFError:
            pass
        finally:
            return log


# =============================================================================


def walk_key_tree(tree, i=0, sofar=[], accum=[]):
    '''
    given a tree where every level's children has the same structure,
    in the form of an array of arrays [[node1, node2], [node3, node4] etc]
    flatten this into an array of depth-first paths through the tree
    '''
    if i >= len(tree):
        accum += [sofar]
    else:
        for c in tree[i]:
            walk_key_tree(tree, i+1, sofar + [c])
    return accum
        

def dict_append_with_array(d, key_sequence, value):
    for i in range(len(key_sequence)-1):
        k = key_sequence[i]
        if not k in d:
            d[k] = {}
        d = d[k]
    if not key_sequence[-1][0] in d:
        d[key_sequence[-1][0]] = np.array([])
    d[key_sequence[-1][0]] = np.append(d[key_sequence[-1][0]], value / key_sequence[-1][1])

def dict_get_with_array(d, key_sequence):
    for i in range(len(key_sequence)-1):
        d = d[key_sequence[i]]
    return d[key_sequence[-1][0]]

def AoS2SoA(AoS, key_sequences):
    ''' assumed indices have a repeated structure, where at every level i select a set of'''
    struct = {}
    for state in AoS:
      for sequence in key_sequences:
        try:
            val = dict_get_with_array(state, sequence)
            dict_append_with_array(struct, sequence, val)
        except KeyError:
          # NJ HACK: We're filling in missing data with a blank. that seems silly.
          dict_append_with_array(struct, sequence, 0)
    
    return struct


# =============================================================================

pylab.rcParams['figure.figsize'] = 8, 8
def extractAndDrawIconicTrajectory(figure, log, title):
    '''
    Here we extract one nice image of the trajectory, to show us what it looks like.
    '''    
    
    key_tree = [["192.168.2.51","192.168.2.52"], ["MsgBaselineNED"], [("tow", 1), ("n", 1000.), ("e", 1000.), ("d", 1000.), ("flags", 1), ("n_sats",1)]]            
    key_sequences = walk_key_tree(key_tree)    
    traj_SoA = AoS2SoA(log, key_sequences)
    
    n1 = traj_SoA["192.168.2.51"]["MsgBaselineNED"]["n"]
    e1 = traj_SoA["192.168.2.51"]["MsgBaselineNED"]["e"]
    d1 = traj_SoA["192.168.2.51"]["MsgBaselineNED"]["d"]
    fl1 = traj_SoA["192.168.2.51"]["MsgBaselineNED"]["flags"]
    ns1 = traj_SoA["192.168.2.51"]["MsgBaselineNED"]["n_sats"]
    
    n2 = traj_SoA["192.168.2.52"]["MsgBaselineNED"]["n"]
    e2 = traj_SoA["192.168.2.52"]["MsgBaselineNED"]["e"]
    d1 = traj_SoA["192.168.2.52"]["MsgBaselineNED"]["d"]
    fl2 = traj_SoA["192.168.2.52"]["MsgBaselineNED"]["flags"]
    ns2 = traj_SoA["192.168.2.52"]["MsgBaselineNED"]["n_sats"]
    
    
    # Calculate limits
    nmin = np.min([n1,n2])
    nmax = np.max([n1,n2])
    nmid = (nmax + nmin)/2.0

    emin = np.min([e1,e2])
    emax = np.max([e1,e2])
    emid = (emax + emin)/2.0

    nemin = np.min([n1,n2,e1,e2])
    nemax = np.max([n1,n2,e1,e2])
    nediff2 = (nemax - nemin)/2.0

    elim = (emid-nediff2,emid+nediff2)
    nlim = (nmid-nediff2,nmid+nediff2)

    # Colors and Legends
    p1_color_fixed = t10[2]
    p1_color_float = t10l[2]
    p2_color_fixed = t10[3]
    p2_color_float = t10l[3]
    
    p1_fixed = mpatches.Patch(color=p1_color_fixed, label="P1 Fixed")
    p2_fixed = mpatches.Patch(color=p2_color_fixed, label="P2 Fixed")
    p1_float = mpatches.Patch(color=p1_color_float, label="P1 Float")
    p2_float = mpatches.Patch(color=p2_color_float, label="P2 Float")
    
    cmap_flags1 = matplotlib.colors.ListedColormap([p1_color_float, p1_color_fixed], name="niels_simple")
    cmap_flags2 = matplotlib.colors.ListedColormap([p2_color_float, p2_color_fixed], name="niels_simple")

    
    # Figure 1: Trajectory with Fix
    
    figure.set_title("Trajectory for %s" % title)
    figure.set_xlabel("East (meters)")
    figure.set_ylabel("North (meters)")
    figure.set_aspect('equal')
    figure.set_xlim(elim)
    figure.set_ylim(nlim)
    figure.axhline(0, color=(1,0,0,0.4))
    figure.axvline(0, color=(1,0,0,0.4))
    figure.scatter(e1, n1, c=fl1, cmap=cmap_flags1, vmin=0, vmax=1.0, s=10, linewidths=0.1)
    figure.scatter(e2, n2, c=fl2, cmap=cmap_flags2, vmin=0, vmax=1.0, s=10, linewidths=0.1)
    figure.grid(b=True, which='both')
    figure.legend(handles=[p1_fixed,p1_float,p2_fixed,p2_float])


# =============================================================================

def find_logs(p="/Users/njoubert/Code/spooky/logs/", only_new=True):
  all_logs = [f for f in listdir(p) if isfile(join(p, f)) and splitext(f)[1] == ".pickle"]

  if only_new:
    return [f for f in all_logs if not(isfile(join(p, splitext(f)[0] + ".iconic.png")))]
  return all_logs

def save_iconic_trajectory(log, filename):
  gs = gridspec.GridSpec(1, 1) 
  fig = plt.figure()
  f1 = fig.add_subplot(gs[0])

  extractAndDrawIconicTrajectory(f1, log, filename)

  plt.savefig(splitext(filename)[0] + ".iconic.png")

def process_new():
  logs = find_logs(only_new=True)

  for filename in logs:
    try:
      print "Processing", filename
      l = loadLog(filename)
      save_iconic_trajectory(l, filename)
    except KeyboardInterrupt:
      sys.exit(0)
    except Exception:
      import traceback
      traceback.print_exc()

  logs = find_logs(only_new=False)
  with open("ICONS.md", "w") as f:
    for filename in logs:
      noext = splitext(filename)[0]
      f.write("![%s](https://raw.githubusercontent.com/njoubert/spooky/master/logs/%s)\n" % (noext, noext + ".iconic.png"))


def main():
  process_new()






if __name__ == '__main__':
  main()


    