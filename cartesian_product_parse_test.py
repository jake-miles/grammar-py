from cartesian_product_calc import *
from cartesian_product_parse import parse_bash_cp

class CartesianProductParseTest(unittest.TestCase):

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
    
