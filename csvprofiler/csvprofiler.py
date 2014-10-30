#!/usr/bin/python
__author__ = 'Juergen Umbrich'

'''
TODO fix max bytes flag
'''

import argparse
import sys
import copy
import logging
import logging.config
import os.path
import requests

import encoding
import dialect
import deviations


LOGGING_CONF = os.path.join(os.path.dirname(__file__),
                            "logging.ini")
logging.config.fileConfig(LOGGING_CONF)
logger = logging.getLogger()

# own modules
from pprint import pprint
from util import utils
import csv

#python twisted multiprocessing
#from twisted.internet.defer import DeferredSemaphore, gatherResults
#from twisted.internet import reactor
#from twisted.internet.threads import deferToThread
import gzip


def save_local(url, download_dir='temp/', max_bytes=None):
    if download_dir[-1] != '/':
        download_dir += '/'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    filename = download_dir + str(os.getpid())
    with open(filename, 'wb') as handle:
        response = requests.get(url, stream=True)
        if not response.ok:
            return None
        size = 0
        block_size = 1024
        for block in response.iter_content(block_size):
            if not block:
                break
            handle.write(block)
            size += block_size
            if max_bytes and size >= max_bytes:
                break
    return filename


def profileCSV(content, header, ):
    '''
        1) guess encoding
        2) proper content encoding
        3) guess dialect ( delimiter, etc)
        4) determine deviations
        5) stats for table(s) ( in case of multi table deviation
    '''

    results = {}
    results['enc'] = encoding.guessEncoding(content, header)

    ##we only try the chardet
    content_encoded = content.decode(encoding=results['enc']['lib_chardet']['encoding'])

    results['dialect'] = dialect.guessDialect(content_encoded)

    results['deviation'] = deviations.deviations(content_encoded)

    pprint(results)



def getContentFromDisk(fname_csv, max_bytes = None):
    if fname_csv[-3:] == '.gz':
        with gzip.open(fname_csv, 'rb') as f:
            if max_bytes:
                file_content = f.read(max_bytes)
            else:
                file_content = f.read()

    else:
        with open(fname_csv, 'rb') as f:
            if max_bytes:
                file_content = f.read(max_bytes)
            else:
                file_content = f.read()

    return file_content

def getContentAndHeader(file=None, url=None, datamonitor=None):
     #input
    content = None
    header = None

    if file:
        #process local file
        content = getContentFromDisk(file, max_bytes=4096)


    elif url:
        #we have an URL, either download it or get the content from the datamonitor

        if datamonitor:
            #get file content and header from data monitor
            logger.debug('TODO')
        else:
            # head lookup
            header = requests.head(url)
            # save file to local directory
            local_file = save_local(url, max_bytes=4096)
            # process local file
            content = getContentFromDisk(local_file, max_bytes=4096)

    return content, header

def runJob(pObj, args, dbm):
    pURL = pObj['pURL']
    url = pObj['url']
    logger.info("(%s) running job", url)
    status = ''.join(url)

    portal = dbm.getPortal(url, pURL)

    return status




def run(urls, num_of_processes, args, dbm):
    sem = DeferredSemaphore(num_of_processes)
    jobs = []

    for url_obj in urls:
        jobs.append(sem.run(async, url_obj, args, dbm))

    d = gatherResults(jobs)
    d.addBoth(done)
    reactor.run()


def async(url_obj, args, dbm):
    return deferToThread(runJob, url_obj, args, dbm)


def done(*args, **kwargs):
    print args
    print kwargs
    reactor.stop()


def parseArgs(pa):
    pa.add_argument('-v', '--verbose', help='verbose', action='store_true', default=False)
    pa.add_argument('-p', '--processors', help='Number of processors', default=1, type=int)


    group = pa.add_argument_group('input')
    group.add_argument('--file', help='local file')
    group.add_argument('--url', help='URL of CSV file')
    group.add_argument('--urllist', help='List of CSV URLs')

    group1 = pa.add_argument_group('env')
    group1.add_argument('--datamonitor', help='Datamonitor REST API URL')


    group2 = pa.add_argument_group('output')
    group2.add_argument('--out', help='Output')
    group1.add_argument('--db', help='database name')
    pa.add_argument('--host', help='MongoDBhost', default="localhost")

    args = pa.parse_args()

    #if args.url is None and args.urllist is None:
     #   pa.error("at least one of --url or --urllist is required to check the database")

    # if args.download and args.downloaddir is None:
    #     pa.error("option --downloadcsv needs option --downloaddir")
    # if args.analysecsv and args.downloaddir is None:
    #    pa.error("option --analysecsv needs option --downloaddir")
    return args


def main(argv):
    pa = argparse.ArgumentParser(description='CSVprofiler toolset.')
    args = parseArgs(pa)

    url_list = []

    #env


    #output
    if args.out:
        #output handling
        logger.debug("TODO")

    if args.db:
        logger.debug("establishing connection to MongoDB")
        #dbm = DBManager(args.db, args.host)


    file_content, header = getContentAndHeader(args.file, args.url, args.datamonitor)
    profileCSV( file_content, header)

if __name__ == "__main__":
    main(sys.argv[1:])




