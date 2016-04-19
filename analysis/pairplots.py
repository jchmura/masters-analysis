import argparse
import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from tables_utils import group_by_type


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf5_file', help='Path to the HDF5 file', type=argparse.FileType())
    parser.add_argument('-t', '--table', help='Name of the table (default = %(default)s)',
                        default='DownstreamDebugTuple')

    args = parser.parse_args()

    dirname = 'pairplots'
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    hdf5_file = args.hdf5_file.name
    hdf = pd.HDFStore(hdf5_file)
    df = hdf.get('DownstreamDebugTuple')
    hdf.close()

    df = df.drop('seed_z', axis=1)
    for col in df.columns:
        if col != 'TT_hits' and col.startswith('TT') or col.startswith('OT') or col.startswith('IT'):
            df = df.drop(col, axis=1)

    # df.loc[df['seed_class'] == 1, 'seed_class'] = 'IT'
    # df.loc[df['seed_class'] == 2, 'seed_class'] = 'OT'
    # df.loc[df['seed_class'] == 3, 'seed_class'] = 'IT/OT'

    group_by_type(df)
    groups = df.groupby('type')

    columns = list(df.columns)
    columns.remove('type')
    columns.remove('seed_class')

    for x in columns:
        for y in columns:
            if x == y:
                continue

            dir = os.path.join(dirname, x)
            if not os.path.exists(dir):
                os.makedirs(dir)

            fig, ax = plt.subplots()
            sizes = [6, 4, 3]
            for i, (name, group) in enumerate(groups):
                ax.plot(group[x], group[y], marker='o', linestyle='', label=name, markersize=sizes[i])

            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.legend()
            plt.savefig('{}/{}.png'.format(dir, y))
            plt.close(fig)


if __name__ == '__main__':
    main()
