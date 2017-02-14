import unittest
from cartesian_product import *

def cartesian_from_terms(units):
    return And(units).product()

class TestCartesianProduct(unittest.TestCase):
    
    def test_no_segments(self):
        cp = cartesian_from_terms([])
        self.assertEqual(cp, [])

    def test_one_static_segment(self):
        cp = cartesian_from_terms([Lit("abc")])
        self.assertEqual(cp, ["abc"])

    def test_multiple_static_segments(self):
        cp = cartesian_from_terms([Lit("abc"), Lit("def"), Lit("ghi")])
        self.assertEqual(cp, ["abcdefghi"])

    def test_single_multiplier(self):
        cp = cartesian_from_terms([Or([Lit("a"),Lit("b"),Lit("c")])])
        self.assertEqual(cp, ["a", "b", "c"])

    def test_nested_multiplier(self):
        # echo z{a,{b,c},d}y
        cp = cartesian_from_terms([Lit("z"),
                                   Or([Lit("a"),
                                       Or([Lit("b"), Lit("c")]),
                                       Lit("d")]),
                                   Lit("y")])
        self.assertEqual(cp, ["zay", "zby", "zcy", "zdy"])

    def test_multiple_multipliers(self):
        # echo {a,b,c}{d,e,f}{g,h,i}
        cp = cartesian_from_terms([Or([Lit("a"), Lit("b"), Lit("c")]),
                                   Or([Lit("d"), Lit("e"), Lit("f")]),
                                   Or([Lit("g"),Lit("h"),Lit("i")])])
        self.assertEqual(cp, ["adg", "adh", "adi", "aeg", "aeh", "aei", "afg", "afh", "afi", "bdg", "bdh", "bdi", "beg", "beh", "bei", "bfg", "bfh", "bfi", "cdg", "cdh", "cdi", "ceg", "ceh", "cei", "cfg", "cfh", "cfi"])
        
    def test_mixed_one_level(self):
        # echo abc{d,e}fgh{i,j,k}
        cp = cartesian_from_terms([Lit("abc"),
                                   Or([Lit("d"),Lit("e")]),
                                   Lit("fgh"),
                                   Or([Lit("i"),Lit("j"),Lit("k")])])
        self.assertEqual(cp, ["abcdfghi", "abcdfghj", "abcdfghk", "abcefghi", "abcefghj", "abcefghk"])

    # echo a{b,c}d{e,f,g}hi
    def test_example_1(self):
        cp = cartesian_from_terms([Lit("a"),Or([Lit("b"),Lit("c")]),Lit("d"),Or([Lit("e"), Lit("f"), Lit("g")]), Lit("hi")])
        self.assertEqual(cp, ["abdehi", "abdfhi", "abdghi", "acdehi", "acdfhi", "acdghi"])
    def test_example_2(self):
        # echo a{b,c{d,e,f}g,h}ij{k,l}
        cp = cartesian_from_terms([Lit("a"),Or([Lit("b"),And([Lit("c"),Or([Lit("d"),Lit("e"),Lit("f")]),Lit("g"),Lit("h")])]),Lit("ij"),Or([Lit("k"),Lit("l")])])
        self.assertEqual(cp, ["abijk", "abijl", "acdgijk", "acdgijl", "acegijk", "acegijl", "acfgijk", "acfgijl", "ahijk", "ahijl"])

        
class TestParseBashCP(unittest.TestCase):

    def test_empty_string(self):
        expr = parse_bash_cp("")
        self.assertEqual(expr, And([]))

    def test_Literal(self):
        expr = parse_bash_cp("abc")
        self.assertEqual(expr, And([Lit("abc")]))

    def test_Or(self):
        expr = parse_bash_cp("{a,b,c}")
        self.assertEqual(expr, And([Or([Lit("a"),Lit("b"),Lit("c")])]))
        
    def test_Literal_Or_Literal(self):
        expr = parse_bash_cp("abc{d,e,f}ghi{k,l}")
        self.assertEqual(expr, And([Lit("abc"), Or([Lit("d"),Lit("e"),Lit("f")]), Lit("ghi"), Or([Lit("k"), Lit("l")])]))
        
    def test_Or_Literal_Or(self):
        expr = parse_bash_cp("{a,b,c}def{g,h,i}kl")
        self.assertEqual(expr, And([Or([Lit("a"),Lit("b"),Lit("c")]), Lit("def"), Or([Lit("g"),Lit("h"),Lit("i")])]))

    def test_Or_Or(self):
        expr = parse_bash_cp("{a,b,c}{d,e,f}")
        self.assertEqual(expr, And([Or([Lit("a"),Lit("b"),Lit("c")]), Or([Lit("d"),Lit("e"),Lit("f")])]))

    def test_disjunction_first_empty(self):
        expr = parse_bash_cp("abc{,de}")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Lit(""), Lit("de")])]))

    def test_disjunction_second_empty(self):
        expr = parse_bash_cp("abc{de,}")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Lit("de"), Lit("")])]))
        
    def test_disjunction_all_empty(self):
        expr = parse_bash_cp("abc{,,}de}")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Lit(""), Lit(""), List("")]),
                                    Lit("de")]))
        
    def test_nested_Or(self):
        expr = parse_bash_cp("z{a,{b,c},d}y")
        self.assertEqual(expr, And([Lit("z"),
                                  Or([Lit("a"),
                                      Or([Lit("b"), Lit("c")]),
                                      Lit("d")]),
                                  Lit("y")]))

    def test_nested_And_beginning_with_Or(self):
        expr = parse_bash_cp("{{a,b}cd,ef}")
        self.assertEqual(expr, Or([And([Or([Lit("a"),Lit("b")]),Lit("cd")]), Lit("ef")]))
 
    # when curlies don't contain a comma, they don't denote a disjunction but a literal enclosed in curlies
        
    def test_empty_curlies(self):
        expr = parse_bash_cp("a{}b{c,d}")
        self.assertEqual(expr, And([Lit("a{}b"), Or([Lit("c"), Lit("d")])]))

    def test_curlies_no_comma(self):
        expr = parse_bash_cp("a{}b{c,d}")
        self.assertEqual(expr, And([Lit("a{}b"), Or([Lit("c"), Lit("d")])]))
        
    def test_nested_literal_curlies_with_subexpr(self):
        expr = parse_bash_cp("a{b{c,d}}")
        self.assertEqual(expr, And([Lit("a{b"), Or([Lit("c"), Lit("d")]), Lit("}")]))

    def test_literal_open_curly_then_disjunction(self):
        expr = parse_bash_cp("a{b{c,d}")
        self.assertEqual(expr, And([Lit("a{b"), Or([Lit("c"), Lit("d")])]))

    def test_literal_open_curly_then_comma(self):
        expr = parse_bash_cp("abc{,de")
        self.assertEqual(expr, Lit("abc{,de"))
        
    def test_nested_literal_close_curly(self):
        expr = parse_bash_cp("ab{c,d}}")
        self.assertEqual(expr, And([Lit("ab"), Or([Lit("c"), Lit("d")]), Lit("}")]))

    def test_nested_literal_close_curly_no_open(self):
        expr = parse_bash_cp("ab}{c,d}")
        self.assertEqual(expr, And([Lit("ab}"), Or([Lit("c"), Lit("d")])]))
        
    def test_mix(self):
        expr = parse_bash_cp("a{b,c}{d,e}fg{h,i,j}")
        self.assertEqual(expr, And([Lit("a"), Or([Lit("b"),Lit("c")]), Or([Lit("d"),Lit("e")]), Lit("fg"), Or([Lit("h"),Lit("i"),Lit("j")])]))
        
# tests the integration of the parse/compute steps tested above, and pretty-printing.
# if all the tests above pass, it would be very strange if these failed.
class TestBashCP(unittest.TestCase):

    def test_example_1(self):
        cp = bash_cartesian_product("a{b,c}d{e,f,g}hi")
        self.assertEqual(cp, "abdehi abdfhi abdghi acdehi acdfhi acdghi")

    def test_example_2(self):
        cp = bash_cartesian_product("a{b,c{d,e,f}g,h}ij{k,l}")
        self.assertEqual(cp, "abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl")
            
if __name__ == '__main__':
    unittest.main()
    
