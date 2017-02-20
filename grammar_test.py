import unittest
from grammar import *

class GrammarTest(unittest.TestCase):

    def suite(self):
        return unittest.TestSuite(map(loadTests, [
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
        merged = Result.merge_all(result1, result2)
        self.assertEqual(merged, Result([result1, result2, result3]))

    def test_merge_all_merges_keeps(self):
        result1 = Result("result1", { 'a': 1 })
        result2 = Result("result2", { 'b': 2 })
        result3 = Result("result3", { 'c': 3 })
        merged = Result.merge_all(result1, result2)
        self.assertEqual(merged, Result([result1, result2, result3], { 'a': 1, 'b': 2, 'c': 3 }))


# TODO: add assertions for cursor position
# TODO: add assetions for Result's value for each grammar type

        
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
        self.assertFalse(result.value)
        self.assertTrue(end.empty())

        
class OneOrMoreTest(unittest.TestCase):

    def test_zero_no_match(self):
        grammar = OneOrMore(Token("sunshine"))        
        input = Cursor(["hello", "goodbye", "sunshine"])
        (result, end) = grammar.parse(input)
        self.assertFalse(result.value)
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
        self.assertFalse(result.value)
        self.assertEqual(end, input)
        
    def test_one_no_match(self):
        grammar = MoreThanOne(Token("hello"))
        input = Cursor(["hello", "goodbye", "sunshine"])
        (result, end) = grammar.parse(input)
        self.assertFalse(result.value)
        self.assertEqual(end, input.at(1))
        
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

        
class AllOfTest(unittest.TestCase):

    def __init__(self):
        self.grammar = AllOf([Token("hello"), Token("goodbye"), Token("sunshine")])
    
    def test_empty_input_no_match(self):
        input = Cursor([])
        result = self.grammar.parse(input)
        self.assertFalse(result.value)    
        self.assertEqual(end, input)
        
    def test_no_match_input_shorter_than_grammar(self):
        input = Cursor(["hello", "goodbye"])
        result = self.grammar.parse(input)
        self.assertFalse(result.value)    
        self.assertEqual(end, input)
        
    def test_one_matched_token_no_match(self):
        input = Cursor(["hello"])
        result = self.grammar.parse(input)        
        self.assertFalse(result.value)
        self.assertEqual(end, input)
        
    def test_two_matched_tokens_no_match(self):
        input = Cursor(["hello", "goodbye", "rain", "clouds"])
        result = self.grammar.parse(input)        
        self.assertFalse(result.value)
        self.assertEqual(end, input)
        
    def test_all_match(self):
        input = Cursor(["hello", "goodbye", "sunshine", "rain", "clouds"])
        result = self.grammar.parse(input)
        # Result.value is just True for this one - to retain values use `keep`
        self.assertTrue(result.value)
        self.assertEqual(end, input.at(3))

        
class OneOfTest(unittest.TestCase):

    def __init__(self):
        self.grammar = OneOf([Token("hello"), Token("goodbye"), Token("sunshine")])
    
    def test_no_match(self):
        input = Cursor(["rain", "hello"])
        result = self.grammar.parse(input)
        self.assertFalse(result)
        self.assertEqual(end, input)
        
    def test_first_option_match(self):
        input = Cursor(["hello", "rain"])
        result = self.grammar.parse(input)
        self.assertEqual(result.value, "hello")
        self.assertEqual(end, input.at(1))
        
    def test_middle_option_match(self):
        input = Cursor(["goodbye", "rain"])
        result = self.grammar.parse(input)
        self.assertTrue(result.value, "goodbye")
        self.assertEqual(end, input.at(1))
        
    def test_last_option_match(self):
        input = Cursor(["sunshine", "rain"])
        result = self.grammar.parse(input)
        self.assertTrue(result.value, "rain")
        self.assertEqual(end, input.at(1))

        
class KeepTest(unittest.TestCase):

    def test_adds_key(self):
        result = Result(5, { 'a': 1 }).keep('b')
        self.assertEqual(result, Result(5, { 'a': 1, 'b': 5 }))

    def test_use_with_all_of(self):
        grammar = AllOf([Token("hello").keep('h'), Token("goodbye"), Token("sunshine").keep('s')])
        input = "hello goodbye sunshine"
        (result, cursor) = grammar.parse(input)
        self.assertEqual(result, Result(True, { 'h': 'hello', 's': 'sunshine' }))
        
        
class MapTest(unittest.TestCase):
        
    def test_maps_value(self):
        result = Result(5, { 'a': 2 }).map(lambda value, keeps: value * keeps['a'])
        self.assertEqual(result, Result(10, { 'a': 2 }))

        
class ClearTest(unittest.TestCase):

    def test_clears_keeps(self):
        result = Result(5, { 'a': 1 }).clear()
        self.assertEqual(result, Result(5))

    
class GrammarTest(unittest.TestCase):

    def test_empty_no_match(self):
        grammar = AnyToken()
        (result, end) = grammar.parse(Cursor([]))
        self.assertFalse(result)
    
    def test_map(self):
        grammar = AnyToken()
        (result, end) = grammar.parse(Cursor["5"])
        self.assertEqual(result.map(lambda n, ks: n + "a"), Result("5a"))

    def test_keep(self):
        grammar = AnyToken()
        (result, end) = grammar.parse(Cursor["5"]).keep('n')
        self.assertEqual(result, Result("5", { 'n': "5" }))

    def clear(self):
        grammar = AnyToken()
        (result, end) = grammar.parse(Cursor["5"]).keep('n').clear()
        self.assertEqual(result, Result("5"))

    # AST classes for a limited arithmetic expression tree
    
    class Arithmetic(Grammar):
        def __eq_(self, other):
            return self.__dict__ == other.__dict__
        
    class Number(Arithmetic):

        def __init__(self, value):
            self.value = value
            
        @staticmethod
        def fromResult(n, keeps):
            return Number(n)
            
    class Negate(Arithmetic):

        def __init__(self, value):
            self.value = value

        @staticmethod            
        def fromResult(n, keeps):
            return Negate(n)
            
    class Add(Arithmetic):

        def __init__(self, terms):
            self.terms = terms

        @staticmethod
        def fromResult(terms, keeps):
            return Add(ks['left'].append(ks['right']))
            
    # grammar for the limited arithmetic expression tree
            
    number = AnyToken().map(lambda n,_: int(n)).map(Number.fromResult)

    negation = AllOf([Token("-"), number.keep('n')]).map(Negate.fromResult)

    expr = OneOf([number, negation, add])
    
    add = AllOf([expr.keep('left'), Token("+"), expr.keep('right')]).map(Add.fromResult)
    
    paren_expr = AllOf([Token("("), OneOrMore(expr).keep('expr')])

    def to_cursor(string):
        tokens = re.split('([()+-])', string)
        non_empty = [token for token in tokens if token != ""]
        return Cursor(non_empty)
    
    def test_primitive(self):
        self.assertEqual(number.parse(to_cursor("34")), Result(Number(34)))

    def test_prefix_discriminator_match(self):
        self.assertEqual(negation.parse(to_cursor("-5")), Result(Negate(Number(5))))

    def test_prefix_discriminator_no_match(self):
        self.assertFalse(negation.parse(to_cursor("5")))
        
    def test_infix_discriminator_match(self):
        self.assertEqual(add.parse(to_cursor("5 + 6")), Result(Add(5, 6)))

    def test_infix_discriminator_no_op_no_match(self):
        self.assertFalse(add.parse(to_cursor("5 6")))

    def test_infix_discriminator_no_right_term_no_match(self):
        self.assertFalse(add.parse(to_cursor("5 +")))
            
    def test_bracketed_expr(self):
        self.assertEqual(paren_expr.parse(to_cursor("(5)")),
                         Result(True, { 'expr': Number(5) }))

    def test_bracketed_expr_no_right_bracket_no_match(self):
        self.assertFalse(paren_expr.parse(to_cursor("(5")))

    def test_multiple_infix(self):
        self.assertEqual(OneOrMore(add).parse(to_cursor("5 + 6 + 7")),
                         Result([Add(Number("5"), Add(Number("6"), Number("7")))]))

    def test_multiple_infix_no_last_term_no_match(self):
        self.assertFalse(OneOrMore(add).parse(to_cursor("5 + 6 +")))

    def test_nested_bracket(self):
        self.assertEqual(paren_expr.parse(to_cursor("5 + (6 + 7)")),
                         Result(Add(Number(5), Add(Number(6), Number(7)))))

    def test_nested_bracket_no_right_inner_bracket_no_match(self):
        self.assertFalse(paren_expr.parse(to_cursor("5 + (6 + )")))        
    
    def test_complex_expression(self):
        self.assertEqual(expr.parse(to_cursor("5 + (6 + -7 + (8 + 9) + 10) + -11")),
                         Add([Number(5),
                              Add([Number(6),
                                   Negate(Number(7)),
                                   Add([Number(8), Number(9)]),
                                   Number(10)]),
                              Negate(Number(11))]))
                                 
    

