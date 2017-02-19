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

    def test_merge_keeps_all_empty(self):
        keeps1 = {}
        keeps2 = {}
        keeps3 = {}
        merged = Result.merge_keeps(keeps1, keeps2)
        self.assertEqual(merged, {})

    def test_merge_keeps_self_empty(self):
        keeps1 = {}
        keeps2 = { 'a': 1, 'b': 2 }
        keeps3 = { 'c': 3, 'd': 4 }
        merged = Result.merge_keeps(keeps1, keeps2, keeps3)
        self.assertEqual(merged, { 'a': 1, 'b': 2, 'c': 3, 'd': 4 })

    def test_merge_keeps_others_empty(self):
        keeps1 = { 'a': 1, 'b': 2 }
        keeps2 = {}
        keeps3 = {}
        merged = Result.merge_keeps(keeps1, keeps2, keeps3)
        self.assertEqual(merged, keeps1)

    def test_merge_keeps_new_keys(self):
        keeps1 = { 'a': 1, 'b': 2 }
        keeps2 = { 'c': 3, 'd': 4 }
        keeps3 = { 'e': 5, 'f': 6 }
        merged = Result.merge_keeps(keeps1, keeps2, keeps3)
        self.assertEqual(merged, { 'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6 })

    def test_merge_keeps_repeated_keys_become_arrays(self):
        keeps1 = { 'a': 1, 'b': 2 }
        keeps2 = { 'a': 3, 'd': 4 }
        keeps3 = { 'e': 5, 'a': 6 }
        merged = Result.merge_keeps(keeps1, keeps2)
        self.assertEqual(merged, { 'a': [1,3,6], 'b': 2, 'd': 4, 'e': 5 })

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
# also, the return value is falsy if no match, and (result, cursor) if match
# but value doesn't matter until MapResult
        
class AnyTokenTest(unittest.TestCase):    
    def test_match_token(self):
        grammar = AnyToken() 
        input = Cursor(["hello"])
        result = grammar.parse(input)
        self.assertTrue(result.value)
                         

class TokenTest(unittest.TestCase):

    def test_specified_token_match(self):
        grammar = Token("hello")
        input = Cursor(["hello"])
        result = grammar.parse(input)        
        self.assertTrue(result.value)

    def test_different_token_no_match(self):
        grammar = Token("goodbye")
        input = Cursor(["hello"])
        result = grammar.parse(input)                
        self.assertFalse(result.value)


class OneOrMoreTest(unittest.TestCase):

    def test_zero_no_match(self):
        grammar = OneOrMore(Token("sunshine"))
        input = Cursor(["hello", "goodbye", "sunshine"])
        result = grammar.parse(input)
        self.assertFalse(result.value)
    
    def test_one_match(self):
        grammar = OneOrMore(Token("hello"))
        input = Cursor(["hello", "goodbye", "sunshine"])        
        result = grammar.parse(input)
        self.assertTrue(result.value)

    def test_two_match(self):
        grammar = OneOrMore(Token("hello"))
        input = Cursor(["hello", "hello", "goodbye"])        
        result = grammar.parse(input)
        self.assertTrue(result.value)

    def test_more_than_two_match(self):
        grammar = OneOrMore(Token("hello"))
        input = Cursor(["hello", "hello", "hello", "goodbye"])        
        result = grammar.parse(input)
        self.assertTrue(result.value)

    
class MoreThanOneTest(unittest.TestCase):

    def test_zero_no_match(self):
        grammar = MoreThanOne(Token("sunshine"))
        input = Cursor(["hello", "goodbye", "sunshine"])
        result = grammar.parse(input)
        self.assertFalse(result.value)

    def test_one_no_match(self):
        grammar = MoreThanOne(Token("hello"))
        input = Cursor(["hello", "goodbye", "sunshine"])
        result = grammar.parse(input)
        self.assertFalse(result.value)

    def test_two_match(self):
        grammar = MoreThanOne(Token("hello"))
        input = Cursor(["hello", "hello", "goodbye", "sunshine"])
        result = grammar.parse(input)
        self.assertTrue(result.value)

    def test_more_than_two_match(self):
        grammar = MoreThanOne(Token("hello"))
        input = Cursor(["hello", "hello", "hello" "goodbye", "sunshine"])
        result = grammar.parse(input)
        self.assertTrue(result.value)


class AllOfTest(unittest.TestCase):

    def __init__(self):
        self.grammar = AllOf([Token("hello"), Token("goodbye"), Token("sunshine")])
    
    def test_empty_input_no_match(self):
        input = Cursor([])
        result = self.grammar.parse(input)
        self.assertFalse(result.value)    
    
    def test_no_match_input_shorter_than_grammar(self):
        input = Cursor(["hello", "goodbye"])
        result = self.grammar.parse(input)
        self.assertFalse(result.value)    
        
    def test_one_matched_token_no_match(self):
        input = Cursor(["hello"])
        result = self.grammar.parse(input)        
        self.assertFalse(result.value)

    def test_two_matched_tokens_no_match(self):
        input = Cursor(["hello", "goodbye", "rain", "clouds"])
        result = self.grammar.parse(input)        
        self.assertFalse(result.value)

    def test_all_match(self):
        input = Cursor(["hello", "goodbye", "sunshine", "rain", "clouds"])
        result = self.grammar.parse(input)        
        self.assertTrue(result.value)
    

class OneOfTest(unittest.TestCase):

    def __init__(self):
        self.grammar = OneOf([Token("hello"), Token("goodbye"), Token("sunshine"))])
    
    def test_no_match(self):
        input = Cursor(["rain", "hello"])
        result = self.grammar.parse(input)
        self.assertFalse(result)
        
    def test_first_option_match(self):
        input = Cursor(["hello", "rain"])
        result = self.grammar.parse(input)
        self.assertTrue(result)

    def test_middle_option_match(self):
        input = Cursor(["goodbye", "rain"])
        result = self.grammar.parse(input)
        self.assertTrue(result)

    def test_last_option_match(self):
        input = Cursor(["sunshine", "rain"])
        result = self.grammar.parse(input)
        self.assertTrue(result)

    
class MapResultTest(unittest.TestCase):

    def test_identity(self):
        result1 = Result(5, { 'a': 1 })
        self.assertEqual(result1.map(lambda r: r), result1)

    def test_maps_result(self):
        self.assertEqual(Result(5, { 'a': 1 }).map(lambda r: Result(r.value * 2, { 'b': r.keeps['a'] * 2 })),
                         Result(10, { 'b': 2 }))
    

class KeepTest(unittest.TestCase):

    def test_keeps_result_value_as_key(self):
        result = Result(5, { 'a': 1 }).keepAs('b')
        self.assertEqual(result, Result(5, { 'a': 1, 'b': 5 }))

    def test_turns_key_into_list(self):
        result = Result(5, { 'a': 1 }).keepAs('a')
        self.assertEqual(result, Result(5, { 'a': [1,5] }))
    

class ClearTest(unittest.TestCase):

    def test_clears_keeps(self):
        result = Result(5, { 'a': 1 }).clear()
        self.assertEqual(result, Result(5))

    
class GrammarTest(unittest.TestCase):

    class Arithmetic:
        def __eq_(self, other):
            return self.__dict__ == other.__dict__
    
    class Number(Arithmetic):
        def __init__(self, value):
            self.value = value

    class Negate(Arithmetic):
        def __init__(self, value):
            self.value = value
            
    class Add(Arithmetic):
        def __init__(self, terms):
            self.terms = terms
            
    class Multiply(Arithmetic):
        def __init__(self, factors):
            self.factors = factors

    def test_empty_no_match(self):        
        pass
    
    def test_map(self):
        pass

    def test_keepAs(self):
        pass

    def clear(self):
        pass
    
    def test_primitive(self):
        pass

    def test_prefix_discriminator(self):
        pass

    def test_infix_discriminator(self):
        pass

    def test_postfix_discriminator(self):
        pass

    def test_multiple_infix(self):
        pass
    
    def test_bracket(self):
        pass

    def test_nested_bracket(self):
        pass

    def test_complex_expression(self):
        pass
    
