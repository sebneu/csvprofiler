__author__ = 'sebastian'

import tablemagician

#url = 'http://data.wu.ac.at/dataset/3e4e505f-85cd-4f4c-af43-b547b51fc287/resource/9c2f7b09-f2da-447c-83cd-ea1df37d8e4f/download/allcourses15s.csv'

datatables = tablemagician.from_path('testdata/39.csv')

for t in datatables:
    print t
    anlyser_table = t.process(max_lines=100)
    print anlyser_table
t.close()
