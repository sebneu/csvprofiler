# -*- coding: utf-8 -*-

from column_stats_analyser import ColumnStatsAnalyser

__author__ = 'sebastian'

import unittest
import tablemagician
from complex_type_analyser import ComplexTypeAnalyser
from analyser import AnalyserEngine
import StringIO


class ComplexTypeTest(unittest.TestCase):
    def setUp(self):
        # build analyser table
        data = "c1,c2,c3,c4\n" \
               "12cm,3%,€300.50,\n" \
               "1 cm,1%,€ 12.345,\n" \
               "1.5 cm,0.5%,€ 130,34.2\n" \
               "1 cm,1%,€ 12.345,\n" \
               "1.5 cm,0.5%,€ 130,34.2\n" \
               "1.5 cm,0.5%,€ 130.1000,"

        data_tables = tablemagician.from_file_object(StringIO.StringIO(data))
        self.analyser_table = data_tables[0].process()
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

        self.assertTrue(columns[0]['NUMALPHA/NUMBER/INT:1+-ALPHA:2'] == 2)

        for t in columns[1]:
            self.assertTrue(t.startswith('NUMALPHA'))

        self.assertTrue(columns[1]['NUMALPHA/NUMBER/FLOAT:1.1-ALPHA+:1'] == 3)

        for t in columns[2]:
            self.assertTrue(t.startswith('ALPHANUM'))

        self.assertTrue(columns[2]['ALPHANUM/ALPHA+:1-NUMBER/FLOAT:2.3'] == 2)
        self.assertTrue(columns[2]['ALPHANUM/ALPHA+:1-NUMBER/FLOAT:3.*'] == 1)
        self.assertTrue(columns[3]['EMPTY'] == 4)

        for stats in self.analyser_table.analysers[ColumnStatsAnalyser.name]:
            print 'ColStats:', stats


if __name__ == '__main__':
    unittest.main()
