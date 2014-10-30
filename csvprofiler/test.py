__author__ = 'jumbrich'


import csvprofiler


content, header = csvprofiler.getContentAndHeader(file="../resources/sonnenscheindauer_seit_1906.csv")
csvprofiler.profileCSV(content, header)

content, header = csvprofiler.getContentAndHeader(file="../resources/spielplatzdaten.csv")
csvprofiler.profileCSV(content, header)

content, header = csvprofiler.getContentAndHeader(url='http://opingogn.is/dataset/86bf30b4-a67b-4c42-a7a2-ff9081333e7f/resource/861ec659-7c4c-4c00-bbc0-082bc532f464/download/gjoldsertekjur2010arsfj1.csv')
csvprofiler.profileCSV(content, header)

content, header = csvprofiler.getContentAndHeader(url='http://donnees.ville.sherbrooke.qc.ca/storage/f/2014-03-10T17%3A43%3A58.925Z/matieres-residuelles.csv')
csvprofiler.profileCSV(content, header)
