from __future__ import print_function
import os
import traceback
import tablemagician
import gzip
import shutil
import sys

__author__ = 'sebastian'

def build_by_header(header_set, rootdir, dest_dir):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filename = os.path.join(rootdir, file)
                # unzip filesq
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
    if len(sys.argv) >= 7 and sys.argv[1] == '-d' and sys.argv[3] == '-b' and sys.argv[5] == '-s':
        directory = sys.argv[2]
        dest = sys.argv[4]
        headers = sys.argv[6:]
        build_by_header(headers, directory, dest)
    else:
        print('wrong argument (order)')
        print('-d DIR -b DEST -s HEADER1 HEADER2 ...: builds folder in DEST containing files with given headers')
        exit(-1)