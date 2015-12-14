# Copyright (C) 2015 Stanford University
# Contact: Niels Joubert <niels@cs.stanford.edu>
#
 
EXCLUDE = ['sender', 'msg_type', 'crc', 'length', 'preamble', 'payload']

def exclude_fields(obj, exclude=EXCLUDE):
  """
  Return dict of object without parent attrs.
  """
  return dict([(k, getattr(obj, k)) for k in obj.__slots__ if k not in exclude])

def fmt_dict(obj):
  return dict((k, v) for k, v in exclude_fields(obj).items())
