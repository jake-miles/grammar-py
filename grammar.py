import abc
from cursor import Cursor

# A small parser combinator library.

# TODO: try replacing the classes with functions.  a lot less code.

class Grammar:

    trace = False

    def __init__(self, name = None):
        self.name = name

    def __repr__(self):
        return self.name or self.trace_repr()

    def parse(self, cursor):
        if cursor.empty():
            return (None, cursor)
        else:

            if Grammar.trace:
                print(self, cursor)

            (result, end) = self.parse_non_empty(cursor)

            if result and Grammar.trace:
                print("*** match:", self)
            else:
                print("--- no-match:", self)

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

    def __init__(self, thunk, name = None):
        Grammar.__init__(self, name)        
        self.thunk = thunk

    def parse(self, cursor):
        return self.thunk().parse(cursor)

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
    
    def parse_non_empty(self, cursor):
        return (Result(cursor.head()), cursor.tail())


class Token(Grammar):
    "Represents a token matching a given string."
    
    def __init__(self, value, name = None):
        Grammar.__init__(self, name)                
        self.value = value

    def trace_repr(self):
        return "Token(" + self.value + ")"

    def rename(self, name):
        return Token(self.value, name)
    
    def parse_non_empty(self, start):
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
            return (Result.merge_all(results), end)


class OneOrMore(Grammar):
    """
    Matches one or more subsequent matches.  
    `Result.value` is a list of the collected
    Results' values, and `Result.keeps` is a result of merging their `keeps`.
    """
    
    def __init__(self, grammar, stop, name = None):
        """
        `stop` is a grammar to check before checking for another repeat of `grammar`.
        If `stop` matches, return no match with the original cursor.
        """
        Grammar.__init__(self, name)        
        self.grammar = grammar
        self.stop = stop

    def trace_repr(self):
        return "OneOrMore(" + str(self.grammar) + ", stop=" + str(stop) + ")"

    def rename(self, name):
        return OneOrMore(self.grammar, name)
    
    def parse_non_empty(self, start):
        (results, end) = start.crawl_while(self.parse_next)
        if results:
            cursor = end
        else:
            cursor = start
        return (results and Result.merge_all(results), cursor)

    def parse_next(self, cursor):
        return (not (self.stop and self.stop.parse(cursor))) or self.grammar.parse(cursor)
            
    

class MoreThanOne(Grammar):
    """
    Matches at least two in a row of a grammar.
    `Result.value` is a list of the collected
    Results' values, and `Result.keeps` is a result of merging their `keeps`.
    """

    def __init__(self, grammar, name = None):
        Grammar.__init__(self, name)        
        self.grammar = grammar

    def trace_repr(self):
        return "MoreThanOne(" + str(self.grammar) + ")"

    def rename(self, name):
        return MoreThanOne(self.grammar, name)
    
    def parse_non_empty(self, start):

        def flatten(results, keeps):
            first = results[0]
            rest = results[1]
            flattened = [first]
            flattened.extend(rest)
            return flattened

        return AllOf([self.grammar, OneOrMore(self.grammar)]).map(flatten).parse(start)


class OneOf(Grammar):
    "A disjunction: takes a number of grammars and finds the first one that matches."

    def __init__(self, grammars, name = None):
        Grammar.__init__(self, name)        
        self.grammars = grammars

    def trace_repr(self):
        return "OneOf(" + str(self.grammars) + ")"

    def rename(self, name):
        return OneOf(self.grammars, name)
        
    def parse_non_empty(self, start):
        grammars = Cursor(self.grammars)
        result = False
        end = start
        while grammars.not_empty() and not result:
            (result, end) = grammars.head().parse(start)
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

    def parse_non_empty(self, start):
        (unless, _) = self.unless.parse(start)
        if unless:
            return (False, start)
        else:
            return self.grammar.parse(start)

    

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

    def parse_non_empty(self, start):
        (result, end) = self.grammar.parse(start)
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
    
    def parse_non_empty(self, start):
        (result, end) = self.grammar.parse(start)
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
        


        
    
    
