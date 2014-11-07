#!/usr/bin/python
import csv
from pprint import pprint
import datetime
from DBManager import DBManager
from CsvMetaData import CsvMetaData

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

from multiprocessing import Process, Queue, current_process
import gzip

MAX_CHARACTER = 6
DATAMONITOR = "http://137.208.51.23:8080/datamonitor-rest/service/v1/crawldata?uri="

LOGGING_CONF = os.path.join(os.path.dirname(__file__),
                            "logging.ini")
logging.config.fileConfig(LOGGING_CONF)
logger = logging.getLogger()


def get_file_extension(filename):
    file_extension = None
    f, long_file_extension = os.path.splitext(filename)
    if long_file_extension == '.gz':
        f, long_file_extension = os.path.splitext(filename[:-3])
    if len(long_file_extension) < MAX_CHARACTER:
        file_extension = long_file_extension[1:]
    return file_extension




def save_local(url, download_dir, max_bytes=None):
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


def profileCSV(content, header):
    '''
        1) guess encoding
        2) proper content encoding
        3) guess dialect ( delimiter, etc)
        4) determine deviations
        5) stats for table(s) ( in case of multi table deviation
    '''

    results = {}
    try:
        results['enc'] = encoding.guessEncoding(content, header)

        ##we only try the chardet
        if not results['enc']['lib_chardet']['encoding']:
            raise Exception('chardet: encoding not detected')

        logger.debug('chardet encoding: %s', results['enc']['lib_chardet']['encoding'])
        content_encoded = content.decode(encoding=results['enc']['lib_chardet']['encoding'])


        results['dialect'] = dialect.guessDialect(content_encoded)

        results['deviation'] = deviations.deviations(content_encoded,
                                                     delimiter=results['dialect']['lib_csv']['delimiter'],
                                                     dialects= results['dialect'])
    except Exception as inst:
        logger.exception(inst, exc_info=True)
        results['error'] = inst.message
    finally:
        return results



def getContentFromDisk(fname_csv, max_lines=None):
    if fname_csv[-3:] == '.gz':
        with gzip.open(fname_csv, 'rb') as f:
            if max_lines:
                file_content = ''
                c =0
                for line in f:
                    file_content += line
                    c+=1
                    if c>=max_lines:
                        break

            else:
                file_content = f.read()

    else:
        with open(fname_csv, 'rU') as f:
            if max_lines:
                file_content = ''
                for line in f.readlines(max_lines):
                    file_content += line
            else:
                file_content = f.read()

    return file_content

def getContentAndHeader(file=None, url=None, download_dir=None):
     #input
    content = None
    header = None
    file_extension = None
    status_code = None

    if file:
        file_extension = get_file_extension(file)

        if os.path.exists(file):
            #process local file
            content = getContentFromDisk(file, max_lines=100)
        else:
            logger.exception('(%s) No such file: %s', url, file)
            file = None

    if url:
        if not file_extension:
            # TODO preprocess url
            file_extension = get_file_extension(url)

        # put requests into try block
        try:
            # head lookup
            head = requests.head(url)
            status_code = head.status_code
            header = dict(head.headers)

            if not file:
                # save file to local directory
                local_file = save_local(url, max_bytes=4096, download_dir=download_dir)
                if local_file:
                    # process local file
                    content = getContentFromDisk(local_file, max_lines=100)
        except Exception as e:
            logger.exception(e, exc_info=True)
            status_code = 701

    return content, header, file_extension, status_code


def getDatamonitorInfo(url, datamonitor_url):
    file = None
    dm_header = None

    try:
        req_url = datamonitor_url + url
        r = requests.get(req_url)
        if r.status_code == requests.codes.ok:
            # get datamonitor json
            results = r.json()
            if 'results' in results and len(results['results']) > 0:
                # take the latest results
                sorted_results = sorted(results['results'], key=lambda k: k['timestamp'])
                # select latest result (by timestamp)
                result = sorted_results[-1]

                # look for redirect
                if result['status'] in [requests.codes.moved, requests.codes.found]:
                    # then there is a location in the header
                    moved_url = result['header']['Location']
                    return getDatamonitorInfo(moved_url, datamonitor_url)

                if 'header' in result:
                    dm_header = result['header']
                if 'disklocation' in result:
                    file = result['disklocation']

    except Exception as e:
        logger.exception(e, exc_info=True)

    return file, dm_header


def run_job(p, args, dbm):
    try:
        url = p['url']
        portal_id = p['portal']
        logger.info("(%s) running job", url)
        status = ''.join(url)
        file, dm_header = getDatamonitorInfo(url, args.datamonitor)
        content, header, file_extension, status_code = getContentAndHeader(file=file, url=url, download_dir=args.downdir)
        csv_entry = CsvMetaData(url)
        csv_entry.filename = file
        csv_entry.time = datetime.datetime.now()
        csv_entry.header = header
        csv_entry.extension = file_extension
        csv_entry.status_code = status_code
        csv_entry.portal_id = portal_id

        if file:
            csv_entry.datamonitor = True
        if dm_header:
            csv_entry.dm_header = dm_header

        if content:
            results = profileCSV(content, header)
            csv_entry.results = results

        dbm.storeCsvMetaData(csv_entry, args.collection)
    except Exception as e:
        logger.exception(e, exc_info=True)

    return status


def worker(work_queue, done_queue, args, dbm):
    try:
        for p in iter(work_queue.get, 'STOP'):
            url = p['url']
            logger.info('START#%s (process %s)', url, current_process().name)
            status = run_job(p, args, dbm)
            done_queue.put("%s - done %s" % (current_process().name, status))
            logger.info('END#%s (process %s)', url, current_process().name)
    except Exception, e:
        logger.exception('%s - %s:%s (process %s)', url, type(e), e.message, current_process().name)
        done_queue.put("%s failed on %s with: %s" % (current_process().name, url, e.message))
    return True



def parseArgs(pa):
    pa.add_argument('-v', '--verbose', help='verbose', action='store_true', default=False)
    pa.add_argument('-p', '--processors', help='Number of processors', default=1, type=int)


    group = pa.add_argument_group('input')
    group.add_argument('--urllist', help='List of CSV URLs')
    group.add_argument('-d', '--downdir', help='Directory for downloads', default='temp/', type=str)

    group1 = pa.add_argument_group('env')
    group1.add_argument('--datamonitor', help='Datamonitor REST API URL', default=DATAMONITOR)


    group2 = pa.add_argument_group('output')
    group2.add_argument('--out', help='Output')
    group1.add_argument('--db', help='database name')
    group1.add_argument('--collection', help='collection name', default='profiler')
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


    work_queue = Queue()
    done_queue = Queue()
    processes = []

    c = 0
    #populate work queue
    if args.urllist:
        with open(args.urllist) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if row[0].startswith("http"):
                    c += 1
                    if len(row[1]) > 1:
                        work_queue.put({"url": row[0], "portal": row[1]})

    logger.debug("establishing connection to MongoDB")
    dbm = DBManager(args.db)

    logger.info("Processing %s url(s)", c)
    for w in xrange(args.processors):
        p = Process(target=worker, args=(work_queue, done_queue, args, dbm))
        p.start()
        processes.append(p)
        work_queue.put('STOP')

    for p in processes:
        p.join()

    done_queue.put('STOP')


if __name__ == "__main__":
    main(sys.argv[1:])
