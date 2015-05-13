import argparse
import gzip
import os
import traceback
import pickle
from analyser import AnalyserEngine
from column_stats_analyser import ColumnStatsAnalyser
from complex_type_analyser import ComplexTypeAnalyser
import tablemagician
from multiprocessing import Process, Queue

__author__ = 'sebastian'

MAX_LINES = 200


def write_analyser_table_to_file(f, filename, out_dir, analyser_engine):
    data_tables = tablemagician.from_file_object(f, filename)
    for dt in data_tables:
        analyser_table = dt.process(max_lines=MAX_LINES)

        # feed with analyser table
        analyser_engine.process(analyser_table)

        # write analyser table in out dir
        out_path = os.path.join(out_dir, filename + '.pkl')
        with open(out_path, 'wb') as h:
            pickle.dump(analyser_table, h)
    dt.close()


def start_job(path, filename, out_dir, engine):
    try:
        # open file
        if path.endswith('.gz'):
            f = gzip.open(path, 'rb')
        else:
            f = open(path, 'rb')

        write_analyser_table_to_file(f, filename, out_dir, engine)

    except Exception as e:
        traceback.print_exc()
        print e


def main():
    parser = argparse.ArgumentParser(description='Read and write CSV analyser tables.')

    parser.add_argument('-r', help='read analyser tables in dir', action='store_true')
    parser.add_argument('-w', help='write analyser tables to dir', action='store_true')

    parser.add_argument('--dir', help='the directory of the CSV files/analyser tables')
    parser.add_argument('--out-dir', help='the destination dir for the stats')
    parser.add_argument('-pj', help='stop after a max number of files')
    args = parser.parse_args()

    if args.w:
        queue = []
        for subdir, dirs, files in os.walk(args.dir):
            for filename in files:
                file_path = os.path.join(args.dir, filename)
                queue.append((file_path, filename))

        a = ComplexTypeAnalyser()
        b = ColumnStatsAnalyser()

        analyser_chain = [a, b]
        # build engine
        engine = AnalyserEngine(analyser_chain)

        # TODO multiprocessing
        for path, filename in queue:
            start_job(path, filename, args.out_dir, engine)

    elif args.r:
        analyser_tables = []
        for subdir, dirs, files in os.walk(args.dir):
            for file in files:
                try:
                    filename = os.path.join(args.dir, file)
                    if filename.endswith('.pkl'):
                        with open(filename, 'rb') as f:
                            analyser_tables.append(pickle.load(f))
                except Exception as e:
                    traceback.print_exc()
                    print e
        print len(analyser_tables)
        for t in analyser_tables:
            print t


if __name__ == '__main__':
    main()