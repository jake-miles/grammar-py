import unittest
from cartesian_product_model import And, Or, Lit, Empty
from cartesian_product_parse import *
from grammar import Grammar

class CreateCursor(unittest.TestCase):
    "Tests tokenizing the bash cartesian product input string"
    
    def test_create_cursor_empty_string(self):
        self.assertEqual(create_cursor(""), Cursor([]))

    def test_create_cursor_non_empty_string(self):
        self.assertEqual(create_cursor("abc{def,ghi}jk"),
                         Cursor(["abc", "{", "def", ",", "ghi", "}", "jk"]))    


class BasicCases(unittest.TestCase):

    def test_empty_string(self):
        expr = parse("")
        self.assertEqual(expr, Empty())

    def test_Lit(self):
        expr = parse("abc")
        self.assertEqual(expr, Lit("abc"))

    def test_Or(self):
        expr = parse("{a,b,c}")
        print("expr", expr)
        self.assertEqual(expr, Or([Lit("a"),Lit("b"),Lit("c")]))

    def test_Lit_Or(self):
        expr = parse("abc{d,e,f}")
        self.assertEqual(expr, And([Lit("abc"), Or([Lit("d"),Lit("e"),Lit("f")])]))

    def test_Or_Lit(self):
        expr = parse("{d,e,f}ghi")
        self.assertEqual(expr, And([Or([Lit("d"),Lit("e"),Lit("f")]), Lit("ghi")]))        

    def test_Lit_Or_Lit(self):
        expr = parse("abc{d,e,f}ghi")
        self.assertEqual(expr, And([Lit("abc"), Or([Lit("d"),Lit("e"),Lit("f")]), Lit("ghi")]))

    def test_Or_Lit_Or(self):
        expr = parse("{a,b,c}def{g,h,i}")
        self.assertEqual(expr, And([Or([Lit("a"),Lit("b"),Lit("c")]),
                                    Lit("def"),
                                    Or([Lit("g"),Lit("h"),Lit("i")])]))

    def test_Or_Or(self):
        expr = parse("{a,b,c}{d,e,f}")
        self.assertEqual(expr, And([Or([Lit("a"),Lit("b"),Lit("c")]), Or([Lit("d"),Lit("e"),Lit("f")])]))

    def test_example_1(self):
        "Example 1 in the assignment requirements."
        expr = parse("a{b,c}d{e,f,g}hi")
        self.assertEqual(expr, And([
            Lit("a"),
            Or([Lit("b"), Lit("c")]),
            Lit("d"),
            Or([Lit("e"), Lit("f"), Lit("g")]),
            Lit("hi")
        ]))


class EmptyBranches(unittest.TestCase):

    def test_Or_first_empty(self):
        expr = parse("{,de}")
        self.assertEqual(expr, Or([Empty(), Lit("de")]))

    def test_Or_second_empty(self):
        expr = parse("abc{de,}")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Lit("de"), Empty()])]))
        
    def test_Or_all_empty(self):
        expr = parse("abc{,,}de")
        self.assertEqual(expr, And([Lit("abc"),
                                    Or([Empty(), Empty(), Empty()]),
                                    Lit("de")]))


class ComplexExpressions(unittest.TestCase):
        
    def test_sub_expression(self):
        expr = parse("z{a,{b,c},d}y")
        self.assertEqual(expr, And([Lit("z"),
                                  Or([Lit("a"),
                                      Or([Lit("b"), Lit("c")]),
                                      Lit("d")]),
                                  Lit("y")]))
        
    def test_nested_Or_on_left(self):
        expr = parse("{{b,c},d}ef")
        self.assertEqual(expr, And([Or([Or([Lit("b"), Lit("c")]),
                                        Lit("d")]),
                                    Lit("ef")]))

    def test_nested_Or_on_right(self):
        expr = parse("{b,{c,d},e}")
        self.assertEqual(expr, Or([Lit("b"),
                                   Or([Lit("c"), Lit("d")]),
                                   Lit("e")]))
        
    def test_example_2(self):
        "Example 2 in the assignment requirements"
        expr = parse("a{b,c{d,e,f}g,h}ij{k,l}")
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


class LiteralCurliesAndCommas(unittest.TestCase):
    """
    Test cases of literal open/close curly braces and literal commas.

    To define an Or the parser must find an open curly, at least one comma
    at the "level" of the curly, and a close curly.
    
    Without all three in concert, they are just literals.

    For example:
    > echo ab{cd{e,f}
    ab{cde ab{cdf

    > echo {ef}
    {ef}  

    > echo {ab,cd{e,f}
    {ab,cde {abcdf

    """
        
    def test_literal_open_curly(self):
        expr = parse("{")
        self.assertEqual(expr, Lit("{"))

    def test_literal_close_curly(self):
        expr = parse("}")
        self.assertEqual(expr, Lit("}"))

    def test_literal_comma(self):
        expr = parse(",")
        self.assertEqual(expr, Lit(","))

    def test_literal_open_close_curly(self):
        expr = parse("{}")
        self.assertEqual(expr, And([Lit("{"), Lit("}")]))

    def test_empty_curlies_after_literal(self):
        expr = parse("a{}")
        self.assertEqual(expr, And([Lit("a"), Lit("{"), Lit("}")]))

    def test_literal_open_curly_then_Or(self):
        expr = parse("a{{b,c}")
        self.assertEqual(expr, And([Lit("a"),
                                    Lit("{"),
                                    Or([Lit("b"), Lit("c")])]))

    def test_literal_open_curly_faux_empty_branch(self):
        expr = parse("abc{,de")
        self.assertEqual(expr, And([Lit("abc"), Lit("{"), Lit(","), Lit("de")]))

    def test_literal_open_curly_and_faux_branch(self):
        expr = parse("ab{c,de")
        self.assertEqual(expr, And([Lit("ab"), Lit("{"), Lit("c"), Lit(","), Lit("de")]))
                         
    def test_second_close_curly_is_literal(self):
        expr = parse("ab{c,d}}")
        self.assertEqual(expr, And([Lit("ab"),
                                    Or([Lit("c"), Lit("d")]),
                                    Lit("}")]))

    def test_open_curly_comma(self):
        expr = parse("ab{c,d")
        self.assertEqual(expr, And([Lit("ab"), Lit("{"), Lit("c"), Lit(","), Lit("d")]))

    def test_comma_close_curly(self):
        expr = parse("ab,c}d")
        self.assertEqual(expr, And([Lit("ab"), Lit(","), Lit("c"), Lit("}"), Lit("d")]))

    def test_literal_close_curly_no_open(self):
        expr = parse("ab}{c,d}")
        self.assertEqual(expr, And([Lit("ab"),
                                    Lit("}"),
                                    Or([Lit("c"), Lit("d")])]))

    def test_outer_curlies_have_no_comma(self):
        expr = parse("a{b{c,d}}")
        self.assertEqual(expr, And([Lit("a"),
                                    Lit("{"),
                                    Lit("b"),
                                    Or([Lit("c"), Lit("d")]),
                                    Lit("}")]))

    def test_inner_curlies_have_no_comma(self):
        """
        TODO: BUG: This case reveals a difference in how this parser
        and bash interpret the input string.

        For this input:

        {b,{}}

        bash produces:

        b {}

        and this parser produces:

        b} {}
        
        The issue is that this parser interprets the first close curly brace in 
        this example as the match for the open curly at the start of the string,
        producing the disjunction with branches "b" and "{",
        followed by a literal "}".  So the } in the second resulting string
        is not the inner } being matched, but the inner one being appended to it
        after multiplying the disjunction.

        This is arguably a valid interpretation, because if curlies
        don't include a comma they're just literal curlies, 
        and there's no reason to require or expect literal curlies to match.
        At first I didn't realize it was a bug at all.

        But it is not the behavior of bash, and it is definitely not the 
        intuitive interpretation of the user, who would assume the curly braces 
        balance regardless of whether they denote a disjunction or literal curly braces.
        
        It's not clear to me yet whether this is something that could be fixed
        with an adjustment to the composition of the bash cartesian product grammar
        in `bash_cartesian_product.py`, or whether it requires adding a feature to the 
        underlying grammar library in `grammar.py`.
        """
        expr = parse("{b,{cd}}")
        self.assertEqual(expr, Or([Lit("b"),
                                   And([Lit("{"), Lit("cd"), Lit("}")])]))

                                       
if __name__ == '__main__':
    unittest.main()
    
