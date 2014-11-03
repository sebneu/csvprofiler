__author__ = 'jumbrich'

import pandas as pd
import StringIO
import csv
from itertools import groupby
from messytables_types import type_guess

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


def deviations(file_content, delimiter=',', dialects=None):
    results = {}
    results['pandas'] = parse_using_pandas(file_content, delimiter)
    results['csv'] = parse_using_csv(file_content, delimiter, dialects)

    return results


def parse_using_csv(file_content, delimiter, dialects = None):
    results={}

    input = StringIO.StringIO(file_content.encode('utf-8'))

    rows = csv.reader(input, delimiter=delimiter.encode('ascii'), quoting=dialects['lib_csv']['quoting'])

    t = {
        'r_len': [],
        'r_val': [],
        'r_types': []
    }
    for row in rows:
        t['r_len'].append(len(row))
        t['r_val'].append(row)
        t['r_types'].append(determine_types(row))

    #group table by length element

    min_len = min(t['r_len'])
    max_len = max(t['r_len'])
    com = most_common_oneliner(t['r_len'])

    print "Min:",min_len, 'max', max_len, 'com', com
    grouped_L = [(k, sum(1 for i in g)) for k,g in groupby(t['r_len'])]
    print "groups", grouped_L
    #lets identify potentiall table areas


    #determine preceding/succeeding whitespaces
    # row_length == 0
    results['whitespaces']={'pre':0, 'suc':0, 'tuples':[]}

    # do we have descriptions
    # row length < common_len and row_length
    results['description']=[]

    ts = []

    '''
        tuple = (length, #elements)
        e.g., (5,3) = 5 columns and 3 rows
    cases:
        perfect table :
            (5,3)
        preceding, succedding whitespaces:
            (0,1), (5,3), (0,1)
        table with description:
            (1,1), (5,3)
        multi-table:
            (5,3), (4,3)
            (5,3),(0,3), (4,3)

    '''
    if len(grouped_L) == 1 and min_len == max_len == com!=0:
        print 'perfect symmetric table'
        ts.append({'s':0, 'e':grouped_L[0][1]})
    else:
        line = 0
        new_t= True
        tab ={}
        for i in range(len(grouped_L)):
            if grouped_L[i][0] == 0:
                results['whitespaces']['tuples'].append(grouped_L[i])
                if i == 0:
                    #preceding whitespaces
                    results['whitespaces']['pre'] =grouped_L[i][1]
                elif i == len(grouped_L)-1:
                    #succeding whitespace
                    results['whitespaces']['suc'] =grouped_L[i][1]
                    tab['e']=line+1
                    new_t=True
                    ts.append(tab)
                    tab ={}
                else:
                    tab['e']=line
                    new_t=True
                    ts.append(tab)
                    tab ={}
                    print 'whitespaces in the middle, indication for a multi table'
            elif grouped_L[i][0] == 1:
                #TODO Description line
                pass
            else:
                if new_t:
                    tab['s']=line
                    new_t=False



            line = grouped_L[i][1]


    tables = []

    for tab in ts:
        current_table = {}
        current_table['s'] = tab['s']
        current_table['e'] = tab['e']

        p_header = True
        h_rows = []
        p_row_t = None
        #r_types = type_guess(t['r_val'])
        #print r_types
        still_header_count = 0

        for i in range(tab['s'], tab['e']):
            header_types = []
            row = t['r_val'][i]
            r_types = t['r_types'][i]
            com_type = most_common_oneliner(r_types)
            print 'row', i, ': comtype', com_type
            print row

            if p_header:
                #lets assume we have a header
                still_header_count += 1
                #store types of the header
                header_types = r_types

            if p_row_t is not None:
                if set(p_row_t) != set(r_types):
                    print 'types change'
                    if p_header:
                        p_header = False

            p_row_t = r_types

            print '--'


        # check if all types in header are strings
        header_all_str = False
        if len(set(header_types)) == 1 and 'str' in header_types:
            header_all_str = True

        # subtract last header count
        still_header_count -= 1
        # all lines have the same type, but the only type is strings: guess that first line is header
        if still_header_count == len(range(tab['s'], tab['e'])) and header_all_str:
            current_table['header'] = 1
        # all lines have same type and not all of them are strings: assume that there is no header
        elif still_header_count == len(range(tab['s'], tab['e'])) and not header_all_str:
            current_table['header'] = 0
        # header is between 1 and 3 lines, but length of table is > header
        elif 1 <= still_header_count <= 3 and len(range(tab['s'], tab['e'])) > still_header_count:
            current_table['header'] = still_header_count
        # as default use the most common: first line is header
        else:
            current_table['header'] = 1


        tables.append(current_table)


    results['tables'] = tables




    # TODO move to other place
    results['ermilov'] = calc_ermilov_deviations(results, grouped_L, rows)


    return results

def most_common_oneliner(L):
  return max(groupby(sorted(L)), key=lambda(x, v):(len(list(v)),-L.index(x)))[0]



types = {'int':int, 'long':long, 'float':float, 'str':str}

def determine_types(row):

    r_types = []
    for cell in row:
        for type in types:
            try:
                types[type](cell)
                r_types.append(type)
                break
            except ValueError:
                pass

    return r_types


def calc_ermilov_deviations(csv_results, grouped_L, rows):
    results = {}

    # T-Whitespace
    if csv_results['whitespaces']['pre'] > 0 or csv_results['whitespaces']['suc'] > 0:
        results['T-Whitespace'] = True
    else:
        results['T-Whitespace'] = False

    # T-Multiple
    results['T-Multiple'] = _multiple_tables(grouped_L)

    # T-Metadata
    results['T-Metadata'] = _metadata(csv_results)

    # D-Duplicate
#    results['D-Duplicate'] =

    return results


def _multiple_tables(grouped_L):
    # TODO improved heuristic, description would also be multiple table
    if len([group for group in grouped_L if group[0] != 0]) > 1:
        return True
    else:
        return False


def _metadata(csv_results):
    # TODO metadata embedded below the table
    if len(csv_results['description']) > 0:
        return True
    else:
        return False