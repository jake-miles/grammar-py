import unittest
from grammar import *
from cursor import Cursor
import re

class GrammarTest(unittest.TestCase):

    def suite(self):
        return unittest.TestSuite(map(loadTests, [
            LazyTest,
            ResultTest,
            AnyTokenTest,
            TokenTest,
            OneOrMoreTest,
            MoreThanOneTest,
            AllOfTest,
            OneOfTest,
            MapResultTest,
            KeepAsTest,
            ClearTest,
            GrammarTest
        ]))
        
class ResultTest(unittest.TestCase):

    def test_merge_all_merges_values_into_list(self):
        result1 = Result("result1")
        result2 = Result("result2")
        result3 = Result("result3")
        merged = Result.merge_all([result1, result2, result3])
        self.assertEqual(merged, Result(["result1", "result2", "result3"]))

    def test_merge_all_merges_keeps(self):
        result1 = Result("result1", { 'a': 1 })
        result2 = Result("result2", { 'b': 2 })
        result3 = Result("result3", { 'c': 3 })
        merged = Result.merge_all([result1, result2, result3])
        self.assertEqual(merged, Result(["result1", "result2", "result3"], { 'a': 1, 'b': 2, 'c': 3 }))


class AnyTokenTest(unittest.TestCase):    
    def test_match_token(self):
        grammar = AnyToken() 
        input = Cursor(["hello"])
        (result, end) = grammar.parse(input)
        self.assertEqual(result.value, "hello")
        self.assertTrue(end.empty())                 

        
class TokenTest(unittest.TestCase):

    def test_specified_token_match(self):
        grammar = Token("hello")
        input = Cursor(["hello"])
        (result, end) = grammar.parse(input)        
        self.assertEqual(result.value, "hello")
        self.assertTrue(end.empty())

    def test_different_token_no_match(self):
        grammar = Token("goodbye")
        input = Cursor(["hello"])
        (result, end) = grammar.parse(input)                
        self.assertFalse(result)
        self.assertEqual(end, input)

        
class AllOfTest(unittest.TestCase):

    grammar = AllOf([Token("hello"), Token("goodbye"), Token("sunshine")])
    
    def test_empty_input_no_match(self):
        input = Cursor([])
        (result, end) = AllOfTest.grammar.parse(input)
        self.assertFalse(result)    
        self.assertEqual(end, input)
        
    def test_no_match_input_shorter_than_grammar(self):
        input = Cursor(["hello", "goodbye"])
        (result, end) = AllOfTest.grammar.parse(input)
        self.assertFalse(result)    
        self.assertEqual(end, input)
        
    def test_one_matched_token_no_match(self):
        input = Cursor(["hello"])
        (result, end) = AllOfTest.grammar.parse(input)        
        self.assertFalse(result)
        self.assertEqual(end, input)
        
    def test_two_matched_tokens_no_match(self):
        input = Cursor(["hello", "goodbye", "rain", "clouds"])
        (result, end) = AllOfTest.grammar.parse(input)        
        self.assertFalse(result)
        self.assertEqual(end, input)
        
    def test_all_match(self):
        input = Cursor(["hello", "goodbye", "sunshine", "rain", "clouds"])
        (result, end) = AllOfTest.grammar.parse(input)
        # Result.value is just True for this one - to retain values use `keep`
        self.assertEqual(result, Result(["hello", "goodbye", "sunshine"]))
        self.assertEqual(end, input.at(3))

                
class OneOrMoreTest(unittest.TestCase):

    def test_zero_no_match(self):
        grammar = OneOrMore(Token("sunshine"))        
        input = Cursor(["hello", "goodbye", "sunshine"])
        (result, end) = grammar.parse(input)
        self.assertFalse(result)
        self.assertEqual(end, input)
        
    def test_one_match(self):
        grammar = OneOrMore(Token("hello"))
        input = Cursor(["hello", "goodbye", "sunshine"])        
        (result, end) = grammar.parse(input)
        self.assertEqual(result.value, ["hello"])
        self.assertEqual(end, input.at(1))
        
    def test_two_match(self):
        grammar = OneOrMore(Token("hello"))
        input = Cursor(["hello", "hello", "goodbye"])        
        (result, end) = grammar.parse(input)
        self.assertEqual(result.value, ["hello", "hello"])
        self.assertEqual(end, input.at(2))
        
    def test_more_than_two_match(self):
        grammar = OneOrMore(Token("hello"))
        input = Cursor(["hello", "hello", "hello", "goodbye"])        
        (result, end) = grammar.parse(input)
        self.assertEqual(result.value, ["hello", "hello", "hello"])
        self.assertEqual(end, input.at(3))

                
class MoreThanOneTest(unittest.TestCase):

    def test_zero_no_match(self):
        grammar = MoreThanOne(Token("sunshine"))
        input = Cursor(["hello", "goodbye", "sunshine"])
        (result, end) = grammar.parse(input)
        self.assertFalse(result)
        self.assertEqual(end, input)
        
    def test_one_no_match(self):
        grammar = MoreThanOne(Token("hello"))
        input = Cursor(["hello", "goodbye", "sunshine"])
        (result, end) = grammar.parse(input)
        self.assertFalse(result)
        self.assertEqual(end, input)
        
    def test_two_match(self):
        grammar = MoreThanOne(Token("hello"))
        input = Cursor(["hello", "hello", "goodbye", "sunshine"])
        (result, end) = grammar.parse(input)
        self.assertEqual(result.value, ["hello", "hello"])
        self.assertEqual(end, input.at(2))
        
    def test_more_than_two_match(self):
        grammar = MoreThanOne(Token("hello"))
        input = Cursor(["hello", "hello", "hello", "goodbye", "sunshine"])
        (result, end) = grammar.parse(input)
        self.assertEqual(result.value, ["hello", "hello", "hello"])
        self.assertEqual(end, input.at(3))

        
class OneOfTest(unittest.TestCase):

    grammar = OneOf([Token("hello"), Token("goodbye"), Token("sunshine")])
    
    def test_no_match(self):
        input = Cursor(["rain", "hello"])
        (result, end) = OneOfTest.grammar.parse(input)
        self.assertFalse(result)
        self.assertEqual(end, input)
        
    def test_first_option_match(self):
        input = Cursor(["hello", "rain"])
        (result, end) = OneOfTest.grammar.parse(input)
        self.assertEqual(result.value, "hello")
        self.assertEqual(end, input.at(1))
        
    def test_middle_option_match(self):
        input = Cursor(["goodbye", "rain"])
        (result, end) = OneOfTest.grammar.parse(input)
        self.assertEqual(result.value, "goodbye")
        self.assertEqual(end, input.at(1))
        
    def test_last_option_match(self):
        input = Cursor(["sunshine", "rain"])
        (result, end) = OneOfTest.grammar.parse(input)
        self.assertEqual(result.value, "sunshine")
        self.assertEqual(end, input.at(1))


class LazyTest(unittest.TestCase):

    def test_passes_through_to_grammar(self):
        a = Lazy(lambda: Token("c"))
        (result, end) = a.parse(Cursor(["c"]))
        self.assertEqual(result.value, "c")
        self.assertTrue(end.empty())

        
class KeepTest(unittest.TestCase):

    def test_adds_key(self):
        (result, end) = AnyToken().keep('key').parse(Cursor(["a"]))
        self.assertEqual(result, Result("a", { 'key': 'a' }))

    def test_use_with_all_of(self):
        grammar = AllOf([Token("hello").keep('h'), Token("goodbye"), Token("sunshine").keep('s')])
        (result, cursor) = grammar.parse(Cursor(["hello", "goodbye", "sunshine"]))
        self.assertEqual(result, Result(["hello", "goodbye", "sunshine"],
                                        { 'h': 'hello', 's': 'sunshine' }))
        
        
class MapTest(unittest.TestCase):

    def test_does_not_map_falsy_value(self):
        (result, end) = Token("c").map(lambda v, keeps: v + "b").parse(Cursor(["a"]))
        self.assertFalse(result)
    
    def test_maps_value(self):
        (result, end) = AnyToken().map(lambda v, keeps: v + "b").parse(Cursor(["a"]))
        self.assertEqual(result, Result("ab"))

        
class ClearTest(unittest.TestCase):

    def test_clears_keeps(self):
        (result, end) = AnyToken().keep('key').clear().parse(Cursor(["a"]))        
        self.assertEqual(result, Result("a"))



# AST classes for a limited arithmetic expression tree
    
class Arithmetic(Grammar):

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
class Number(Arithmetic):
    
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Number(" + str(self.value) + ")"
        
    @staticmethod
    def fromResult(n, keeps):
        return Number(n)
            
class Negate(Arithmetic):
    
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Negate(" + self.value + ")"
        
    @staticmethod            
    def fromResult(n, keeps):
        return Negate(n)
            
class Add(Arithmetic):

    def __init__(self, terms):
        self.terms = terms

    def __repr__(self):
        return "Add(" + str(self.terms) + ")"

    @staticmethod
    def fromResult(terms, keeps):
        return Add(keeps['left'].append(keeps['right']))
        
    
class GrammarTest(unittest.TestCase):

    def test_empty_no_match(self):
        grammar = AnyToken()
        (result, end) = grammar.parse(Cursor([]))
        self.assertFalse(result)
    
    def test_map(self):
        grammar = AnyToken()
        (result, end) = grammar.map(lambda n, ks: n + "a").parse(Cursor(["5"]))
        self.assertEqual(result, Result("5a"))

    def test_keep(self):
        grammar = AnyToken()
        (result, end) = grammar.keep('n').parse(Cursor(["5"]))
        self.assertEqual(result, Result("5", { 'n': "5" }))

    def test_clear(self):
        grammar = AnyToken()
        (result, end) = grammar.keep('n').clear().parse(Cursor(["5"]))
        self.assertEqual(result, Result("5"))
            
    # grammar for the limited arithmetic expression tree
            
    number = AnyToken().map(lambda n,_: int(n)).map(Number.fromResult)

    negation = AllOf([Token("-"), number.keep('n')]).map(Negate.fromResult)

    expr = OneOf([number, negation, Lazy(lambda: add)])
    
    add = AllOf([expr.keep('left'), Token("+"), expr.keep('right')]).map(Add.fromResult)
    
    paren_expr = AllOf([Token("("), OneOrMore(expr).keep('expr')])

    def to_cursor(self, string):
        tokens = re.split('([()+-])', string)
        non_empty = [token for token in tokens if token != ""]
        return Cursor(non_empty)
    
    def test_primitive(self):
        (result, _) = GrammarTest.number.parse(self.to_cursor("34"))
        self.assertEqual(result, Result(Number(34)))

    def test_prefix_discriminator_match(self):
        (result, _) = GrammarTest.negation.parse(self.to_cursor("-5"))
        self.assertEqual(result, Result(Negate(Number(5))))

    def test_prefix_discriminator_no_match(self):
        (result, _) = GrammarTest.negation.parse(self.to_cursor("5"))
        self.assertFalse(result)
        
    def test_infix_discriminator_match(self):
        (result, _) = GrammarTest.add.parse(self.to_cursor("5 + 6"))
        self.assertEqual(result, Result(Add(5, 6)))

    def test_infix_discriminator_no_op_no_match(self):
        (result, _) = GrammarTest.add.parse(self.to_cursor("5 6"))
        self.assertFalse(result)

    def test_infix_discriminator_no_right_term_no_match(self):
        (result, _) = GrammarTest.add.parse(self.to_cursor("5 +"))
        self.assertFalse(result)
            
    def test_bracketed_expr(self):
        (result, _) = GrammarTest.paren_expr.parse(self.to_cursor("(5)"))
        self.assertEqual(result, Result(True, { 'expr': Number(5) }))

    def test_bracketed_expr_no_right_bracket_no_match(self):
        (result, _) = GrammarTest.paren_expr.parse(self.to_cursor("(5"))
        self.assertFalse(result)

    def test_multiple_infix(self):
        (result, _) = OneOrMore(GrammarTest.add).parse(self.to_cursor("5 + 6 + 7"))
        self.assertEqual(result,
                         Result([Add(Number("5"), Add(Number("6"), Number("7")))]))

    def test_multiple_infix_no_last_term_no_match(self):
        (result, _) = OneOrMore(GrammarTest.add).parse(self.to_cursor("5 + 6 +"))
        self.assertFalse(result)

    def test_nested_bracket(self):
        (result, _) = GrammarTest.paren_expr.parse(self.to_cursor("5 + (6 + 7)"))
        self.assertEqual(result, Result([Add(Number(5), Add(Number(6), Number(7)))]))

    def test_nested_bracket_no_right_inner_bracket_no_match(self):
        (result, _) = GrammarTest.paren_expr.parse(self.to_cursor("5 + (6 + )"))
        self.assertFalse(result)
    
    def test_complex_expression(self):
        (result, _) = GrammarTest.expr.parse(self.to_cursor("5 + (6 + -7 + (8 + 9) + 10) + -11"))
        self.assertEqual(result,
                         Add([Number(5),
                              Add([Number(6),
                                   Negate(Number(7)),
                                   Add([Number(8), Number(9)]),
                                   Number(10)]),
                              Negate(Number(11))]))
                                 
    

