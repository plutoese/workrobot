# coding = UTF-8

import unittest
from demo.calculate import Calculate


class TestCalculate(unittest.TestCase):
    def setUp(self):
        self.calc = Calculate()

    def test_add_method(self):
        self.assertEqual(4, self.calc.add(2,2))

if __name__ == '__main__':
    unittest.main()