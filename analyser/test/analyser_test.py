__author__ = 'sebastian'

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        Analyser()

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
