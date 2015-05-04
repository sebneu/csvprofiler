from column_stats_analyser import ColumnStatsAnalyser

__author__ = 'sebastian'

import unittest
import tablemagician
from complex_type_analyser import ComplexTypeAnalyser
from analyser import AnalyserEngine


class ComplexTypeTest(unittest.TestCase):
    def setUp(self):
        # build analyser table
        data_tables = tablemagician.from_path('../parser/testdata/values.csv')
        self.analyser_table = data_tables[0].process(max_lines=50)
        data_tables[0].close()

        a = ComplexTypeAnalyser()
        b = ColumnStatsAnalyser()

        analyser_chain = [a, b]
        # build engine
        engine = AnalyserEngine(analyser_chain)
        # feed with analyser table
        engine.process(self.analyser_table)


    def test_type_detection(self):
        columns = self.analyser_table.analysers[ComplexTypeAnalyser.name]
        for t in columns[0]:
            self.assertTrue(t.startswith('NUMALPHA'))
        for t in columns[1]:
            self.assertTrue(t.startswith('NUMALPHA'))
        for t in columns[2]:
            self.assertTrue(t.startswith('ALPHANUM'))

        for stats in self.analyser_table.analysers[ColumnStatsAnalyser.name]:
            print 'ColStats:', stats



if __name__ == '__main__':
    unittest.main()
