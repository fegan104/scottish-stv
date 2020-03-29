from rcv import viability_threshold
import unittest
from test import support

class MyTestCase1(unittest.TestCase):

    def test_feature_one(self):
        self.assertTrue(viability_threshold(1, 5) == 2.5)

if __name__ == '__main__':
    unittest.main()