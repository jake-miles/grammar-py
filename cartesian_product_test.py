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
        
    def test_mixed(self):
        cp = cartesian_from_units([Static("abc"), Multiplier(["d","e"]), Static("fgh"), Multiplier(["i","j","k"])])
        # generated with echo abc{d,e}fgh{i,j,k}
        self.assertEqual(cp, ["abcdfghi", "abcdfghj", "abcdfghk", "abcefghi", "abcefghj", "abcefghk"])
        
class TestParseBashCP(unittest.TestCase):

    def test_empty_string(self):
        segments = parse_bash_cp("")
        self.assertEqual(segments, [])

    def test_static(self):
        segments = parse_bash_cp("abc")
        self.assertEqual(segments, [Static("abc")])

    def test_multiplier(self):
        segments = parse_bash_cp("{a,b,c}")
        self.assertEqual(segments, [Multiplier(["a","b","c"])])

    def test_multiplier_one_element(self):
        segments = parse_bash_cp("{a}")
        self.assertEqual(segments, [Multiplier(["a"])])
        
    def test_static_multiplier_static(self):
        segments = parse_bash_cp("abc{d,e,f}ghi{k,l}")
        self.assertEqual(segments, [Static("abc"), Multiplier(["d","e","f"]), Static("ghi"), Multiplier(["k", "l"])])
        
    def test_multiplier_static_multiplier_static(self):
        segments = parse_bash_cp("{a,b,c}def{g,h,i}kl")
        self.assertEqual(segments, [Multiplier(["a","b","c"]), Static("def"), Multiplier(["g","h","i"]), Static("kl")])

    def test_multiplier_multiplier(self):
        segments = parse_bash_cp("{a,b,c}{d,e,f}")
        self.assertEqual(segments, [Multiplier(["a","b","c"]), Multiplier(["d","e","f"])])
    def test_mix(self):
        segments = parse_bash_cp("a{b,c}{d,e}fg{h,i,j}")
        self.assertEqual(segments, [Static("a"), Multiplier(["b","c"]), Multiplier(["d","e"]), Static("fg"), Multiplier(["h","i","j"])])
                                                                                
    
# tests the integration of the parse/compute steps tested above, and pretty-printing.
# also tests the two examples provided with the problem.
class TestBashCP(unittest.TestCase):

    def test_example_1(self):
        cp = bash_cartesian_product("a{b,c}d{e,f,g}hi")
        self.assertEqual(cp, "abdehi abdfhi abdghi acdehi acdfhi acdghi")

    def test_example_2(self):
        cp = bash_cartesian_product("a{b,c{d,e,f}g,h}ij{k,l}")
        self.assertEqual(cp, "abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl")
            
if __name__ == '__main__':
    unittest.main()
    
