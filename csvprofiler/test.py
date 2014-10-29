__author__ = 'jumbrich'


import csvprofiler


content, header = csvprofiler.getContentAndHeader(file="../resources/sonnenscheindauer_seit_1906.csv")
csvprofiler.profileCSV(content, header)

content, header = csvprofiler.getContentAndHeader(file="../resources/spielplatzdaten.csv")
csvprofiler.profileCSV(content, header)
