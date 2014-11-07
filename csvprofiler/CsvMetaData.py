__author__ = 'neumaier'

class CsvMetaData:
    def __init__(self, url=None, dict_string=None):
        if dict_string is not None:
            self.__dict__ = dict_string
        else:
            self.url = url
            self.filename = None
            self.header = None
            self.results = None
            self.time = None
            self.status_code = None
            self.extension = None
            self.portal_id = None
            self.dm_header = None
            self.datamonitor = False