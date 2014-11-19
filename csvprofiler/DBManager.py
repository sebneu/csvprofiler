__author__ = 'neumaier'

from pymongo import Connection
from model.CSVProfileStats import CSVProfileStats

from db.allow_mongo_dot_keys import KeyTransform




class DBManager:
    def __init__(self, db=None, host="localhost"):
        con = Connection(host, 27017)
        if db is not None:
            self.db = con[db]
        else:
            self.db = con["csv"]
        self.db.add_son_manipulator(KeyTransform(".", "_dot_"))

    def storeCsvMetaData(self, csv_meta, collection):
        self.db[collection].save(csv_meta.__dict__)



    def getCsvMetaData(self, portal, portalID):
        if portal is None:
            return self.db['portal_core'].find(timeout=False)
        else:
            return self.db['portal_core'].find({'portal_id':portalID},timeout=False)


    def storeCSVProfilStatis(self, csvps):
        #print 'Storing ....'
        #print csvps.__dict__
        self.db['portal_stats'].save(csvps.__dict__)

    def getCSVProfilStatis(self, portal, portalID):
        p = self.db['portal_stats'].find_one({'portal_id': portalID})
        csv = CSVProfileStats(portal, portalID)
        if p is not None:
            csv = CSVProfileStats(dict_string=p)
        return csv