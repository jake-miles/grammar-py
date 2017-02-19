import unittest

from cartesian_product_test_calc import TestCartesianProductCalc
from cartesian_product_test_parse import TestCartesianProductParse

def loadTests(case):
    unittest.TestLoader().loadTestsFromTestCase(case)

class CartesianProductTest:
    def suite():
        return unittest.TestSuite(map(loadTest, [
            CursorTest,
            GrammarTest,
            TestCartesianProductCalc,
            TestCartesianProductParse,
            TestBashCP
        ]))

# just tests the integration of the parse/compute steps tested above, and pretty-printing.
# if all the tests above pass, it would be very strange if these failed.
class TestBashCP(unittest.TestCase):

    def test_example_1(self):
        cp = bash_cartesian_product("a{b,c}d{e,f,g}hi")
        self.assertEqual(cp, "abdehi abdfhi abdghi acdehi acdfhi acdghi")

    def test_example_2(self):
        cp = bash_cartesian_product("a{b,c{d,e,f}g,h}ij{k,l}")
        self.assertEqual(cp, "abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl")


def main():
    unittest.main()

if __name__ == 'main':
    main()
