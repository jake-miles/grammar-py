class Grammar:

    def __init__(self, toAst):
        self.toAst = toAst
    
    def parse(self, cursor):
        """
        Returns None if this expression can't be parsed beginning
        at `cursor`, or the pair (ast, new_cursor) if it can,
        where `ast` is the node of the abstract syntax tree that was parsed,
        and `new_cursor` is the cursor at the last token 
        used to parse `ast`.  i.e. it is not advanced to the next
        token.
        """
        raise Exception("Call to abstract method `Grammar.parse`.")

    
class Literal(Grammar):
    "Represents a literal string, matching a token equal to that string"
    
    def __init__(self, toAst, value):
        Grammar.__init__(self, toAst)
        self.value = value

    def parse(self, start):
        return (start.notEmpty() and
                start.head() == self.value and
                self.toAst(self.value)

    
class OneOrMore(ZeroOrMore):
    "Matches one or more, but not zero, subsequent matches"
    
    def __init__(self, toAst, grammar):
        Grammar.__init__(self, toAst)
        self.grammar = grammar

    def parse(self, start):
        (matches, end) = start.crawl_while(self.grammar.parse, lambda (token, _): token)
        return matches and (self.toAst(matches, end))
            
class OneOf(Grammar):
    "A disjunction: takes a number of grammars and finds the first match."

    def __init__(self, toAst, grammars):
        Grammar.__init__(self, toAst)
        self.grammars = grammars

    def parse(self, start):
        (match, end) = Cursor(self.grammars).find(lambda parser: parser.parse(start))
        return matches and self.toAst(match, end)


        
        
    

        
    
    
