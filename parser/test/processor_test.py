import tablemagician
from tablemagician.processor import Processor

__author__ = 'sebastian'

import unittest


class ProcessorTestCase(unittest.TestCase):
    def test_null_counter_processor(self):
        # create datatables object
        datatables = tablemagician.from_path('testdata/107.csv')
        # use with statement
        with datatables[0] as t:
            # register processor
            p = NullCounterProcessor(t)

            self.assertEqual(p.count, 0)
            # iterate to apply processor
            analyser_table = t.process()
            self.assertGreater(p.count, 0)
            print p.count

    def test_inherit_null_counter_processor(self):
        # create datatables object
        datatables = tablemagician.from_path('testdata/107.csv')
        # use with statement
        for t in datatables:
            # register processor
            p = InheritNullCounterProcessor(t)

            self.assertEqual(p.count, 0)
            # iterate to apply processor
            analyser_table = t.process()
            self.assertLess(p.count, 0)
            print p.count
        t.close()

    def test_use_null_counter_result_processor(self):
        # create datatables object
        datatables = tablemagician.from_path('testdata/107.csv')
        # use with statement
        with datatables[0] as t:
            # register processor
            p = UseNullCounterStateProcessor(t)

            # iterate to apply processor
            analyser_table = t.process()
            print p.count
            print p.avg
            print p.avg/p.count


if __name__ == '__main__':
    unittest.main()


class NullCounterProcessor(Processor):
    def __init__(self, datatable):
        self.count = 0
        super(NullCounterProcessor, self).__init__(datatable=datatable)

    def visit(self, row_set, row):
        for cell in row:
            if cell.value == 'NULL':
                self.count += 1
        return row


class InheritNullCounterProcessor(NullCounterProcessor):
    def visit(self, row_set, row):
        for cell in row:
            if cell.value == 'NULL':
                self.count -= 1
        return row


class UseNullCounterStateProcessor(Processor):
    def __init__(self, datatable):
        self.count = 0.0
        self.avg = 0.0
        # require NullCounterProcessor
        self.null_counter = datatable.get_processor(NullCounterProcessor)
        if not self.null_counter:
            self.null_counter = NullCounterProcessor(datatable)
        super(UseNullCounterStateProcessor, self).__init__(datatable=datatable)

    def visit(self, row_set, row):
        self.count += 1
        avg_null_per_row = self.null_counter.count/self.count
        self.avg += avg_null_per_row/len(row)
        return row
