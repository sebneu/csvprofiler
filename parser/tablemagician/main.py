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
