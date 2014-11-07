__author__ = 'jumbrich'

import argparse
import sys
import logging
import logging.config
import os.path
from DBManager import DBManager
from pprint import pprint

import pandas
import plot
from reporting import Report
import operator
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

def update(count, key ):
    if key and isinstance(key, basestring):
        key = key.lower()
    if key is None:
        key = 'None'
    count[key] = count.get(key , 0) + 1

def parseArgs(pa):
    pa.add_argument('-v', '--verbose', help='verbose', action='store_true', default=False)
    pa.add_argument('-p', '--processors', help='Number of processors', default=1, type=int)




    group2 = pa.add_argument_group('output')
    group2.add_argument('--out', help='Output')
    group2.add_argument('--db', help='database name')
    group2.add_argument('--host', help='MongoDBhost', default="localhost")

    args = pa.parse_args()

    #if args.url is None and args.urllist is None:
     #   pa.error("at least one of --url or --urllist is required to check the database")

    # if args.download and args.downloaddir is None:
    #     pa.error("option --downloadcsv needs option --downloaddir")
    # if args.analysecsv and args.downloaddir is None:
    #    pa.error("option --analysecsv needs option --downloaddir")
    return args

def get_header_charset(cont_type):

    header_encoding = cont_type
    if cont_type and len(cont_type.split(';')) > 1:
        header_encoding = cont_type.split(';')[0]
        header_encoding = header_encoding.strip()
    return header_encoding

def main(argv):
    pa = argparse.ArgumentParser(description='Open Portal Watch toolset.')
    args = parseArgs(pa)


    logger.debug("establishing connection to MongoDB")
    dbm = DBManager(args.db, args.host)


    stats={'overview':{'total':0, 'suc':0, 'no_res':0, '404':0, 'errors':0}}
    overview = stats['overview']

    fC={
        'f_ext': {},
        'devs':{},
        'h_charset' : {},
        'd_charset' : {},
        'd_delim' : {},
        'errors': {},
        'h_ctype': {}
    }


    charset={}



    c = 0
    for csvm in dbm.getCsvMetaData():
        overview['total']+=1


        update(fC['f_ext'], csvm['extension'])

        if csvm['results']:
            res = csvm['results']

            if 'error' not in res:
                if csvm['header']:
                    deviations = res['deviation']['csv']['ermilov']
                    for dev in deviations:
                        if dev not in fC['devs']:
                            fC['devs'][dev] = {}
                        update(fC['devs'][dev], deviations[dev])

                    overview['suc']+=1

                    update(fC['d_delim'],res['dialect']['lib_csv']['delimiter'])
                    enc = res['enc']['lib_chardet']['encoding']
                    update(fC['d_charset'],enc)

                    if 'content-type' in csvm['header']:
                        update(fC['h_ctype'], get_header_charset(csvm['header']['content-type']))
                    else:
                        update(fC['h_ctype'], 'missing')
                    update(fC['h_charset'],res['enc']['header']['encoding'])


                    if enc is None:
                        enc = 'mis'

                    h_enc = charset.get(enc, {})
                    if res['enc']['header']['encoding'] is None:
                        update(h_enc, 'mis')
                    else:
                        update(h_enc, res['enc']['header']['encoding'])
                    charset[enc] = h_enc

                else:
                    overview['404'] +=1

            else:
                overview['errors'] +=1
                update(fC['errors'], res['error'])
        else:
            #no_res +=1
            overview['no_res'] +=1
        if overview['total']%1000 == 0:
            #break;
            print 'processed ',overview['total'],'files'


    stats['freqDist']={}
    for fc in fC:

        if fc is 'devs':
            t = {k:v[True] for (k,v) in fC[fc].iteritems()}.values()
            f = {k:v[False] for (k,v) in fC[fc].iteritems()}.values()

            df = pandas.DataFrame(dict(graph=fC[fc].keys(),
                           value=t, F=f))
            df = df.sort(['value'], ascending=False)
        else:
            df = pandas.DataFrame(dict(graph=fC[fc].keys(),
                           value=fC[fc].values()))
            df = df.sort(['value'], ascending=False)
        #print fc
        #print df
        stats['freqDist'][fc]=df






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
    pprint(stats)

    pprint(charset)


    report = Report(stats, args.out)
    report.generateReport()


    for p in plots:

        printlist(p['d'])
        freq_list2 = [(val, key) for key, val in p['d'].items()]
        # sort by val or frequency
        freq_list2.sort(reverse=True)

        sorted_x = sorted(p['d'].items(), key=operator.itemgetter(1),reverse=True)

        print 'sort',sorted_x
        data = {}
        for v,k in sorted_x:
            if v is None:
                v = 'mis'
            data[v.encode('utf-8')] = k

        print 'data',data

        df = pandas.DataFrame(dict(graph=data.keys(),
                           n=data.values()))
        plot.hbarchart(df,p['xl'] , p['yl'], '', args.out, p['fname'])


if __name__ == "__main__":
    main(sys.argv[1:])