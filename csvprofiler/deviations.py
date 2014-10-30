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
    return


def deviations(file_content, delimiter=','):
    parse_using_pandas(file_content, delimiter)