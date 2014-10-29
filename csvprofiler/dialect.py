__author__ = 'jumbrich'

import csvkit as csvkit
from csvkit import sniffer


def guessDialect(file_content):

    result = {}

    result['lib_csv'] = guessDialectWithLibCSV(file_content)






    return result


def guessDialectWithLibCSV(file_content):
    """

    :param file_content: the file content of the csv file
    :return: a csv dialect object
    """
    dialect = sniffer.sniff_dialect(file_content)

    return {
        'delimiter': dialect.delimiter,
        'doublequote': dialect.doublequote,
        'lineterminator': dialect.lineterminator,
        'quotechar': dialect.quotechar,
        'quoting': dialect.quoting,
        'skipinitialspace': dialect.skipinitialspace
    }
