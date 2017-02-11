import unittest
from cartesian_product import *

class TestCartesianProduct(unittest.TestCase):

    def test_assert_equal(self):
        self.assertEquals([Static("abc"), Multiplier(["x", "y", "z"]), Static("efg")],
                          [Static("abc"), Multiplier(["x", "y", "z"]), Static("efg")])

    def test_assert_not_equal(self):
        self.assertEquals([Static("abc"), Multiplier(["x", "y", "z"]), Static("efg")],
                          [Static("abc1"), Multiplier(["x", "y", "z"]), Static("efg")])

        
class TestParseBashCP(unittest.TestCase):
    pass

# just tests the integration of parsing/computing 
class TestBashCP(unittest.TestCase):
    def test_bash_cp(self):
        cp = bash_cartesian_product("a{b,c}d{e,f,g}hi")
        self.assertEqual(cp, "abdehi abdfhi abdghi acdehi acdfhi acdghi")

if __name__ == '__main__':
    unittest.main()
    
