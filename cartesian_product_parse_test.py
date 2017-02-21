import unittest
from cartesian_product_calc import And, Or, Lit, Empty
from cartesian_product_parse import *
from grammar import Grammar

class ParseSaneCasesTest(unittest.TestCase):
    
    def test_create_cursor_empty_string(self):
        self.assertEqual(create_cursor(""), Cursor([]))

    def test_create_cursor_non_empty_string(self):
        self.assertEqual(create_cursor("abc{def,ghi}jk"), Cursor(["abc", "{", "def", ",", "ghi", "}", "jk"]))    

    def test_empty_string(self):
        expr = parse_bash_cp("")
        self.assertEqual(expr, Empty())

    def test_Lit(self):
        expr = parse_bash_cp("abc")
        self.assertEqual(expr, Lit("abc"))

    def test_Or(self):
        expr = parse_bash_cp("{a,b,c}")
        print("expr", expr)
        self.assertEqual(expr, Or([Lit("a"),Lit("b"),Lit("c")]))

    def test_Lit_Or(self):
        expr = parse_bash_cp("abc{d,e,f}")
        self.assertEqual(expr, And([Lit("abc"), Or([Lit("d"),Lit("e"),Lit("f")])]))

    def test_Or_Lit(self):
        expr = parse_bash_cp("{d,e,f}ghi")
        self.assertEqual(expr, And([Or([Lit("d"),Lit("e"),Lit("f")]), Lit("ghi")]))        

    def test_Lit_Or_Lit(self):
        expr = parse_bash_cp("abc{d,e,f}ghi")
        self.assertEqual(expr, And([Lit("abc"), Or([Lit("d"),Lit("e"),Lit("f")]), Lit("ghi")]))

    def test_Or_Lit_Or(self):
        expr = parse_bash_cp("{a,b,c}def{g,h,i}")
        self.assertEqual(expr, And([Or([Lit("a"),Lit("b"),Lit("c")]),
                                    Lit("def"),
                                    Or([Lit("g"),Lit("h"),Lit("i")])]))

    def test_Or_Or(self):
        expr = parse_bash_cp("{a,b,c}{d,e,f}")
        self.assertEqual(expr, And([Or([Lit("a"),Lit("b"),Lit("c")]), Or([Lit("d"),Lit("e"),Lit("f")])]))
###                
    def test_Or_first_empty(self):
        expr = parse_bash_cp("{,de}")
        self.assertEqual(expr, Or([Empty(), Lit("de")]))

    def test_Or_second_empty(self):
        expr = parse_bash_cp("abc{de,}")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Lit("de"), Empty()])]))
        
    def test_Or_all_empty(self):
        expr = parse_bash_cp("abc{,,}de")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Empty(), Empty(), Empty()]),
                                    Lit("de")]))

    def test_sub_expression(self):
        expr = parse_bash_cp("z{a,{b,c},d}y")
        self.assertEqual(expr, And([Lit("z"),
                                  Or([Lit("a"),
                                      Or([Lit("b"), Lit("c")]),
                                      Lit("d")]),
                                  Lit("y")]))
        
    def test_nested_Or_on_left(self):
        expr = parse_bash_cp("{{b,c},d}ef")
        self.assertEqual(expr, And([Or([Or([Lit("b"), Lit("c")]),
                                        Lit("d")]),
                                    Lit("ef")]))

    def test_nested_Or_on_right(self):
        expr = parse_bash_cp("{b,{c,d},e}")
        self.assertEqual(expr, Or([Lit("b"),
                                   Or([Lit("c"), Lit("d")]),
                                   Lit("e")]))
    def test_example_1(self):
        expr = parse_bash_cp("a{b,c}d{e,f,g}hi")
        self.assertEqual(expr, And([
            Lit("a"),
            Or([Lit("b"), Lit("c")]),
            Lit("d"),
            Or([Lit("e"), Lit("f"), Lit("g")]),
            Lit("hi")
        ]))

    def test_example_2(self):
        expr = parse_bash_cp("a{b,c{d,e,f}g,h}ij{k,l}")
        self.assertEqual(expr, And([
            Lit("a"),
            Or([Lit("b"),
                And([Lit("c"),
                     Or([Lit("d"), Lit("e"), Lit("f")]),
                     Lit("g")]),
                Lit("h")
            ]),
            Lit("ij"),
            Or([Lit("k"), Lit("l")])
        ]))


# when curlies don't contain a comma,
# they don't denote a Or but a literal that includes the curlies.
# same goes for open and close curlies with no match.
class ParseLiteralCurliesTest(unittest.TestCase):
        
    def test_literal_open_curly(self):
        expr = parse_bash_cp("{")
        self.assertEqual(expr, Lit("{"))

    def test_literal_close_curly(self):
        expr = parse_bash_cp("}")
        self.assertEqual(expr, Lit("}"))

    def test_literal_open_close_curly(self):
        expr = parse_bash_cp("{}")
        self.assertEqual(expr, And([Lit("{"), Lit("}")]))

    def test_empty_curlies_after_literal(self):
        expr = parse_bash_cp("a{}b")
        self.assertEqual(expr, And([Lit("a"), Lit("{"), Lit("}"), Lit("b")]))

    def test_literal_curlies_containing_subexpr(self):
        expr = parse_bash_cp("a{b{c,d}}")
        self.assertEqual(expr, And([Lit("a"), Lit("{"), Lit("b"), Or([Lit("c"), Lit("d")]), Lit("}")]))

    def test_Or_containing_literal_curly_expression(self):
        # this one's wacky - the first close curly closes the Or.  the second is Lit.
        expr = parse_bash_cp("{b,{cd}}")
        self.assertEqual(expr, And([Or([Lit("b"), And([Lit("{"), Lit("cd")])]), Lit("}")]))

    def test_literal_open_curly_then_Or(self):
        expr = parse_bash_cp("a{{b,c}")
        self.assertEqual(expr, And([Lit("a"), Lit("{"), Or([Lit("b"), Lit("c")])]))

    def test_literal_open_curly_faux_empty_branch(self):
        expr = parse_bash_cp("abc{,de")
        self.assertEqual(expr, And([Lit("abc"), Lit("{"), Lit(","), Lit("de")]))

    def test_literal_open_curly_and_faux_branch(self):
        expr = parse_bash_cp("ab{c,de")
        self.assertEqual(expr, And([Lit("ab"), Lit("{"), Lit("c"), Lit(","), Lit("de")]))
                         
    def test_second_close_curly_is_literal(self):
        expr = parse_bash_cp("ab{c,d}}")
        self.assertEqual(expr, And([Lit("ab"), Or([Lit("c"), Lit("d")]), Lit("}")]))

    def test_literal_close_curly_no_open(self):
        expr = parse_bash_cp("ab}{c,d}")
        self.assertEqual(expr, And([Lit("ab"), Lit("}"), Or([Lit("c"), Lit("d")])]))
        
    def test_mix(self):
        expr = parse_bash_cp("a{b,c}{d,e}fg{h,{y,z}i,j}")
        self.assertEqual(expr, And([Lit("a"),
                                    Or([Lit("b"),Lit("c")]),
                                    Or([Lit("d"),Lit("e")]),
                                    Lit("fg"),
                                    Or([Lit("h"),
                                        And([Or([Lit("y"),
                                                 Lit("z")]),
                                             Lit("i")]),
                                        Lit("j")])]))
        
if __name__ == '__main__':
    unittest.main()
    
