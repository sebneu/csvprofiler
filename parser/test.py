import os
import traceback
from analyser import AnalyserEngine
from column_stats_analyser import ColumnStatsAnalyser
from complex_type_analyser import ComplexTypeAnalyser

__author__ = 'sebastian'

import tablemagician

#url = 'http://data.wu.ac.at/dataset/3e4e505f-85cd-4f4c-af43-b547b51fc287/resource/9c2f7b09-f2da-447c-83cd-ea1df37d8e4f/download/allcourses15s.csv'
rootdir = 'testdata/nuts'

# Build analysers
comp = ComplexTypeAnalyser()
col = ColumnStatsAnalyser()
engine = AnalyserEngine([comp, col])

data = []

# Load a path:
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        print file
        try:
            datatables = tablemagician.from_path(os.path.join(rootdir, file))

            for t in datatables:
                analyser_table = t.process(max_lines=50)
                engine.process(analyser_table)
                stats = analyser_table.analysers[ColumnStatsAnalyser.name]
                data.append({'name': file, 'header': analyser_table.headers, 'stats': stats})

            t.close()
        except Exception as e:
            print(file + ' - ' + str(e))
            print(traceback.format_exc())
            with open('errors.txt', 'wb') as f:
                f.write(file + ' - ' + str(e))
                f.write(traceback.format_exc())

    break


