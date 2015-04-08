__author__ = 'sebastian'


class AnalyserTable:
    def __init__(self, rows, cols, headers, types, name, delimiter):
        self.rows = rows
        self.columns = cols
        self.headers = headers
        self.types = types
        self.name = name
        self.delimiter = delimiter

    def __repr__(self):
        return "AnalyserTable (%s x %s)" % (len(self.columns), len(self.rows))