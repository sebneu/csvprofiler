from analyser import Analyser
import celltype_analyzer

__author__ = 'jumbrich'




class ComplexTypeAnalyser(Analyser):
    def process(self, analyser_table):
        vals = detect_datatypes(analyser_table)
        a = 0
        for s in vals:
            a += 1
            if len(s) > 1:
                ss = '_'.join(sorted(s))
                print('COLTYPES  %s %s' % (ss, str(a)))


def detect_datatypes(table):
    types = []
    for column in table.columns:
        c_types = determine_types(column)
        types.append(c_types)
    return types


def getCellType(cell):
    return celltype_analyzer.detectCellType(cell)


def determine_types(column):
    r_types = {}
    for cell in column:
        value = cell.value
        if cell.empty:
            value = ''
        if cell.type.result_type != basestring:
            value = str(cell.value)
        type = getCellType(value)
        if type not in r_types:
            r_types[type] =0
        r_types[type]+=1
    return r_types