import unittest
from cartesian_product import *

def cartesian_from_units(units):
    return cartesian_product(map(lambda u: u.toSets(), units))

class TestCartesianProduct(unittest.TestCase):
    
    def test_no_segments(self):
        cp = cartesian_from_units([])
        self.assertEqual(cp, [])

    def test_one_static_segment(self):
        cp = cartesian_from_units([Static("abc")])
        self.assertEqual(cp, ["abc"])

    def test_multiple_static_segments(self):
        cp = cartesian_from_units([Static("abc"), Static("def"), Static("ghi")])
        self.assertEqual(cp, ["abcdefghi"])

    def test_single_multiplier(self):
        cp = cartesian_from_units([Multiplier(["a","b","c"])])
        self.assertEqual(cp, ["a", "b", "c"])
        
    def test_multiple_multipliers(self):
        cp = cartesian_from_units([Multiplier(["a","b","c"]), Multiplier(["d","e","f"]), Multiplier(["g","h","i"])])
        # generated using bash command `echo {a,b,c}{d,e,f}{g,h,i}`
        self.assertEqual(cp, ["adg", "adh", "adi", "aeg", "aeh", "aei", "afg", "afh", "afi", "bdg", "bdh", "bdi", "beg", "beh", "bei", "bfg", "bfh", "bfi", "cdg", "cdh", "cdi", "ceg", "ceh", "cei", "cfg", "cfh", "cfi"])
        
class SomethingElse:    
    def test_mixed(self):
        cp = cartesian_from_units([Static("abc"), Multiplier(["d","e"]), Static("fgh"), Multiplier(["i","j","k"])])
        # generated with echo abc{d,e}fgh{i,j,k}
        self.assertEqual(cp, ["abcdfghi" "abcdfghj" "abcdfghk" "abcefghi" "abcefghj" "abcefghk"])
        
class TestParseBashCP(unittest.TestCase):

    def test_empty_string(self):
        pass

    def test_static(self):
        pass

    def test_multiplier(self):
        pass

    def test_static_multiplier_static(self):
        pass

    def test_multiplier_static_multiplier(self):
        pass

    def test_multiplier_multiplier(self):
        pass

    def test_mix(self):
        pass

    
# just tests the integration of parsing/computing 
class TestBashCP:#(unittest.TestCase):
    def test_bash_cp(self):
        cp = bash_cartesian_product("a{b,c}d{e,f,g}hi")
        self.assertEqual(cp, "abdehi abdfhi abdghi acdehi acdfhi acdghi")

if __name__ == '__main__':
    unittest.main()
    
