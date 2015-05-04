import decimal
import tablemagician

__author__ = 'sebastian'

import argparse
import os
import gzip
import traceback
import csv
import numpy as np
from urlparse import urlparse



def arg_parser():
    parser = argparse.ArgumentParser(description='Collect stats about a folder of csv files.')
    parser.add_argument('-o', '--out-dir', help='out directory for files', default='.')
    parser.add_argument('-i', '--in-dir', help='in directory of files')
    parser.add_argument('-l', '--list', help='list of all urls + files', default='/data/csv/url_csv.csv')
    parser.add_argument('-f', '--features', help='csv file with features')
    parser.add_argument('--max', help='max number of files', default=-1, type=int)
    parser.add_argument('--plot', help='store a plot', action='store_true')

    args = parser.parse_args()
    return args


def feature_extraction(filename):
    if filename.endswith('.gz'):
        f = gzip.open(filename, 'rb')
    else:
        f = open(filename, 'rb')

    # read first rows of table
    tables = tablemagician.from_file_object(f, filename)
    if len(tables) == 0:
        raise ValueError('No table: ' + filename)
    for table in tables:
        #analyser_table = table.process(max_lines=MAX_ROWS)

        num_of_columns = len(table.headers)

        header = [h.lower() for h in table.headers]

        types = [t.result_type for t in table.types]

        numeric = types.count(int) + types.count(decimal.Decimal)
        strings = types.count(basestring)
        # add feature
        f.close()
        feature = [num_of_columns, numeric, strings]
        break

    # reopen file after iteration
    if filename.endswith('.gz'):
        f = gzip.open(filename, 'rb')
    else:
        f = open(filename, 'rb')
    number_lines = sum(1 for _ in f)
    f.close()
    return [number_lines] + feature


def features_from_dir(rootdir):
    features = []
    i = 0
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filename = os.path.join(rootdir, file)
                feature = feature_extraction(filename)
                features.append([filename, ''] + feature)
                i += 1
            except Exception as e:
                traceback.print_exc()
                print e
            if 0 < MAX_FEATURES < i:
                print 'max features', MAX_FEATURES
                break
    return features


def features_from_url_file(urls_file):
    features = []
    csvf = csv.reader(urls_file)
    i = 0
    for row in csvf:
        url = row[0]
        filename = row[1]
        if filename.endswith('xml.gz'):
            continue

        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

        try:
            feature = [url, domain] + feature_extraction(filename)
            features.append(feature)
            i += 1
        except Exception as e:
            traceback.print_exc()
            print e
        if 0 < MAX_FEATURES < i:
            print 'max features', MAX_FEATURES
            break
    return features


def plot_mean_shift(features):
    from sklearn.cluster import MeanShift, estimate_bandwidth
    # Compute clustering with MeanShift

    # The following bandwidth can be automatically detected using
    bandwidth = estimate_bandwidth(features, quantile=0.2, n_samples=500)

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(features)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    labels_unique, counts = np.unique(labels, return_counts=True)
    n_clusters_ = len(labels_unique)

    print("number of estimated clusters : %d" % n_clusters_)

    ###############################################################################
    # Plot result
    import matplotlib.pyplot as plt
    from itertools import cycle

    fig = plt.figure()
    ax = plt.subplot(111)

    #centers = []
    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters_), colors):
        my_members = labels == k
        cluster_center = cluster_centers[k]
        ax.plot(features[my_members, 0], features[my_members, 1], col + '.')
        c, = ax.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                 markeredgecolor='k', markersize=14, label=str(counts[k]))
        #centers.append(c)

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(str(len(features)) + ' values. Estimated number of clusters: %d' % n_clusters_)
    plt.savefig('clustering.pdf')


if __name__ == '__main__':
    args = arg_parser()
    MAX_FEATURES = args.max

    if args.features:
        features = []
        with open(args.features, 'rb') as f:
            csvf = csv.reader(f)
            for row in csvf:
                try:
                    features.append([x for x in row])
                except Exception as e:
                    traceback.print_exc()
                    print e
    else:
        if args.in_dir:
            features = features_from_dir(args.in_dir)
        else:
            f = open(args.list, 'rb')
            features = features_from_url_file(f)

        with open('features.csv', 'w') as f:
            for values in features:
                try:
                    line = ','.join(str(x) for x in values)
                    f.write(line + '\n')
                except Exception as e:
                    traceback.print_exc()
                    print e

    if args.plot:
        max_x = 20000.0
        max_y = 30.0
        print max_x, 'x', max_y
        plot_fts = [[int(x[2])/max_x, int(x[3])/max_y] for x in features if int(x[2]) < max_x and int(x[3]) < max_y]
        fts = np.array(plot_fts)
        plot_mean_shift(fts)