import argparse
import csv
import sys
import cStringIO
from messytables import any_tableset, headers_guess, headers_processor, offset_processor, type_guess, types_processor
import messytables
from tablemagician.data_table import DataTable
import urllib2
from cStringIO import StringIO
import logging
import logging.config
import os
import codecs

# load the logging configuration

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logging.ini'))
logger = logging.getLogger(__name__)

__author__ = 'sebastian'


def _build_datatables(handle, name, date_parser):
    table_set = any_tableset(handle)

    tables = []
    # Build meta data objects
    for row_set in table_set.tables:
        # A table set is a collection of tables:
        # guess header names and the offset of the header:
        offset, headers = headers_guess(row_set.sample)
        logger.debug('headers: %s', headers)

        row_set.register_processor(headers_processor(headers))

        # add one to begin with content, not the header:
        row_set.register_processor(offset_processor(offset + 1))

        # guess column types:
        messytables.types.BoolType.true_values = ['true', 'True', 'TRUE']
        messytables.types.BoolType.false_values = ['false', 'False', 'FALSE']
        selected_types = [messytables.types.StringType,
                          messytables.types.DecimalType,
                          messytables.types.IntegerType,
                          messytables.types.BoolType]
        if date_parser:
            selected_types.append(messytables.types.DateUtilType)

        types = type_guess(row_set.sample, types=selected_types
                           #strict=True
                           )
        logger.debug('types: %s', types)

        # and tell the row set to apply these types to
        # each row when traversing the iterator:
        row_set.register_processor(types_processor(types))

        datatable = DataTable(handle, headers, row_set, types, name, row_set._dialect.delimiter)
        tables.append(datatable)

    logger.debug('num of tables: %s', len(tables))
    return tables


def from_path(path, date_parser=False):
    """

    :param path: The local file name of the resource
    :return: A DataTable object
    :param date_parser: if true, the type detection will parse for dates
    """
    f = open(path, 'rb')
    # Load a file object
    logger.debug('parse file from local path: %s', path)
    datatables = _build_datatables(f, path, date_parser)
    return datatables


def from_url(url, date_parser=False):
    """

    :param url: The URL of the resource
    :param date_parser: if true, the type detection will parse for dates
    :return: A DataTable object
    """
    # TODO add max num of lines to download
    response = urllib2.urlopen(url)
    f = StringIO(response.read())
    datatables = _build_datatables(f, url, date_parser)
    return datatables


def from_file_object(file, name=None, date_parser=False):
    datatables = _build_datatables(file, name, date_parser)
    return datatables


def arguments(args=None, description=None):
    argparser = argparse.ArgumentParser(description=description)

    argparser.add_argument(metavar="FILE", dest='input_path',
                           help='The CSV file to operate on.')

    argparser.add_argument('-m', '--max-lines', dest='max_lines', type=int, default=-1,
                           help='Maximum number of lines processed by the parser.')
    argparser.add_argument('--types', dest='types', action='store_true',
                           help='Print the guessed types of the columns.')
    argparser.add_argument('--header', dest='header', action='store_true',
                           help='Print only the header line.')
    argparser.add_argument('-o', '--output', dest='output',
                           help='Specify an output file. If not specified, output will be written to STDOUT.')
    argparser.add_argument('--rfc', dest='rfc', action='store_true',
                           help='Converts the input file into RFC 4180 conform output.')
    argparser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                           help='Print detailed information.')

    args = argparser.parse_args(args)

    if not args.input_path:
        argparser.error("Parameter FILE is required.")

    return args


def main():
    args = arguments(description='A simple CSV parser based on messytables')

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(level=logging.DEBUG)

    datatables = from_path(args.input_path)
    for d in datatables:
        if args.output:
            out = open(args.output, 'wb')
        else:
            out = sys.stdout

        writer = UnicodeWriter(out)
        if args.header:
            writer.writerow(d.headers)

        if args.types:
            writer.writerow(d.types)

        table = d.process(args.max_lines)

        if args.rfc:
            writer = UnicodeWriter(out)
            writer.writerow(table.headers)
            for row in table.rows:
                writer.writerow([c.value for c in row])

        # assume that we only have one table here
        if len(datatables) > 1:
            logger.warning('Multiple tables found in the input-file.')
        break


if __name__ == '__main__':
    main()


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        u_row = []
        for s in row:
            out = s
            if isinstance(s, basestring):
                out = s.encode("utf-8")
            elif s is None:
                out = ''
            u_row.append(out)
        self.writer.writerow(u_row)

        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
