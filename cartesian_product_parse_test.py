import unittest
from cartesian_product_calc import And, Or, Lit
from cartesian_product_parse import *

class CartesianProductParseTest(unittest.TestCase):
        
    def test_create_cursor_empty_string(self):
        self.assertEqual(create_cursor(""), Cursor([]))

    def test_create_cursor_non_empty_string(self):
        self.assertEqual(create_cursor("abc{def,ghi}jk"), Cursor(["abc", "{", "def", ",", "ghi", "}", "jk"]))    

    def test_parse_nothing_empty_cursor(self):
        self.assertEqual(parse_nothing(Cursor([])), (None, Cursor([])))
        
    def test_parse_nothing_non_empty_cursor(self):
        self.assertEqual(parse_nothing(Cursor([1])), None)

    def test_empty_string(self):
        expr = parse_bash_cp("")
        self.assertEqual(expr, And([]))

    def test_Lit_one_char(self):
        expr = parse_bash_cp("a")
        self.assertEqual(expr, Lit("a"))

    def test_Lit_multiple_chars(self):
        expr = parse_bash_cp("abc")
        self.assertEqual(expr, Lit("abc"))

    def test_Or(self):
        expr = parse_bash_cp("{a,b,c}")
        self.assertEqual(expr, Or([Lit("a"),Lit("b"),Lit("c")]))

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
        self.assertEqual(expr, Or([Lit(""), Lit("de")]))

    def test_Or_second_empty(self):
        expr = parse_bash_cp("abc{de,}")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Lit("de"), Lit("")])]))
        
    def test_Or_all_empty(self):
        expr = parse_bash_cp("abc{,,}de}")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Lit(""), Lit(""), Lit("")]),
                                    Lit("de")]))

    def test_sub_expression(self):
        expr = parse_bash_cp("z{a,{b,c},d}y")
        self.assertEqual(expr, And([Lit("z"),
                                  Or([Lit("a"),
                                      Or([Lit("b"), Lit("c")]),
                                      Lit("d")]),
                                  Lit("y")]))
        
    def test_nested_Or(self):
        expr = parse_bash_cp("{{b,c},d}ef")
        self.assertEqual(expr, And([Or([Or([Lit("b"), Lit("c")]),
                                        Lit("d")]),
                                    Lit("ef")]))

    # when curlies don't contain a comma, they don't denote a Or but a literal that includes the curlies

    def test_literal_open_curly(self):
        expr = parse_bash_cp("{")
        self.assertEqual(expr, Lit("{"))

    def test_literal_close_curly(self):
        expr = parse_bash_cp("}")
        self.assertEqual(expr, Lit("}"))

    def test_literal_open_close_curly(self):
        expr = parse_bash_cp("{}")
        self.assertEqual(expr, Lit("{}"))

    def test_empty_curlies_after_literal(self):
        expr = parse_bash_cp("a{}b")
        self.assertEqual(expr, Lit("a{}b"))

    def test_literal_curlies_containing_subexpr(self):
        expr = parse_bash_cp("a{b{c,d}}")
        self.assertEqual(expr, And([Lit("a{b"), Or([Lit("c"), Lit("d")]), Lit("}")]))

    def test_Or_containing_literal_curly_expression(self):
        expr = parse_bash_cp("{b,{cd}}")
        self.assertEqual(expr, Or([Lit("b"), Lit("{cd}")]))

    def test_literal_open_curly_then_Or(self):
        expr = parse_bash_cp("a{{b,c}")
        self.assertEqual(expr, And([Lit("a{"), Or([Lit("b"), Lit("c")])]))

    def test_literal_open_curly_and_faux_empty_branch(self):
        expr = parse_bash_cp("abc{,de")
        self.assertEqual(expr, Lit("abc{,de"))

    def test_literal_open_curly_and_faux_branch(self):
        expr = parse_bash_cp("ab{c,de")
        self.assertEqual(expr, Lit("abc{,de"))
                         
    def test_second_close_curly_is_literal(self):
        expr = parse_bash_cp("ab{c,d}}")
        self.assertEqual(expr, And([Lit("ab"), Or([Lit("c"), Lit("d")]), Lit("}")]))

    def test_nested_literal_close_curly_no_open(self):
        expr = parse_bash_cp("ab}{c,d}")
        self.assertEqual(expr, And([Lit("ab}"), Or([Lit("c"), Lit("d")])]))
        
    def test_mix(self):
        expr = parse_bash_cp("a{b,c}{d,e}fg{h,{y,z}i,j}")
        self.assertEqual(expr, And([Lit("a"),
                                    Or([Lit("b"),Lit("c")]),
                                    Or([Lit("d"),Lit("e")]),
                                    Lit("fg"),
                                    Or([Lit("h"),
                                        Or([Lit("y"), Lit("z")]), Lit("i"),Lit("j")])]))
                    
if __name__ == '__main__':
    unittest.main()
    
