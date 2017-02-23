import unittest
from cartesian_product_model import *

def test(expr):
    return expr.cartesian_product()

class CartesianProductModelTest(unittest.TestCase):
    
    def test_empty_and(self):
        # echo
        cp = test(And([]))
        self.assertEqual(cp, [])

    def test_one_static_segment(self):
        # echo abc
        cp = test(Lit("abc"))
        self.assertEqual(cp, ["abc"])

    def test_multiple_static_segments(self):
        cp = test(And([Lit("abc"), Lit("{"), Lit("ghi")]))
        self.assertEqual(cp, ["abc{ghi"])

    def test_single_or(self):
        # echo {a,b,c}
        cp = test(Or([Lit("a"),Lit("b"),Lit("c")]))
        self.assertEqual(cp, ["a", "b", "c"])

    def test_lit_or_lit(self):
        # echo a{b,c,d}e
        cp = test(And([Lit("a"),
                       Or([Lit("b"), Lit("c"), Lit("d")]), Lit("e")]))
        self.assertEqual(cp, ["abe", "ace", "ade"])
        
    def test_nested_or(self):
    # echo z{a,{b,c},d}y
        cp = test(And([Lit("z"),
                       Or([Lit("a"),
                           Or([Lit("b"), Lit("c")]),
                           Lit("d")]),
                       Lit("y")]))
        self.assertEqual(cp, ["zay", "zby", "zcy", "zdy"])

    def test_nested_lit_or(self):
        # echo z{a,b{c,d},e}y
        cp = test(And([Lit("z"),
                        Or([Lit("a"),
                            And([Lit("b"), Or([Lit("c"), Lit("d")])]),
                            Lit("e")]),
                        Lit("y")]))
        self.assertEqual(cp, ["zay", "zbcy", "zbdy", "zey"])
        
    def test_or_or_or(self):
        # echo {a,b,c}{d,e,f}{g,h,i}
        cp = test(And([Or([Lit("a"), Lit("b"), Lit("c")]),
                       Or([Lit("d"), Lit("e"), Lit("f")]),
                       Or([Lit("g"),Lit("h"),Lit("i")])]))
        self.assertEqual(cp, ["adg", "adh", "adi", "aeg", "aeh", "aei", "afg", "afh", "afi", "bdg", "bdh", "bdi", "beg", "beh", "bei", "bfg", "bfh", "bfi", "cdg", "cdh", "cdi", "ceg", "ceh", "cei", "cfg", "cfh", "cfi"])
        
    def test_mixed_one_level(self):
        # echo abc{d,e}fgh{i,j,k}
        cp = test(And([Lit("abc"),
                       Or([Lit("d"),Lit("e")]),
                       Lit("fgh"),
                       Or([Lit("i"),Lit("j"),Lit("k")])]))
        self.assertEqual(cp, ["abcdfghi", "abcdfghj", "abcdfghk", "abcefghi", "abcefghj", "abcefghk"])

    # example 1 from the requirements
    # echo a{b,c}d{e,f,g}hi
    def test_example_1(self):
        cp = test(And([Lit("a"),
                       Or([Lit("b"),
                           Lit("c")]),
                       Lit("d"),
                       Or([Lit("e"),
                           Lit("f"),
                           Lit("g")]),
                       Lit("hi")]))

        self.assertEqual(cp, ["abdehi", "abdfhi", "abdghi", "acdehi", "acdfhi", "acdghi"])
        
    # example 2 from the requirements
    def test_example_2(self):
        # echo a{b,c{d,e,f}g,h}ij{k,l}
        cp = test(And([Lit("a"),
                       Or([Lit("b"),
                           And([Lit("c"),
                                Or([Lit("d"),
                                    Lit("e"),
                                    Lit("f")]),
                                Lit("g")]),
                           Lit("h")]),
                       Lit("ij"),
                       Or([Lit("k"),
                           Lit("l")])]))
        
        self.assertEqual(cp, ["abijk", "abijl", "acdgijk", "acdgijl", "acegijk", "acegijl", "acfgijk", "acfgijl", "ahijk", "ahijl"])


