__author__ = 'jumbrich'

import os.path
from string import Template


class Report:

    def __init__(self, reportStats, out):
        self.stats = reportStats
        self.dir_out = out
        self.createDir(self.dir_out)
        #open the file
        filein = open( '../reports/csv_profiling_templ.tex' )
        #read it
        self.doc =  filein.read()


    def generateReport(self):

        #create tables
        self.overviewTexTable()

        #self.hbarplot(self.stats['freqDist']['f_ext'], "fextTable.png")
        self.twoColumTexTable(self.stats['freqDist']['f_ext'], "fextTable.tex", 'csv', total= self.stats['overview']['total'])
        self.twoColumTexTable(self.stats['freqDist']['d_delim'], "delimTable.tex",',')
        self.twoColumTexTable(self.stats['freqDist']['h_ctype'], "hctTable.tex",'text/csv')

        self.twoColumTexTable(self.stats['freqDist']['h_charset'], "h_charset.tex")
        self.twoColumTexTable(self.stats['freqDist']['d_charset'], "d_charset.tex")

        self.deviationColumTexTable(self.stats['freqDist']['devs'], "deviations.tex", topK=None)
        self.twoColumTexTable(self.stats['freqDist']['errors'], "errors.tex")


        coord = {'TOTALDOCS': self.stats['overview']['total'],
                 '404': self.stats['overview']['404'],
                 'SUC': self.stats['overview']['suc'],
                 'PARSERERROR': self.stats['overview']['errors']+self.stats['overview']['no_res'],
                 'DATE': self.stats['overview']['suc'],
                 }

        for k in coord:
            print '$'+k+'$', coord[k]
            self.doc = self.doc.replace('$'+k+'$', str(coord[k]))

        file = os.path.join(self.dir_out,"csv_profiler_report.tex")
        print 'Writting overview table to', file
        with open(file, "w") as f:
            f.write(self.doc)



    def overviewTexTable(self):
        overview = self.stats['overview']
        table = '\\begin{tabular}{cccc} \n \\toprule \n'
        table+='\\textsc{total} & \\textsc{success} & \\textsc{404} & \\textsc{parser errors} \\\\ \n \\midrule \n'
        table +=str(overview['total'])+'&'+str(overview['suc'])+'&'+str(overview['404'])
        table +='&'+str(overview['errors']+overview['no_res'])+'\\\\ \n'
        
        table +='&'+format_percent(overview['suc']/(overview['total']*1.0), tex=True)+'&'+format_percent(overview['404']/(overview['total']*1.0), tex=True)
        table +='&'+format_percent((overview['errors']+overview['no_res'])/(overview['total']*1.0), tex=True)+'\\\\ \n'
        table +='\\bottomrule \n \\end{tabular}'

        file = os.path.join(self.dir_out,"overviewTable.tex")
        print 'Writting overview table to', file
        with open(file, "w") as f:
            f.write(table)

    def twoColumTexTable(self, df, fname, boldkey=None, topK=10, total = None):
        #print df
        print fname, topK

        if not total:
            total = self.stats['overview']['suc']*1.0


        table = '\\begin{tabular}{lrr} \n \\toprule \n'
        table+=' & \\textsc{\\#docs} & \\\\ \n \\midrule \n'

        iter = df.iterrows()
        if topK:
            iter = df.head(topK).iterrows()

        for index, row  in iter:
            if boldkey and boldkey in row['graph']:
                table+= "\\textbf{"+row['graph'].replace('_','\\_').replace('\t','\\\\t')+"}&\\textbf{"+str(row['value'])+' }&('+format_percent(row['value']/total, tex=True)+')\\\\ \n  '
            else:
                table+= row['graph'].replace('_','\\_').replace('\t','\\textbackslash t')+"&"+str(row['value'])+' &('+format_percent(row['value']/total, tex=True)+')\\\\ \n  '
        if topK and topK < df.shape[0]:
            table +='\\bottomrule \n'
            print 'bottom others'
            sum = df.ix[10,:]
            sum = sum.value.sum()
            table+= "others&"+str(sum)+' &('+format_percent(sum/total, tex=True)+')\\\\ \n  '


        table +='\\bottomrule \n \\end{tabular}'

        file = os.path.join(self.dir_out,fname)
        #print 'Writting overview table to', file
        #with open(file, "w") as f:
            #f.write(table)

    def deviationColumTexTable(self, df, fname, boldkey=None, topK=10, total = None):
        #print df


        if not total:
            total = self.stats['overview']['suc']*1.0


        table = '\\begin{tabular}{lrr} \n \\toprule \n'
        table+=' & \\textsc{\\#docs} & \\\\ \n \\midrule \n'

        hrows=[]
        drows=[]
        trows=[]
        iter = df.iterrows()
        if topK:
            iter = df.head(topK).iterrows()

        for index, row  in iter:
            if row['graph'].startswith('T'):
                trows.append(row)
            elif row['graph'].startswith('D'):
                drows.append(row)
            else:
                hrows.append(row)

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
        with open(file, "w") as f:
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