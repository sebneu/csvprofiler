__author__ = 'neumaier'

from pymongo import Connection


class DBManager:
    def __init__(self, db=None, host="localhost"):
        con = Connection(host, 27017)
        if db is not None:
            self.db = con[db]
        else:
            self.db = con["csv"]


    def storeCsvMetaData(self, csv_meta):
        self.db['portal_core'].save(csv_meta.__dict__)


    def getCsvMetaData(self):
        return self.db['portal_core'].find(timeout=False)


