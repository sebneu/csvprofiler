

__author__ = 'jumbrich'

import argparse
import sys
import logging
import logging.config
import os.path
from DBManager import DBManager
from pprint import pprint
from urlparse import urlparse
import pandas
import csv
import plot
from reporting import Report
import operator

from model.CSVProfileStats import CSVProfileStats

LOGGING_CONF = os.path.join(os.path.dirname(__file__),
                            "logging.ini")
logging.config.fileConfig(LOGGING_CONF)
logger = logging.getLogger()


def printlist(dict):
    # create list of (val, key) tuple pairs
    freq_list2 = [(val, key) for key, val in dict.items()]
    # sort by val or frequency
    freq_list2.sort(reverse=True)
    # display result
    pprint(freq_list2)


def parseArgs(pa):
    pa.add_argument('-v', '--verbose', help='verbose', action='store_true', default=False)
    pa.add_argument('-p', '--processors', help='Number of processors', default=1, type=int)

    group2 = pa.add_argument_group('output')
    group2.add_argument('--out', help='Output')
    group2.add_argument('--db', help='database name')
    group2.add_argument('--host', help='MongoDBhost', default="localhost")
    group2.add_argument('--agg', help='Aggregate the results')

    group1 = pa.add_argument_group('input')
    group1.add_argument('--url', help='CKAN Portal API URL')
    group1.add_argument('--urllist', help='CKAN Portal API URL list')


    args = pa.parse_args()

    #if args.url is None and args.urllist is None:
     #   pa.error("at least one of --url or --urllist is required to check the database")

    # if args.download and args.downloaddir is None:
    #     pa.error("option --downloadcsv needs option --downloaddir")
    # if args.analysecsv and args.downloaddir is None:
    #    pa.error("option --analysecsv needs option --downloaddir")
    return args


def get_portal_id_from_url(api):
    print api
    domain = urlparse(api).netloc
    portal_id = ""
    for t in domain.split("."):
        portal_id = portal_id + t[:2]
    return portal_id

def main(argv):
    pa = argparse.ArgumentParser(description='Open Portal Watch toolset.')
    args = parseArgs(pa)


    logger.debug("establishing connection to MongoDB")
    dbm = DBManager(args.db, args.host)

    portals = []
    if args.url:
        portals.append(get_portal_id_from_url(args.url))
    elif args.urllist:
        with open(args.urllist) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if row[0].startswith("http"):
                    if len(row[1]) > 1:
                        portals.append(row[0])

    else:
        portals.append(None)



    c = 0
    agg = None
    if args.agg:
        aggID = args.agg
        agg = dbm.getCSVProfilStatis("",aggID)

    for portal in portals:
        if portal == None:
            stats = dbm.getCSVProfilStatis("",'ALL')
        else:
            stats = dbm.getCSVProfilStatis(portal, get_portal_id_from_url(portal))

        for csvm in dbm.getCsvMetaData(portal, get_portal_id_from_url(portal)):
            c+=1
            stats.update(csvm)

        if agg is not None:
            agg.aggregate(stats)

        #report = Report(stats, args.out)
        #report.generateReport()

        dbm.storeCSVProfilStatis(stats)

    if agg:
        report = Report(agg, args.out)
        report.generateReport()
        pprint(agg.__dict__)

    print "Analysed in total ",c," CSV files"







    # plots=[
    #     {'d':f_ext,
    #      'yl':'file extension',
    #      'xl':'\%of documents',
    #      'fname':'f_ext.png'
    #     },
    #     {'d':d_charset,
    #      'yl':'chardet',
    #      'xl':'\%of documents',
    #      'fname':'h_charset.png'
    #     },
    #     {'d':d_delim,
    #      'yl':'delimiter',
    #      'xl':'\%of documents',
    #      'fname':'d_delim.png'
    #     },
    #     {'d':d_delim,
    #      'yl':'delimiter',
    #      'xl':'\%of documents',
    #      'fname':'d_delim.png'
    #     }
    # ]


#    pprint(charset)




    # for p in plots:
    #
    #     printlist(p['d'])
    #     freq_list2 = [(val, key) for key, val in p['d'].items()]
    #     # sort by val or frequency
    #     freq_list2.sort(reverse=True)
    #
    #     sorted_x = sorted(p['d'].items(), key=operator.itemgetter(1),reverse=True)
    #
    #     print 'sort',sorted_x
    #     data = {}
    #     for v,k in sorted_x:
    #         if v is None:
    #             v = 'mis'
    #         data[v.encode('utf-8')] = k
    #
    #     print 'data',data
    #
    #     df = pandas.DataFrame(dict(graph=data.keys(),
    #                        n=data.values()))
    #     plot.hbarchart(df,p['xl'] , p['yl'], '', args.out, p['fname'])


if __name__ == "__main__":
    main(sys.argv[1:])