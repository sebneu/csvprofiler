from __future__ import print_function
import os
import traceback
import tablemagician
import gzip
import shutil
import sys
from os import listdir
from os.path import isfile, join
import pickle
import threading


MAX_LINES = 100

__author__ = 'sebastian'

def build_by_header(header_set, rootdir, dest_dir):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filename = os.path.join(rootdir, file)
                # unzip files
                if filename.endswith('.gz'):
                    f = gzip.open(filename, 'rb')
                else:
                    f = open(filename, 'rb')
                datatables = tablemagician.from_file_object(f, file)
                for dt in datatables:
                    intersec = set(header_set) & set([h.lower().strip() for h in dt.headers])
                    if len(intersec) > 0:
                        train_dir = os.path.join(dest_dir, intersec.pop())
                        if not os.path.exists(train_dir):
                            os.mkdir(train_dir)
                        shutil.copyfile(filename, os.path.join(train_dir, file))
                f.close()
            except Exception as e:
                print(file + ' - ' + str(e))
                print(traceback.format_exc())


def read_files(path, d):
    train_set = []
    train_dir = join(path, d)
    onlyfiles = [join(train_dir, file) for file in listdir(train_dir) if isfile(join(train_dir, file))]
    for filename in onlyfiles:
        try:
            # unzip files
            if filename.endswith('.gz'):
                f = gzip.open(filename, 'rb')
            else:
                f = open(filename, 'rb')
            datatables = tablemagician.from_file_object(f, filename)
            for dt in datatables:
                analyser_table = dt.process(max_lines=MAX_LINES)
                for i, h in enumerate(analyser_table.headers):
                    if d == h.lower().strip():
                        train_set.append({'values': analyser_table.columns[i], 'name': filename})
            f.close()
        except Exception as e:
            print(filename + ' - ' + str(e))
            print(traceback.format_exc())
    with open(join(path, d + '.pkl'), 'wb') as handle:
        pickle.dump(train_set, handle)


if __name__ == '__main__':
    if sys.argv[1] == '-train-sets':
        path = sys.argv[2]
        headers = sys.argv[3:]
        for h in headers:
            thread = threading.Thread(target=read_files, args=(path, h))
            thread.start()
    elif len(sys.argv) >= 7 and sys.argv[1] == '-d' and sys.argv[3] == '-b' and sys.argv[5] == '-s':
        directory = sys.argv[2]
        dest = sys.argv[4]
        headers = sys.argv[6:]
        build_by_header(headers, directory, dest)
    else:
        print('wrong argument (order)')
        print('-d DIR -b DEST -s HEADER1 HEADER2 ...: builds folder in DEST containing files with given headers')
        exit(-1)

