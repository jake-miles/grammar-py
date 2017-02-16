import unittest

from cartesian_product_test_calc import TestCartesianProductCalc
from cartesian_product_test_parse import TestCartesianProductParse

def loadTests(case):
    unittest.TestLoader().loadTestsFromTestCase(case)

class CartesianProductTest:
    def suite():
        return unittest.TestSuite([
            loadTests(TestCartesianProductCalc),
            loadTests(TestCartesianProductParse)
        ])

def main():
    unittest.main()

if __name__ == 'main':
    main()
