import unittest
from cartesian_product import *

def cartesian_from_terms(units):
    return And(units).product()

class TestCartesianProduct(unittest.TestCase):
    
    def test_no_segments(self):
        cp = cartesian_from_terms([])
        self.assertEqual(cp, [])

    def test_one_static_segment(self):
        cp = cartesian_from_terms([Atom("abc")])
        self.assertEqual(cp, ["abc"])

    def test_multiple_static_segments(self):
        cp = cartesian_from_terms([Atom("abc"), Atom("def"), Atom("ghi")])
        self.assertEqual(cp, ["abcdefghi"])

    def test_single_multiplier(self):
        cp = cartesian_from_terms([Or([Atom("a"),Atom("b"),Atom("c")])])
        self.assertEqual(cp, ["a", "b", "c"])

    def test_nested_multiplier(self):
        # echo z{a,{b,c},d}y
        cp = cartesian_from_terms([Atom("z"),
                                   Or([Atom("a"),
                                       Or([Atom("b"), Atom("c")]),
                                       Atom("d")]),
                                   Atom("y")])
        self.assertEqual(cp, ["zay", "zby", "zcy", "zdy"])

    def test_multiple_multipliers(self):
        # echo {a,b,c}{d,e,f}{g,h,i}
        cp = cartesian_from_terms([Or([Atom("a"), Atom("b"), Atom("c")]),
                                   Or([Atom("d"), Atom("e"), Atom("f")]),
                                   Or([Atom("g"),Atom("h"),Atom("i")])])
        self.assertEqual(cp, ["adg", "adh", "adi", "aeg", "aeh", "aei", "afg", "afh", "afi", "bdg", "bdh", "bdi", "beg", "beh", "bei", "bfg", "bfh", "bfi", "cdg", "cdh", "cdi", "ceg", "ceh", "cei", "cfg", "cfh", "cfi"])
        
    def test_mixed_one_level(self):
        # echo abc{d,e}fgh{i,j,k}
        cp = cartesian_from_terms([Atom("abc"),
                                   Or([Atom("d"),Atom("e")]),
                                   Atom("fgh"),
                                   Or([Atom("i"),Atom("j"),Atom("k")])])
        self.assertEqual(cp, ["abcdfghi", "abcdfghj", "abcdfghk", "abcefghi", "abcefghj", "abcefghk"])
        
class TestParseBashCP(unittest.TestCase):

    def test_empty_string(self):
        expr = parse_bash_cp("")
        self.assertEqual(expr, And([]))

    def test_static(self):
        expr = parse_bash_cp("abc")
        self.assertEqual(expr, And([Atom("abc")]))

    def test_multiplier_one_element(self):
        expr = parse_bash_cp("{a}")
        self.assertEqual(expr, And([Or([Atom("a")])]))
        
    def test_multiplier(self):
        expr = parse_bash_cp("{a,b,c}")
        self.assertEqual(expr, And([Or([Atom("a"),Atom("b"),Atom("c")])]))
        
    def test_static_multiplier_static(self):
        expr = parse_bash_cp("abc{d,e,f}ghi{k,l}")
        self.assertEqual(expr, And([Atom("abc"), Or([Atom("d"),Atom("e"),Atom("f")]), Atom("ghi"), Or([Atom("k"), Atom("l")])]))
        
    def test_multiplier_static_multiplier_static(self):
        expr = parse_bash_cp("{a,b,c}def{g,h,i}kl")
        self.assertEqual(expr, And([Or([Atom("a"),Atom("b"),Atom("c")]), Atom("def"), Or([Atom("g"),Atom("h"),Atom("i")]), Atom("kl")]))

    def test_multiplier_multiplier(self):
        expr = parse_bash_cp("{a,b,c}{d,e,f}")
        self.assertEqual(expr, And([Or([Atom("a"),Atom("b"),Atom("c")]), Or([Atom("d"),Atom("e"),Atom("f")])]))

    def test_nested_multiplier(self):
        expr = parse_bash_cp("z{a,{b,c},d}y")
        self.assertEqual(expr, And([Atom("z"),
                                  Or([Atom("a"),
                                      Or([Atom("b"), Atom("c")]),
                                      Atom("d")]),
                                  Atom("y")]))

    # when curlies don't contain a comma, they don't denote a disjunction but a literal enclosed in curlies
        
    def test_literal_empty_curlies(self):
        expr = parse_bash_cp("a{}b{c,d}")
        self.assertEqual(expr, And([Atom("a{}b"), Or([Atom("c"), Atom("d")])]))
        
    def test_nested_literal_curlies_with_subexpr(self):
        expr = parse_bash_cp("a{b{c,d}}")
        self.assertEqual(expr, And([Atom("a{b"), Or([Atom("c"), Atom("d")]), Atom("}")]))

    def test_nested_literal_open_curly(self):
        expr = parse_bash_cp("a{b{c,d}")
        self.assertEqual(expr, And([Atom("a{b"), Or([Atom("c"), Atom("d")])]))

    def test_nested_literal_close_curly(self):
        expr = parse_bash_cp("ab{c,d}}")
        self.assertEqual(expr, And([Atom("ab"), Or([Atom("c"), Atom("d")]), Atom("}")]))

    def test_nested_literal_close_curly_no_open(self):
        expr = parse_bash_cp("ab}{c,d}")
        self.assertEqual(expr, And([Atom("ab}"), Or([Atom("c"), Atom("d")])]))
        
    def test_mix(self):
        expr = parse_bash_cp("a{b,c}{d,e}fg{h,i,j}")
        self.assertEqual(expr, And([Atom("a"), Or([Atom("b"),Atom("c")]), Or([Atom("d"),Atom("e")]), Atom("fg"), Or([Atom("h"),Atom("i"),Atom("j")])]))
        
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
    
