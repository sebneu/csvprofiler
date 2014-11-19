__author__ = 'jumbrich'

import pandas

class CSVProfileStats:
    def __init__(self, portal,  id=None, dict_string=None):
        if dict_string is not None:
            self.__dict__ = dict_string
        else:
            self.id=id
            self.url = portal
            self.overview = {'total':0, 'suc':0, 'no_res':0, '404':0, 'errors':0}

            self.fC={
                'f_ext': {},
                'devs':{},
                'h_charset' : {},
                'd_charset' : {},
                'd_delim' : {},
                'errors': {},
                'h_ctype': {}
            }
            self.charset={}


    def aggregate(self, stats):

        for k in stats.overview:
            self.overview[k]+= stats.overview[k];

        for c in stats.fC:
            if "devs" is not c:
                for k in stats.fC[c]:

                    self.updateCount(self.fC[c], k, stats.fC[c][k])
            else:
                for k in stats.fC[c]:
                    #print k,stats.fC[c][k]
                    if k not in self.fC[c]:
                        self.fC[c][k]={}
                    if 'true' in stats.fC[c][k]:
                        self.updateCount(self.fC[c][k],'true', stats.fC[c][k]['true'])
                    if 'false' in stats.fC[c][k]:
                        self.updateCount(self.fC[c][k],'false', stats.fC[c][k]['false'])

        for k in stats.charset:
            #print k, stats.charset[k]
            if k not in self.charset:
                self.charset[k]={}
            for c in stats.charset[k]:
                self.updateCount(self.charset[k],c, stats.charset[k][c])




    def update(self, csvm):
        self.overview['total']+=1

        self.updateCount(self.fC['f_ext'], csvm['extension'])

        if csvm['results']:
            res = csvm['results']

            if 'error' not in res:
                if csvm['header']:
                    deviations = res['deviation']['csv']['ermilov']
                    hasDev = False
                    for dev in deviations:
                        if dev not in self.fC['devs']:
                            self.fC['devs'][dev] = {}
                        self.updateCount(self.fC['devs'][dev], deviations[dev])
                        if deviations[dev]:
                            hasDev = True

                    dev = 'with deviations'
                    if dev not in self.fC['devs']:
                        self.fC['devs'][dev] = {}
                    self.updateCount(self.fC['devs'][dev], hasDev)


                    self.overview['suc']+=1

                    self.updateCount(self.fC['d_delim'],res['dialect']['lib_csv']['delimiter'])
                    enc = res['enc']['lib_chardet']['encoding']
                    self.updateCount(self.fC['d_charset'],enc)

                    if 'content-type' in csvm['header']:
                        self.updateCount(self.fC['h_ctype'], self.get_header_charset(csvm['header']['content-type']))
                    else:
                        self.updateCount(self.fC['h_ctype'], 'missing')
                    self.updateCount(self.fC['h_charset'],res['enc']['header']['encoding'])


                    if enc is None:
                        enc = 'mis'

                    h_enc = self.charset.get(enc, {})
                    if res['enc']['header']['encoding'] is None:
                        self.updateCount(h_enc, 'mis')
                    else:
                        self.updateCount(h_enc, res['enc']['header']['encoding'])
                    self.charset[enc] = h_enc

                else:
                    self.overview['404'] +=1

            else:
                self.overview['errors'] +=1
                self.updateCount(self.fC['errors'], res['error'])
        else:
            #no_res +=1
            self.overview['no_res'] +=1
        if self.overview['total']%5001 == 0:
            #break;
            print 'processed ',self.overview['total'],'files'



    def updateCount(self,count, key, value = 1 ):
        if key and isinstance(key, basestring):
            key = key.lower()
        if key is False:
            key = 'false'
        if key is True:
            key = 'true'
        if key is None:
            key = 'None'
        count[key] = count.get(key , 0) + value


    def get_header_charset(self,cont_type):

        header_encoding = cont_type
        if cont_type and len(cont_type.split(';')) > 1:
            header_encoding = cont_type.split(';')[0]
            header_encoding = header_encoding.strip()
        return header_encoding


