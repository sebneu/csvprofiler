__author__ = 'jumbrich'

import pandas as pd
import StringIO

"""
http://svn.aksw.org/papers/2013/ISemantics_CSV2RDF/public.pdf
"""


def parse_using_pandas(file_content, delimiter):
    results = {}
    input = StringIO.StringIO(file_content)
    table = pd.read_csv(input, sep=delimiter)
    results['rows'] = table.shape[0]
    results['cols'] = table.shape[1]
    return results


def deviations(file_content, delimiter=','):
    results = {}
    results['pandas'] = parse_using_pandas(file_content, delimiter)
    return results