__author__ = 'jumbrich'

import os.path

class Report:

    def __init__(self, reportStats, out):
        self.stats = reportStats
        self.dir_out = out
        self.createDir(self.dir_out)


    def generateReport(self):

        #create tables
        self.overviewTexTable()

        self.twoColumTexTable(self.stats['freqDist']['f_ext'], "fextTable.tex", 'csv')
        self.twoColumTexTable(self.stats['freqDist']['d_delim'], "delimTable.tex",',')
        self.twoColumTexTable(self.stats['freqDist']['h_ctype'], "hctTable.tex",'text/csv')

        self.twoColumTexTable(self.stats['freqDist']['h_charset'], "h_charset.tex")
        self.twoColumTexTable(self.stats['freqDist']['d_charset'], "d_charset.tex")

        self.twoColumTexTable(self.stats['freqDist']['devs'], "deviations.tex")
        self.twoColumTexTable(self.stats['freqDist']['errors'], "errors.tex")

    def overviewTexTable(self):
        table = '\\begin{tabular}{cccc} \n \\toprule \n'
        table+='\\textsc{total} & \\textsc{success} & \\textsc{404} & \\textsc{parser errors} \\\\ \n \\midrule \n'
        table +=str(self.stats['overview']['total'])+'&'+str(self.stats['overview']['suc'])+'&'+str(self.stats['overview']['404'])
        table +='&'+str(self.stats['overview']['errors']+self.stats['overview']['no_res'])+'\\\\ \n'
        table +='\\bottomrule \n \\end{tabular}'

        file = os.path.join(self.dir_out,"overviewTable.tex")
        print 'Writting overview table to', file
        with open(file, "w") as f:
            f.write(table)

    def twoColumTexTable(self, df, fname, boldkey=None):
        print df

        table = '\\begin{tabular}{lr} \n \\toprule \n'
        table+=' & \\textsc{\\#docs}  \\\\ \n \\midrule \n'
        for index, row  in df.iterrows():
            if boldkey and boldkey in row['graph']:
                table+= "\\textbf{"+row['graph'].replace('_','\\_')+"}&\\textbf{"+str(row['value'])+'}\\\\ \n  '
            else:
                table+= row['graph'].replace('_','\\_')+"&"+str(row['value'])+'\\\\ \n  '
        table +='\\bottomrule \n \\end{tabular}'

        file = os.path.join(self.dir_out,fname)
        print 'Writting overview table to', file
        with open(file, "w") as f:
            f.write(table)

    def createDir(self, dName):
        if not os.path.exists(dName):
            os.makedirs(dName)