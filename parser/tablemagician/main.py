import copy
from messytables import any_tableset, headers_guess, headers_processor, offset_processor, type_guess, types_processor
import messytables
import time
from tablemagician.data_table import DataTable
import urllib2
from cStringIO import StringIO
import logging
import logging.config

# load the logging configuration
logging.config.fileConfig('logging.ini')

logger = logging.getLogger(__name__)

__author__ = 'sebastian'


def _build_datatables(handle, max_rows=-1):
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
        types = type_guess(row_set.sample, types=[messytables.types.StringType,
                                                  messytables.types.DecimalType,
                                                  messytables.types.IntegerType,
                                                  messytables.types.DateUtilType,
                                                  messytables.types.BoolType],
                           strict=True)
        logger.debug('types: %s', types)

        # and tell the row set to apply these types to
        # each row when traversing the iterator:
        row_set.register_processor(types_processor(types))

        # TODO find better solution!
        # copy the rows into the datatable object
        # t1 = time.time()
        # row_count = 0
        # rows = []
        # for row in row_set:
        #     rows.append(copy.deepcopy(row))
        #     if 0 < max_rows < row_count:
        #         break
        # t2 = time.time()
        # logger.debug('copy rows duration: %s', t2 - t1)

        datatable = DataTable(handle, headers, row_set, types)
        tables.append(datatable)

    logger.debug('num of tables: %s', len(tables))
    return tables


def from_path(path):
    """

    :param path: The local file name of the resource
    :return: A DataTable object
    """
    f = open(path, 'rb')
    # Load a file object
    logger.debug('parse file from local path: %s', path)
    datatables = _build_datatables(f)
    return datatables


def from_url(url):
    """

    :param url: The URL of the resource
    :return: A DataTable object
    """
    # TODO add max num of lines to download
    response = urllib2.urlopen(url)
    f = StringIO(response.read())
    datatables = _build_datatables(f)
    return datatables
