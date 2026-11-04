"""Temporary micro-benchmark for RepeatedContainer.remove() (not for upstream)."""

import argparse
import timeit

from google.protobuf import unittest_pb2
from google.protobuf.internal import api_implementation

parser = argparse.ArgumentParser()
parser.add_argument('--label', default='')
args = parser.parse_args()

N_SCALAR = 1000
N_COMPOSITE = 200

scalar = unittest_pb2.TestAllTypes()
scalar.repeated_int32.extend(range(N_SCALAR))
composite = unittest_pb2.TestAllTypes()
for i in range(N_COMPOSITE):
  composite.repeated_nested_message.add(bb=i)
last_msg = unittest_pb2.TestAllTypes.NestedMessage(bb=N_COMPOSITE - 1)
missing_msg = unittest_pb2.TestAllTypes.NestedMessage(bb=-1)


def scalar_miss():
  try:
    scalar.repeated_int32.remove(-1)
  except ValueError:
    pass


def scalar_hit_last():
  scalar.repeated_int32.remove(N_SCALAR - 1)
  scalar.repeated_int32.append(N_SCALAR - 1)


def composite_miss():
  try:
    composite.repeated_nested_message.remove(missing_msg)
  except ValueError:
    pass


def composite_hit_last():
  composite.repeated_nested_message.remove(last_msg)
  composite.repeated_nested_message.add(bb=N_COMPOSITE - 1)


for name, fn, n_elems, number in [
    ('scalar_miss', scalar_miss, N_SCALAR, 2000),
    ('scalar_hit_last', scalar_hit_last, N_SCALAR, 2000),
    ('composite_miss', composite_miss, N_COMPOSITE, 500),
    ('composite_hit_last', composite_hit_last, N_COMPOSITE, 500),
]:
  best = min(timeit.repeat(fn, number=number, repeat=15)) / number
  print('BENCH %s impl=%s %s %.2f us/call %.1f ns/elem' % (
      args.label, api_implementation.Type(), name, best * 1e6,
      best * 1e9 / n_elems))
