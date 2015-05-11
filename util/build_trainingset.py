from __future__ import print_function
import os
import traceback
import tablemagician
from collections import defaultdict
import gzip
import shutil

__author__ = 'sebastian'
rootdir = '/home/sebastian/Repositories/csvprofiler/parser/testdata/nuts'


def header_frequency():
    header = defaultdict(int)
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filename = os.path.join(rootdir, file)
                # unzip files
                if filename.endswith('.gz'):
                    f = gzip.open(filename, 'rb')
                else:
                    f = open(filename, 'rb')
                if f:
                    datatables = tablemagician.from_file_object(f, file)
                    for dt in datatables:
                        for h in dt.headers:
                            header[h.lower().strip()] += 1
                    f.close()
            except Exception as e:
                print(file + ' - ' + str(e))
                print(traceback.format_exc())

    with open('header_frequency.csv', 'w') as f:
        for l in sorted(header, key=header.get, reverse=True):

            try:
                print(l + ',' + str(header[l]), file=f)
            except Exception as e:
                print(str(e))
                print(traceback.format_exc())


def build_by_header(header_set, dest_dir):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filename = os.path.join(rootdir, file)
                # unzip files
                if filename.endswith('.gz'):
                    f = gzip.open(filename, 'rb')
                    datatables = tablemagician.from_file_object(f, file)
                    for dt in datatables:
                        intersec = set(header_set) & set([h.lower() for h in dt.headers])
                        if intersec > 0:
                            train_dir = os.path.join(dest_dir, intersec.pop())
                            if not os.path.exists(train_dir):
                                os.mkdir(train_dir)
                            shutil.copyfile(filename, os.path.join(train_dir, file))
            except Exception as e:
                print(file + ' - ' + str(e))
                print(traceback.format_exc())

if __name__ == '__main__':
    header_frequency()