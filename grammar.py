import abc
from cursor import Cursor

# A small parser combinator library.

class Grammar:

    def parse(self, cursor):
        if cursor.empty():
            return (None, cursor)
        else:
            return self.parse_non_empty(cursor)

    def map(self, f):
        "`f` is (lambda value, keeps: new_value)"
        return MapResult(f, self)

    def keep(self, name):
        return Keep(name, self)

    def clear(self):
        return Clear(self)

    @abc.abstractmethod
    def parse_non_empty(self, cursor):
        """
        Returns a pair:
        1) A `Result`, defined below, or falsy if this Grammar doesn't match the input.
        2) The cursor where it ended up after matching this grammar.
        """

 
class Result:

    def __init__(self, value, keeps = None):
        """
        `value` is the specific result of the Grammar that matched the input.
        `keeps` is a dictionary of values kept during parsing using `keep`.
        """
        self.value = value
        self.keeps = keeps or dict()        

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "Result(" + str(self.value) + ", " + str(self.keeps) + ")"
        
    @staticmethod
    def merge_all(results):
        all_values = map(lambda r: r.value, results)
        all_keeps = {}
        for result in results:
            all_keeps.update(result.keeps)
        return Result(all_values, all_keeps)
        

########################################################################
# Grammars that define syntactic structure, i.e. the recursive descent

class Lazy(Grammar):

    def __init__(self, thunk):
        self.thunk = thunk

    def parse(cursor):
        return self.thunk().parse(cursor)

    
class AnyToken(Grammar):
    "Matches any single token"

    def parse_non_empty(self, cursor):
        return (Result(cursor.head()), cursor.tail())


class Token(Grammar):
    "Represents a token matching a given string."
    
    def __init__(self, value):
        self.value = value

    def parse_non_empty(self, start):
        if start.head() == self.value:
            return (Result(start.head()), start.tail())
        else:
            return (False, start)

        
class AllOf(Grammar):
    """
    Matches an entire list of grammars in sequence.
    `Result.value` is True if it's a match
    To retain values from the individual grammars, use `keep`.
    """

    def __init__(self, grammars):
        self.grammars = grammars

    def parse_non_empty(self, start):

        # a hack to let us modify a closure variable
        class grammars: pass
        grammars.val = Cursor(self.grammars)

        def parse_next(cursor):
            if grammars.val.empty():
                return (None, cursor)
            else:
                (result, end) = grammars.val.head().parse(cursor)
                if result:
                    grammars.val = grammars.val.tail()
                return (result, end)
                
        (results, end) = start.crawl_while(parse_next)

        if not (results and grammars.val.empty()):            
            return (None, start)
        else:
            return (Result(True), end)


class OneOrMore(Grammar):
    """
    Matches one or more subsequent matches.  
    `Result.value` is a list of the collected
    Results' values, and `Result.keeps` is a result of merging their `keeps`.
    """
    
    def __init__(self, grammar):
        self.grammar = grammar

    def parse_non_empty(self, start):
        (results, end) = start.crawl_while(self.grammar.parse)
        if results:
            cursor = end
        else:
            cursor = start
        return (results and Result.merge_all(results), cursor)
    

class MoreThanOne(Grammar):
    """
    Matches at least two in a row of a grammar.
    `Result.value` is a list of the collected
    Results' values, and `Result.keeps` is a result of merging their `keeps`.
    """

    def __init__(self, grammar):
        self.grammar = grammar

    def parse_non_empty(self, start):
        return AllOf([self.grammar, OneOrMore(self.grammar)]).parse(start)


class OneOf(Grammar):
    "A disjunction: takes a number of grammars and finds the first one that matches."

    def __init__(self, grammars):
        self.grammars = grammars

    def parse_non_empty(self, start):
        return Cursor(self.grammars).next_map(lambda parser: parser.parse(start))


#############################################################################
# Grammars that transform a matched Result as it returns back up the stack.

class MapResult(Grammar):

    def __init__(self, f, grammar):
        self.f = f
        self.grammar = grammar

    def parse_non_empty(self, start):
        (result, end) = self.grammar.parse(start)
        return result and (self.f(result.value, result.keeps), end)

    
class Map(MapResult):
    """
    Maps this Result's value into a new value.  Takes a function `f`
    that is called with the current result value and the `keeps` map.
    `f` should return the new value for the Result.
    """
    def __init__(self, grammar):
        MapResult.__init__(self, lambda result: Result(self.f(result.value), result.keeps), grammar)    
    
    
class Keep(MapResult):
    "Maps the Result to one with the result's value in the `keeps` dictionary."

    def __init__(self, name, grammar):
        MapResult.__init__(self, lambda result: self.add_key(result), grammar)

    def add_key(self, result):
        new_keeps = result.keeps.copy()
        if new_keeps[self.name]:
            raise Exception("Keep: adding duplicate key '" + self.name + "'")
        new_keeps[self.name] = result.value
        return Result(result.value, new_keeps)


    
class Clear(MapResult):
    "Clears the Result's `keeps` dictionary before it returns further up the stack."
    def __init__(self, grammar):
        MapResult.__init__(self, lambda result: Result(result.value), grammar)
    
        


        
    
    
