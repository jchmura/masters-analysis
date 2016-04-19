import argparse
import multiprocessing as mp
from collections import defaultdict

import numpy as np
import pandas as pd

from analysis.tables_utils import Columns


def _get_table(hdf5_file, table_name):
    hdf = pd.HDFStore(hdf5_file, mode='r')
    df = hdf.select(table_name)
    hdf.close()
    return df


def _save_table(hdf5_file, table, table_name):
    hdf = pd.HDFStore(hdf5_file)
    hdf.put(table_name, table, format='table')
    hdf.close()


class HitCounter:
    def __init__(self, table, columns, parts=4):
        self.table = table
        self.parts = parts
        self.layers = columns.layers
        self.layer_to_subposition = columns.layer_to_subposition

    def count_in_detector(self, row):
        d1 = defaultdict(int)
        d2 = defaultdict(int)
        for layer in self.layers:
            d1[self.layer_to_subposition[layer]] += row[layer]
        for k, v in d1.items():
            if v > 0:
                if k.startswith('TT'):
                    d2['TT_hits'] += 1
                else:
                    d2['seed_hits'] += 1
        return pd.Series(d2)

    def process(self, df):
        return df[self.layers].apply(self.count_in_detector, axis=1)

    def count(self):
        pool = mp.Pool(processes=self.parts)
        split_dfs = np.array_split(self.table, self.parts)
        pool_results = pool.map(self.process, split_dfs)
        pool.close()
        pool.join()

        return pd.concat(pool_results, axis=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count TT and seed hits in DataFrame')
    parser.add_argument('hdf5_file', help='Path to the HDF5 file', type=argparse.FileType())
    parser.add_argument('-t', '--table', help='Name of the table (default = %(default)s)',
                        default='DownstreamDebugTuple')
    parser.add_argument('-o' '--output', help='Output file with extended table')
    parser.add_argument('-p', '--parts', type=int,
                        help='Parts the input table will be divided into to speedup processing', default=4)

    args = parser.parse_args()

    hdf5_file = args.hdf5_file.name
    table = _get_table(hdf5_file, args.table)
    columns = Columns(hdf5_file, args.table)
    counter = HitCounter(table, columns, args.parts)
    counted = counter.count()
    df = pd.concat([table, counted], axis=1)

    if 'output' in args:
        output = args.output
    else:
        output = '{}_extended.{}'.format(hdf5_file[:hdf5_file.rindex('.')],
                                         hdf5_file[hdf5_file.rindex('.') + 1:])

    _save_table(output, df, args.table)
