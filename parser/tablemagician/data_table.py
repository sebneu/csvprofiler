__author__ = 'sebastian'


class DataTable:
    def __init__(self, headers=None, rows=None, types=None):
        self.headers = headers
        self.rows = rows
        self.types = types

    def __repr__(self):
        return "DataTable (%s x %s)" % (len(self.headers), len(self.rows))