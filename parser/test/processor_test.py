import messytables
import tablemagician
from tablemagician.processor import Processor

__author__ = 'sebastian'

import unittest


class ProcessorTestCase(unittest.TestCase):

    def test_null_counter_processor(self):
        # define processor
        class NullCounterProcessor(Processor):
            def __init__(self):
                self.count = 0

            def visit(self, row_set, row):
                for cell in row:
                    if cell.value == 'NULL':
                        self.count += 1

        p = NullCounterProcessor()

        # create datatables object
        datatables = tablemagician.from_path('testdata/107.csv')
        # use with statement
        with datatables[0] as t:
            t.register_processor(p)
            self.assertEqual(p.count, 0)
            for _ in t.rows:
                pass
            self.assertGreater(p.count, 0)
            print p.count


if __name__ == '__main__':
    unittest.main()
