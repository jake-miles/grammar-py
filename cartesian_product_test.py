import unittest

from cartesian_product import bash_cartesian_product

class TestTopLevelScript(unittest.TestCase):
    """
    This just tests the integration of the parse/compute steps 
    tested above, and pretty-printing.

    If all the model and parser tests above pass, it would be very strange 
    if these failed.
    """

    def test_example_1(self):
        cp = bash_cartesian_product("a{b,c}d{e,f,g}hi")
        self.assertEqual(cp, "abdehi abdfhi abdghi acdehi acdfhi acdghi")

    def test_example_2(self):
        cp = bash_cartesian_product("a{b,c{d,e,f}g,h}ij{k,l}")
        self.assertEqual(cp, "abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl")


if __name__ == 'main':
    unittest.main()

