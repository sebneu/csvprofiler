import decimal
import io
import time
import sys
import os
import traceback
import tablemagician
from collections import defaultdict, Counter
import gzip
import argparse
import shutil

__author__ = 'sebastian'
MAX_ROWS = 50


def arg_parser():
    parser = argparse.ArgumentParser(description='Collect stats about a folder of csv files.')
    parser.add_argument('-i', '--in-dir', help='in directory of files', default='/data/csv')
    parser.add_argument('-o', '--out-dir', help='out directory for files', default='.')
    parser.add_argument('--filter', help='filter files and copy to other directory', action='store_true')

    args = parser.parse_args()
    return args


def type_classification(header_types, column_types):
    cols = len(header_types)
    strings = 0
    ints = 0
    decimals = 0
    bools = 0

    for t in header_types:
        if t == basestring:
            column_types['string'] += 1
            strings += 1
        elif t == int:
            column_types['int'] += 1
            ints += 1
        elif t == decimal.Decimal:
            column_types['decimal'] += 1
            decimals += 1
        elif t == bool:
            column_types['bool'] += 1
            bools += 1

    if cols <= strings + 1:
        return 'all_string'
    elif cols <= ints + 1:
        return 'all_ints'
    elif cols <= decimals + 1:
        return 'all_decimals'
    elif cols <= bools + 1:
        return 'all_bools'
    if cols/2.0 < strings:
        return 'mth_string'
    elif cols/2.0 < ints:
        return 'mth_ints'
    elif cols/2.0 < decimals:
        return 'mth_decimals'
    elif cols/2.0 < bools:
        return 'mth_bools'

    counter = Counter(header_types)
    t = counter.most_common(1)[0]

    if t == basestring:
        return 'mainly_string'
    elif t == int:
        return 'mainly_ints'
    elif t == decimal.Decimal:
        return 'mainly_decimals'
    elif t == bool:
        return 'mainly_bools'

    return 'unknown'


def filter_out_files(rootdir, outdir):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filename = os.path.join(rootdir, file)
                # unzip files
                if filename.endswith('.gz'):

                    f = gzip.open(filename, 'rb')
                    # count all lines
                    number_lines = sum(1 for _ in f)
                    f.close()

                    # open again after iteration
                    f = gzip.open(filename, 'rb')
                    # read first rows of table
                    tables = tablemagician.from_file_object(f, filename)
                    for table in tables:
                        #analyser_table = table.process(max_lines=MAX_ROWS)

                        # columns
                        num_of_columns = len(table.headers)
                        # types
                        types = [t.result_type for t in table.types]

                        # filter criteria, bigger sized tables
                        if number_lines > 50 and num_of_columns > 6:
                            if len(types) == types.count(basestring):
                                # pure string tables
                                str_dir = os.path.join(outdir, 'all_string')
                                if not os.path.exists(str_dir):
                                    os.mkdir(str_dir)
                                shutil.copyfile(filename, os.path.join(str_dir, file))
                            elif basestring in types and (types.count(int) + types.count(decimal.Decimal)) >= len(types)/2:
                                # containing a string column and multiple numerical columns
                                num_dir = os.path.join(outdir, 'some_numeric')
                                if not os.path.exists(num_dir):
                                    os.mkdir(num_dir)
                                shutil.copyfile(filename, os.path.join(num_dir, file))

                    table.close()
            except Exception as e:
                traceback.print_exc()
                print e


def main():
    args = arg_parser()

    rootdir = args.in_dir
    outdir = args.out_dir

    if args.filter:
        filter_out_files(rootdir, outdir)

    num_of_rows = defaultdict(int)
    num_of_columns = defaultdict(int)
    header = defaultdict(int)
    types = defaultdict(int)
    column_types = defaultdict(int)

    start = time.time()
    row_counting_time = 0

    i = 0
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filename = os.path.join(rootdir, file)

                # unzip files
                if filename.endswith('.gz'):

                    f = gzip.open(filename, 'rb')
                    # count all lines
                    start_row_counting = time.time()
                    number_lines = sum(1 for _ in f)
                    end_row_counting = time.time()
                    row_counting_time += end_row_counting - start_row_counting
                    num_of_rows[number_lines] += 1
                    f.close()


                    # open again after iteration
                    f = gzip.open(filename, 'rb')
                    # read first rows of table
                    tables = tablemagician.from_file_object(f, filename)
                    for table in tables:
                        #analyser_table = table.process(max_lines=MAX_ROWS)

                        # columns
                        num_of_columns[len(table.headers)] += 1
                        # header
                        for h in table.headers:
                            header[h.lower()] += 1

                        table_type = type_classification([t.result_type for t in table.types], column_types)
                        types[table_type] += 1
                    table.close()
                    i += 1
            except Exception as e:
                traceback.print_exc()
                print e

            if i % 100 == 0:
                print i, 'files processed'

    with open('rows.csv', 'wb') as f:
        f.write('rows,count\n')
        for r in sorted(num_of_rows, key=num_of_rows.get, reverse=True):
            f.write(str(r) + ',' + str(num_of_rows[r]) + '\n')

    with open('columns.csv', 'wb') as f:
        f.write('columns,count\n')
        for r in sorted(num_of_columns, key=num_of_columns.get, reverse=True):
            f.write(str(r) + ',' + str(num_of_columns[r]) + '\n')

    with io.open('header.csv', 'wt') as f:
        f.write(u'header,count\n')
        for r in sorted(header, key=header.get, reverse=True):
            try:
                f.write(unicode(r) + ',' + unicode(header[r]) + u'\n')
            except Exception as e:
                print e

    with open('types.csv', 'wb') as f:
        f.write('type,count\n')
        for r in sorted(types, key=types.get, reverse=True):
            f.write(str(r) + ',' + str(types[r]) + '\n')

    with open('column_types.csv', 'wb') as f:
        f.write('column_type,count\n')
        for r in sorted(column_types, key=column_types.get, reverse=True):
            f.write(str(r) + ',' + str(column_types[r]) + '\n')

    end = time.time()
    print 'total time:', end - start
    print 'row counting time:', row_counting_time


if __name__ == '__main__':
    main()