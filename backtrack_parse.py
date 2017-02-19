class Grammar:

    def parse(self, cursor):
        if cursor.empty():
            return (None, cursor)
        else:
            return self.parse_next(cursor)

    def map(self, f):
        return MapResult(f, self)

    def keepAs(self, name):
        return KeepAs(name, self)

    def clear(self):
        return Clear(self)
    
    def parse_non_empty(self, cursor):
        """
        Returns None if this grammar can't be parsed completely beginning
        at `cursor`.
        
        If this grammar can be parsed completely beginning at `cursor`,
        this returns a pair containing:
        1) A `Result`, defined below.
        2) the cursor where it ended up after matching this grammar.
        """
        raise Exception("Call to abstract method `Grammar.parse`.")


class Result:
    def __init__(self, value, keeps = None):
        """
        `value` is the specific result of the Grammar.
        `keeps` is a dictionary of kept values during parsing.
        """
        self.value = value
        self.keeps = keeps or dict()

        
##################################################################
# Grammars that transform the Result as it returns up the stack.

class MapResult(Grammar):
    "Maps this Result into a new Result."

    def __init__(self, f, grammar):
        self.f = f
        self.grammar = grammar

    def parse_non_empty(self, start):
        (result, end) = self.grammar.parse(start)
        return result and (self.f(result), end)

    
class ToAST(MapResult):
    """
    Synonym for MapResult, for clarity in the grammar tree 
    for points that map a Result to a final AST node.
    """
    def __init__(self, toAst, grammar):
        MapResult.__init__(self, toAst, grammar)

    
class Clear(MapResult):
    "Clears the Result's `keeps` dictionary."
    def __init__(self, grammar):
        MapResult.__init__(self, lambda result: Result(result.value), grammar)
    

class KeepAs(MapResult):
    "Adds the value of the wrapped Grammar to the returned dictionary under a key"

    def __init__(self, name, grammar):
        MapResult.__init__(self, lambda result: self.add_key(result), grammar)

    def add_key(self, result):
        new_result = (result and result.copy()) or dict()
        new_result[self.name] = result.value

        
def merge_results(results):
    all_values = map(lambda result: result.value, results)
    all_keeps = dict()
    for result in results:
        all_keeps = merge_dicts(all_keeps, result.keeps)
        return Result(all_values, all_keeps)

    
def merge_dicts(keeps1, keeps2):
    merged = keeps1.copy()
    for k,v in keeps2:
        if k not in merged:
            merged[k] = v
        elif isinstance(merged[k], (list)) and isinstance(keeps2[k], (list)):
            merged[k].extend(keeps2[k])
        elif isinstance(merged[k], (list)):
            merged[k].append(keeps2[k])
    return merged
    
        

###########################################
# Grammars that define syntactic structure
        
class Token(Grammar):
    "Represents a token matching a given string."
    
    def __init__(self, value):
        self.value = value

    def parse_non_empty(self, start):
        return (start.head() == self.value and Result(start.head()), end)

    
class AnyToken(Grammar):
    "Matches any single token"

    def parse_non_empty(cursor):
        return (Result(cursor.head(), cursor))

    
class OneOrMore(Grammar):
    "Matches one or more, but not zero, subsequent matches"
    
    def __init__(self, grammar):
        self.grammar = grammar

    def parse_non_empty(self, start):
        (results, end) = start.crawl_while(lambda token: self.grammar.parse(token))
        return (results and merge_results(results), end)

    
class MoreThanOne(Grammar):
    "Matches at least two in a row of a grammar"

    def __init__(self, grammar):
        self.grammar = grammar

    def parse_non_empty(self, start):
        return AllOf([self.grammar, OneOrMore(self.grammar)]).parse(start)

    
class AllOf(Grammar):
    "Matches an entire list of grammars in sequence."

    def __init__(self, grammars):
        self.grammars = grammers

    def parse_non_empty(self, start):
        grammars = Cursor(self.grammars)
        (results, end) = start.crawl_while(lambda cursor: grammars.notEmpty() and grammars.head().parse(cursor))
        return (results and merge_results(results), end)


class OneOf(Grammar):
    "A disjunction: takes a number of grammars and finds the first one that matches."

    def __init__(self, grammars):
        self.grammars = grammars

    def parse_non_empty(self, start):
        # find a grammar in `self.grammars` that produces an AST
        # `match` here is a (Result, Cursor)
        (match, _) = Cursor(self.grammars).find(lambda parser: parser.parse(start))
        return match




        
    
    
