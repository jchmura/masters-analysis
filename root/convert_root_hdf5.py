from __future__ import print_function
import argparse

import pandas as pd
from rootpy.root2hdf5 import root2hdf5

parser = argparse.ArgumentParser(description='Convert ntuple from ROOT file to hdf5 store')
parser.add_argument('root_file', type=argparse.FileType(), help='Path to the ROOT file')
parser.add_argument('-i', '--input', help='Input tuple (default: %(default)s)', default='/ToolSvc.PatDebugTTTruthTool/DownstreamDebugTuple')
parser.add_argument('-o', '--output', help='Output table in hdf5 (default: %(default)s)', default='DownstreamDebugTuple')

args = parser.parse_args()

input_filename = args.root_file.name
output_filename = input_filename[:input_filename.rindex('.root')] + '.h5'

print('Converting {} to {}'.format(input_filename, output_filename))

rpath = ''
if '/' in args.input[1:]:
    rpath = args.input[:args.input.rindex('/')]

root2hdf5(input_filename, output_filename, rpath)

hdf = pd.HDFStore(output_filename)
table = hdf.get(args.input)
hdf.put(args.output, table, 'table')
hdf.remove(args.input)
hdf.close()
