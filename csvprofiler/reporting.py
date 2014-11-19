__author__ = 'jumbrich'

import os.path
from string import Template
import pandas
import codecs

class Report:

    def __init__(self, csvps, out):
        self.stats = csvps
        self.freqDist = {}
        self.aggregate()
        self.dir_out = os.path.join(out,csvps.id)
        self.createDir(self.dir_out)
        #open the file
        filein = open( '../reports/csv_profiling_templ.tex' )
        #read it
        self.doc = filein.read()



    def aggregate(self):
        for fc in self.stats.fC:
            if fc is 'devs':
                #print self.stats.fC[fc]
                stats ={}
                for k,v, in self.stats.fC[fc].iteritems():
                    kstats={'true':0,'false':0}
                    if 'true' in v:
                        kstats['true']= v['true']
                    if 'false' in v:
                        kstats['false']= v['false']
                    stats[k] = kstats


                t1 = {k:v['true'] for (k,v) in stats.iteritems()}
                f = {k:v['false'] for (k,v) in stats.iteritems()}.values()


                df = pandas.DataFrame(dict(graph=t1.keys(),
                                           value=t1.values()))
                df = df.sort(['value'], ascending=False)
            else:
                df = pandas.DataFrame(dict(graph=self.stats.fC[fc].keys(),
                                           value=self.stats.fC[fc].values()))
                df = df.sort(['value'], ascending=False)
                #print fc

            #print df
            self.freqDist[fc]=df

    def generateReport(self):

        #create tables
        self.overviewTexTable()

        print '______'
        print self.stats.__dict__
        #self.hbarplot(self.freqDist['f_ext'], "fextTable.png")


        self.twoColumTexTable(self.freqDist['f_ext'], "fextTable.tex", 'csv', total= self.stats.overview['total'])
        self.twoColumTexTable(self.freqDist['d_delim'], "delimTable.tex",',')
        self.twoColumTexTable(self.freqDist['h_ctype'], "hctTable.tex",'text/csv')

        self.twoColumTexTable(self.freqDist['h_charset'], "h_charset.tex")
        self.twoColumTexTable(self.freqDist['d_charset'], "d_charset.tex")

        self.deviationColumTexTable(self.freqDist['devs'], "deviations.tex", topK=None)
        self.twoColumTexTable(self.freqDist['errors'], "errors.tex")


        coord = {'TOTALDOCS': self.stats.overview['total'],
                 '404': self.stats.overview['404'],
                 'SUC': self.stats.overview['suc'],
                 'PARSERERROR': self.stats.overview['errors']+self.stats.overview['no_res'],
                 'DATE': self.stats.overview['suc'],
                 }

        for k in coord:
            #print '$'+k+'$', coord[k]
            self.doc = self.doc.replace('$'+k+'$', str(coord[k]))

        file = os.path.join(self.dir_out,"csv_profiler_report.tex")
        print 'Writting overview table to', file
        with codecs.open(file, mode="w", encoding="utf-8") as f:
            f.write(self.doc)



    def overviewTexTable(self):
        overview = self.stats.overview
        total = overview['total']

        table = '\\begin{tabular}{cccc} \n \\toprule \n'
        table+='\\textsc{total} & \\textsc{success} & \\textsc{404} & \\textsc{parser errors} \\\\ \n \\midrule \n'
        table +=str(overview['total'])+'&'+str(overview['suc'])+'&'+str(overview['404'])
        table +='&'+str(overview['errors']+overview['no_res'])+'\\\\ \n'
        if overview['total'] != 0:
            table +='&'+format_percent(overview['suc']/(overview['total']*1.0), tex=True)
            table +='&'+format_percent(overview['404']/(overview['total']*1.0), tex=True)
            table +='&'+format_percent((overview['errors']+overview['no_res'])/(overview['total']*1.0), tex=True)+'\\\\ \n'
        else:
            table +='&'+format_percent(0.0, tex=True)
            table +='&'+format_percent(0.0, tex=True)
            table +='&'+format_percent(0.0, tex=True)+'\\\\ \n'

        table +='\\bottomrule \n \\end{tabular}'

        file = os.path.join(self.dir_out,"overviewTable.tex")
        print 'Writting overview table to', file
        with codecs.open(file, mode="w", encoding="utf-8") as f:
            f.write(table)

    def twoColumTexTable(self, df, fname, boldkey=None, topK=10, total = None):
        #print df
        print fname, topK

        if not total:
            total = self.stats.overview['suc']*1.0


        table = '\\begin{tabular}{lrr} \n \\toprule \n'
        table+=' & \\textsc{\\#docs} & \\\\ \n \\midrule \n'

        iter = df.iterrows()
        if topK:
            iter = df.head(topK).iterrows()

        valuesum =0
        for index, row  in iter:
            value =0.0
            valuesum +=row['value']
            if total !=0:
                #print row['value'],total*1.0, row['value']/(total*1.0)
                value =format_percent(row['value']/(total*1.0), tex=True)
            else:
                value =format_percent(0.0, tex=True)

            if boldkey and boldkey in row['graph']:
                table+= "\\textbf{"+row['graph'].replace('_','\\_').replace('\t','\\\\t')+"}&\\textbf{"+str(row['value'])+' }&('+value+')\\\\ \n  '
            else:
                table+= row['graph'].replace('_','\\_').replace('\t','\\textbackslash t')+"&"+str(row['value'])+' &('+value+')\\\\ \n  '

        if topK and topK < df.shape[0]:
            table +='\\bottomrule \n'
            #print 'bottom others'
            sum = df.ix[10,:]
            #print df
            #print "-----"
            #print sum
            #print 'sum',sum.value.sum()
            #print "-----"
            #print df[10:]
            #print 'sum',df[10:].value.sum()

            sum = df[10:].value.sum()
            valuesum+= sum
            if total != 0:
                table+= "others&"+str(sum)+' &('+format_percent(sum/total, tex=True)+')\\\\ \n  '
            else:
                table+= "others&"+str(sum)+' &('+format_percent(0.0, tex=True)+')\\\\ \n  '


        if valuesum != total:
            print "ERROR: row sum does not match", valuesum, total

        table +='\\bottomrule \n \\end{tabular}'

        file = os.path.join(self.dir_out,fname)
        print 'Writting overview table to', file
        with codecs.open(file, mode="w", encoding="utf-8") as f:
            f.write(table)

    def deviationColumTexTable(self, df, fname, boldkey=None, topK=10, total = None):
        #print df
        if not total:
            total = self.stats.overview['suc']*1.0
        else:
            total = total*1.0

        table = '\\begin{tabular}{lrr} \n \\toprule \n'
        table+=' & \\textsc{\\#docs} & \\\\ \n \\midrule \n'

        hrows=[]
        drows=[]
        trows=[]
        nodevrows=[]
        iter = df.iterrows()
        if topK:
            iter = df.head(topK).iterrows()

        for index, row  in iter:
            if row['graph'].startswith('T'):
                trows.append(row)
            elif row['graph'].startswith('D'):
                drows.append(row)
            elif row['graph'].startswith('H'):
                hrows.append(row)
            else:
                nodevrows.append(row)

        for row in nodevrows:
            table+= row['graph'].replace('_','\\_').replace('\t','\\textbackslash t')+"&"+str(row['value'])+' &('+format_percent(row['value']/total, tex=True)+')\\\\ \n  '
        table +='\\bottomrule \n'

        for row in trows:
            table+= row['graph'].replace('_','\\_').replace('\t','\\textbackslash t')+"&"+str(row['value'])+' &('+format_percent(row['value']/total, tex=True)+')\\\\ \n  '
        table +='\\bottomrule \n'

        for row in hrows:
            table+= row['graph'].replace('_','\\_').replace('\t','\\textbackslash t')+"&"+str(row['value'])+' &('+format_percent(row['value']/total, tex=True)+')\\\\ \n  '
        table +='\\bottomrule \n'

        for row in drows:
            table+= row['graph'].replace('_','\\_').replace('\t','\\textbackslash t')+"&"+str(row['value'])+' &('+format_percent(row['value']/total, tex=True)+')\\\\ \n  '
        table +='\\bottomrule \n \\end{tabular}'

        file = os.path.join(self.dir_out,fname)
        print 'Writting overview table to', file
        with codecs.open(file, mode="w", encoding="utf-8") as f:
            f.write(table)


    def hbarplot(self,df,fname):
        p = ggplot(df, aes(x='graph', y="value"))
        print(p+ geom_point())

    def createDir(self, dName):
        if not os.path.exists(dName):
            os.makedirs(dName)


def format_percent(x, at_least=2, tex = False):

    s = '{0:.2f}'.format(x*100, at_least)
    if s == "0.00":
        s = str(0);
    if s == "100.00":
        s = str(100);
    # The percent symbol needs escaping in latex
    # if plt.rcParams['text.usetex'] == True:
    #    return s + r'$\%$'
    if tex:
        return s + '$\\%$'
    else:
        return s + '%'