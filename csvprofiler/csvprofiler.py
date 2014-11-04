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


LOGGING_CONF = os.path.join(os.path.dirname(__file__),
                            "logging.ini")
logging.config.fileConfig(LOGGING_CONF)
logger = logging.getLogger()


def get_file_extension(filename):
    file_extension = None
    f, long_file_extension = os.path.splitext(filename)
    if long_file_extension == '.gz':
        f, long_file_extension = os.path.splitext(filename[:-3])
    if len(long_file_extension) < 10:
        file_extension = long_file_extension[1:]
    return file_extension

from multiprocessing import Process, Queue, current_process
import gzip


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
                for line in f.readlines(max_lines):
                    file_content += line

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

def getContentAndHeader(file=None, url=None, datamonitor=None, download_dir=None):
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
            file_extension = get_file_extension(url)

        #we have an URL, either download it or get the content from the datamonitor
        if datamonitor:
            #get file content and header from data monitor
            logger.debug('TODO')
        else:
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

    return content, header, file_extension, status_code


def run_job(p, args, dbm):
    try:
        url = p['url']
        file = p['file']
        logger.info("(%s) running job", url)
        status = ''.join(url)

        content, header, file_extension, status_code = getContentAndHeader(file=file, url=url, download_dir=args.downdir)
        csv_entry = CsvMetaData(url)
        csv_entry.time = datetime.datetime.now()
        csv_entry.header = header
        csv_entry.extension = file_extension
        csv_entry.status_code = status_code

        if content:
            results = profileCSV(content, header)
            csv_entry.results = results

        dbm.storeCsvMetaData(csv_entry)
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
    group.add_argument('--file', help='local file')
    group.add_argument('--url', help='URL of CSV file')
    group.add_argument('--urllist', help='List of CSV URLs')
    group.add_argument('-d', '--downdir', help='Directory for downloads', default='temp/', type=str)

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

    pa = argparse.ArgumentParser(description='Open Portal Resources toolset.')
    args = parseArgs(pa)

    work_queue = Queue()
    done_queue = Queue()
    processes = []

    c = 0
    #populate work queue
    if args.urllist:
        with open(args.urllist) as f:
            reader = csv.reader(f, delimiter=' ')
            for row in reader:
                if row[0].startswith("http"):
                    c += 1
                    if len(row[1]) > 1:
                        work_queue.put({"url": row[0], "file": row[1]})

    if args.url and args.file:
        c += 1
        work_queue.put({"file": args.file, "url": args.url})

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
