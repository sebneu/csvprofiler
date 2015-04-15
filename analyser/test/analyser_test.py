import traceback
from analyser import AnalyserEngine, Analyser
from complex_type_analyser.extract_datatypes import ComplexTypeAnalyser
from entity_analyser import EntityAnalyser
from structure_analyser import StructureAnalyser
import tablemagician

__author__ = 'sebastian'

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # build analyser table
        data_tables = tablemagician.from_path('../parser/testdata/39.csv')
        analyser_table = data_tables[0].process(max_lines=100)
        data_tables[0].close()

        # test analysers
        a1 = TestAnalyser()
        a2 = AnotherTestAnalyser()
        analyser_chain = [a1, a2]
        # build engine
        engine = AnalyserEngine(analyser_chain)
        # feed with analyser table
        engine.process(analyser_table)

        self.assertEqual(len(analyser_table.analysers), 2)

    def test_structure_analyser(self):
        # build analyser table
        data_tables = tablemagician.from_path('../parser/testdata/nuts/101.csv')
        analyser_table = data_tables[0].process(max_lines=100)
        data_tables[0].close()

        # test structure analysers
        a = StructureAnalyser()

        analyser_chain = [a]
        # build engine
        engine = AnalyserEngine(analyser_chain)
        # feed with analyser table
        engine.process(analyser_table)

    def test_entity_analyser(self):
        # build analyser table
        data_tables = tablemagician.from_path('../parser/testdata/horror/211.csv')
        analyser_table = data_tables[0].process(max_lines=50)
        data_tables[0].close()

        # test structure analysers
        a = EntityAnalyser()

        analyser_chain = [a]
        # build engine
        engine = AnalyserEngine(analyser_chain)
        # feed with analyser table
        engine.process(analyser_table)

    def test_complextype_analyser(self):
        # build analyser table
        data_tables = tablemagician.from_path('../parser/testdata/nuts/101.csv')
        analyser_table = data_tables[0].process(max_lines=50)
        data_tables[0].close()

        # test structure analysers
        a = ComplexTypeAnalyser()

        analyser_chain = [a]
        # build engine
        engine = AnalyserEngine(analyser_chain)
        # feed with analyser table
        engine.process(analyser_table)


if __name__ == '__main__':
    unittest.main()


class TestAnalyser(Analyser):
    def process(self, analyser_table):
        analyser_table.analysers['a1'] = 'TestAnalyser'


class AnotherTestAnalyser(Analyser):
    def process(self, analyser_table):
        analyser_table.analysers['a2'] = 'AnotherTestAnalyser'
