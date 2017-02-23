import abc
from cursor import Cursor
from itertools import repeat

# A lightweight parser combinator library, i.e., lets you define a simple grammar
# by composing more complex grammar expressions out of simpler ones.
# Uses rescursive descent and backtracking (depth-first search) to match a Grammar tree
# against an input string.
#
# Inspired by
# a) prolog,
# b) the rho-contracts.js library, https://github.com/bodylabs/rho-contracts-fork
# c) http://www.lihaoyi.com/fastparse/ (the "parse" part, not the "fast" part)
#

def trace(level, *args):
    print("".join(repeat("-", level)) + ", ".join(map(str, args)))

class Grammar:
    """
    Represents a grammar tree that will parse a string into some top-level value
    and a dictionary of items captured along the way.

    You compose a grammar by composing subtypes of `Grammar` into a tree,
    and then call `parse` on it with an input Cursor (see `cursor.py`).

    For example:

    class Addition:
      def __init__(self, left, right):
        self.left = left
        self.right = right

    addition = AllOf([AnyToken().map(toNumber), 
                      Token("+"), 
                      AnyToken().map(toNumber)]).map(Addition)

    (result, end) = addition.parse(["2", "+", "3", "-", "1")

    result == Addition("2", "3")

    `end` is the cursor on the input after parsing the `addition`, so
    a Cursor pointing to ["-", "1"]. If there is no more string after matching
    a Grammar, `end` would be an empty Cursor.

    The subtypes you compose to create the structure of the grammar are:

    - Token: matches a specific literal string

    - AnyToken: matches any literal string

    - AllOf: takes a list of Grammars, and only matches if they can be matched
      against the input in sequence.

    - OneOrMore: takes a Grammar and matches one or more occurrences of that Grammar
      occurring in sequence in the input.

    - OneOf: takes a list of Grammars and will try them in order until one
      matches the input.

    - Unless: takes two Grammars.  The first is a Grammar whose match is negated, i.e.
      if that Grammar matches, the Unless fails to match the input string.  The
      second Grammar is applied only if the first fails, and its value is returned
      as the result of the Unless.

    When a Grammar matches, it returns a `Result`, which contains a `value`
    and a dictionary called `keeps`.  You can modify this `Result` as it
    returns up the stack using the following methods on `Grammar`:

    `map`: takes a (lambda value, keeps) that is called with the `Result's` `value`
    and `keeps` dictionary, and should return whatever the result should map into
    (an abstract syntax tree node or other model object).

    `keep`: takes a string, and will add the Result's `value` to the `keeps`
    dictionary under that name.  This dictionary can then be used by the `map`
    lambda of a grammar higher up the tree to create its model object.

    `rename`: takes a string, and if you are debugging your grammar 
    (set `Grammar.trace = True`), it will use that name instead of the 
    Grammar's entire tree structure when logging it.    

    For a sample grammar, see `bash_cartesian_product_grammar.py`.
    """

    trace = False

    def __init__(self, name = None):
        self.name = name

    def __repr__(self):
        return self.name or self.trace_repr()

    def parse(self, cursor, level = 0):
        if cursor.empty():
            return (None, cursor)
        else:

            if Grammar.trace:
                trace(level, (self, cursor))

            (result, end) = self.parse_non_empty(cursor, level)

            if result and Grammar.trace:
                trace(level, "*** match:", self)
            elif Grammar.trace:
                trace(level, "--- no-match:", self)

            return (result, end)

    def mapResult(self, f):
        return MapResult(f, self)
        
    def map(self, f):
        "`f` is (lambda value, keeps: new_value)"
        return Map(f, self)

    def keep(self, name):
        return Keep(name, self)

    def clear(self):
        return Clear(self)

    @abc.abstractmethod
    def rename(self, name):
        """
        Returns an instance of this Grammar assigned the given name for debugging"
        """
    
    @abc.abstractmethod
    def parse_non_empty(self, cursor, level):
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
    """
    This grammar is a special wrapper that lets you use forward references
    to grammar elements you define further down the page.  Necessary if
    the gramar contains any recursive element.

    e.g.

    expr = OneOf([addition, substraction])
    addition = AllOf([expr, Token("+"), expr])
    subtraction = AllOf([expr, Token("-"), expr])

    will not run, because the references to `addition` and `subtraction` occur
    before they are defined.  The workaround is to wrap something in `Lazy`:

    expr = OneOf([Lazy(lambda: addition), Lazy(lambda: subtraction)])
    addition = AllOf([expr, Token("+"), expr])
    subtraction = AllOf([expr, Token("-"), expr])

    Then the forward reference will only be resolved when needed during parsing,
    and `addition` and `subtraction` will have been already defined.
    """
    def __init__(self, thunk, name = None):
        Grammar.__init__(self, name)        
        self.thunk = thunk

    def trace_repr(self):
        return "Lazy wrapper"

    def parse(self, cursor, level = 0):
        return self.thunk().parse(cursor, level + 1)

    def rename(self, name):
        return Lazy(self.thunk, name)

    
class AnyToken(Grammar):
    "Matches any single token"

    def __init__(self, name = None):
        Grammar.__init__(self, name)                
    
    def trace_repr(self):
        return "AnyToken"

    def rename(self, name):
        return AnyToken(self.name)
    
    def parse_non_empty(self, cursor, level):
        return (Result(cursor.head()), cursor.tail())


class Token(Grammar):
    """
    Represents a token matching a given string.
    e.g. Token("a") will match the literal string "a".
    """
    
    def __init__(self, value, name = None):
        Grammar.__init__(self, name)                
        self.value = value

    def trace_repr(self):
        return "Token(" + self.value + ")"

    def rename(self, name):
        return Token(self.value, name)
    
    def parse_non_empty(self, start, level):
        if start.head() == self.value:
            return (Result(start.head()), start.tail())
        else:
            return (False, start)
        
        
class AllOf(Grammar):
    """
    Matches an entire list of grammars in sequence.
    `Result.value` is the list of the grammars' results if a match.
    To retain values from the individual grammars more usefully, use `keep`.
    """

    def __init__(self, grammars, name = None):
        Grammar.__init__(self, name)
        self.grammars = grammars

    def trace_repr(self):
        return "AllOf(" + str(self.grammars) + ")"

    def rename(self, name):
        return AllOf(self.grammars, name)

    def parse_non_empty(self, start, level):

        # a hack to let us modify a closure variable
        class grammars: pass
        grammars.val = Cursor(self.grammars)

        def parse_next(cursor):
            if grammars.val.empty():
                return (None, cursor)
            else:
                (result, end) = grammars.val.head().parse(cursor, level + 1)
                if result:
                    grammars.val = grammars.val.tail()
                return (result, end)
                
        (results, end) = start.crawl_while(parse_next)

        if not (results and grammars.val.empty()):            
            return (None, start)
        else:
            return (Result.merge_all(results), end)


class OneOrMore(Grammar):
    """
    Matches one or more subsequent matches.  
    `Result.value` is a list of the collected
    Results' values, and `Result.keeps` is a result of merging their `keeps`.
    """
    
    def __init__(self, grammar, name = None):
        """
        `stop` is a grammar to check before checking for another repeat of `grammar`.
        If `stop` matches, return no match with the original cursor.
        """
        Grammar.__init__(self, name)        
        self.grammar = grammar

    def trace_repr(self):
        return "OneOrMore(" + str(self.grammar) + ")"

    def rename(self, name):
        return OneOrMore(self.grammar, name)
    
    def parse_non_empty(self, start, level):
        (results, end) = start.crawl_while(lambda c: self.grammar.parse(c, level + 1))
        if results:
            cursor = end
        else:
            cursor = start
        return (results and Result.merge_all(results), cursor)
    

class OneOf(Grammar):
    "A disjunction: takes a number of grammars and finds the first one that matches."

    def __init__(self, grammars, name = None):
        Grammar.__init__(self, name)        
        self.grammars = grammars

    def trace_repr(self):
        return "OneOf(" + str(self.grammars) + ")"

    def rename(self, name):
        return OneOf(self.grammars, name)
        
    def parse_non_empty(self, start, level):
        grammars = Cursor(self.grammars)
        result = False
        end = start
        while grammars.not_empty() and not result:
            (result, end) = grammars.head().parse(start, level + 1)
            if not result:
                grammars = grammars.tail()
        return (result, end)

    
class Unless(Grammar):
    """
    Takes an `unless` grammar and a main `grammar`.  Matches the cursor
    only if `unless` does not match and `grammar` does.
    """
    def __init__(self, unless, grammar, name = None):
        Grammar.__init__(self, name)
        self.grammar = grammar
        self.unless = unless

    def trace_repr(self):
        return "Unless(unless=" + str(self.unless) + ", grammar=" + str(self.grammar) + ")"

    def rename(self, name):
        return Unless(self.unless, self.grammar, name)

    def parse_non_empty(self, start, level):
        (unless, _) = self.unless.parse(start, level + 1)
        if unless:
            return (False, start)
        else:
            return self.grammar.parse(start, level + 1)

    

#############################################################################
# Grammars that transform a matched Result as it returns back up the stack.

class MapResult(Grammar):

    def __init__(self, f, grammar, name = None):
        Grammar.__init__(self, name)
        self.f = f
        self.grammar = grammar

    def trace_repr(self):
        return "MapResult(" + str(self.grammar) + ")"

    def rename(self, name):
        return MapResult(self.f, self.grammar.rename(name), "Map of " + name)

    def parse_non_empty(self, start, level):
        (result, end) = self.grammar.parse(start, level + 1)
        return (result and self.f(result), end)

    
class Map(Grammar):
    """
    Maps this Result's value into a new value.  Takes a function `f`
    that is called with the current result value and the `keeps` map.
    `f` should return the new value for the Result.
    """
    def __init__(self, f, grammar, name = None):
        Grammar.__init__(self, name)
        self.f = f
        self.grammar = grammar
        
    def trace_repr(self):
        return "Map(" + str(self.grammar) + ")"

    def rename(self, name):
        return Map(self.f, self.grammar.rename(name), "Map of " + name)

    # TODO: impl. this as a subclass of MapResult.  this caused a bug before.
    
    def parse_non_empty(self, start, level):
        (result, end) = self.grammar.parse(start, level + 1)
        new_result = (result and result.value and
                      Result(self.f(result.value, result.keeps), result.keeps))
        return (new_result, end)
    
    
class Keep(MapResult):
    "Maps the Result to one with the result's value in the `keeps` dictionary."

    def __init__(self, key, grammar, name = None):        
        MapResult.__init__(self, self.add_key, grammar, name)
        self.key = key

    def trace_repr(self):
        return "Keep(" + self.key + ")"

    def rename(self, name):
        return Keep(self.key, self.grammar.rename(name), name)
    
    def add_key(self, result):
        new_keeps = result.keeps.copy()
        if self.key in new_keeps:
            raise Exception("Keep: adding duplicate key '" + self.key + "'")
        new_keeps[self.key] = result.value
        return Result(result.value, new_keeps)


class Clear(MapResult):
    "Clears the Result's `keeps` dictionary before it returns further up the stack."

    def __init__(self, grammar, name = None):
        MapResult.__init__(self, lambda result: Result(result.value), grammar, name)

    def trace_repr(self):
        return "Clear(" + str(self.grammar) + ")"

    def rename(self, name):
        return Clear(self.grammar, name)
        


        
    
    
