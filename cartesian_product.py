from itertools import takewhile, islice

class Expression:
    """
    Represents one segment in the input to cartesian_product.
    A sort of AST produced from parsing an input string.
    """
    # __eq__ enables deep-equals of objects in tests
    # http://stackoverflow.com/questions/22332729/how-to-do-a-deepequals-on-a-object-in-python
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # returns a set of strings to multiply with other sets of strings
    def branches(self):
        raise AbstractMethodCall("Expression.branches")

class AbstractMethodCall(Exception):
    pass

class ParseException(Exception):
    pass

class Lit(Expression):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Lit({0})".format(",".join(self.value))
        
    def branches(self):
        return [self.value]

class Or(Expression):

    def __init__(self, variations):
        self.variations = variations

    def __repr__(self):
        return "Or({0})".format(",".join([str(s) for s in self.variations]))
        
    # flattens any sub-Ors into a single list of variations
    def branches(self):
        all = []
        for v in self.variations:
            all.extend(v.branches())
        return all

class And(Expression):

    def __init__(self, ors):
        self.ors = ors

    def __repr__(self):
        return "And({0})".format(",".join([str(s) for s in self.ors]))

    def branches(self):
        return self.product()

    def product(self, index = 0):
        if index == len(self.ors):
            return []
        else:
            
            # branches at this level of the tree
            variations = self.ors[index].branches()
            
            # the cartesian product of all the ors to the right of the one at index
            rest = self.product(index + 1)
            
            # we're at the leaves - start accumulating back up the tree
            if not rest:
                return variations
            else:
                # for each string to the right, create a string for each variation at this level
                # TODO: I'll bet string concat is slow. could append segments and then reverse and join.
                return [v + result for v in variations for result in rest]

            
def parse_bash_cp(string):
    tokens = re.split('([{},])', string)
    non_empty_tokens = filter(lambda c: c != '', tokens)
    return parse_expr(non_empty_tokens)
            
def parse_expr(cursor):
    """
    Returns a pair - the expression beginning with the first token in `cursor`,
    and the cursor after parsing the expression.
    
    Returns (None, None) if no expression can be parsed (cursor has run out of tokens).

    Since the input string will be fairly small, and the next token
    does not by itself tell the full story of what type of expression tree
    we're about to parse, this implementation uses a backtracking approach -
    just try to parse each possibility until one sticks.  The thinking here
    is that the readability outweighs the couple milliseconds' difference.

    An expression can be a Lit (literal), Or (a set of variations), 
    or an And (a sequence of expressions to multiply together).
    """    
    return (parse_nothing(cursor) or
            parse_or(cursor) or
            parse_and(cursor) or
            parse_literal(cursor))

def parse_nothing(cursor):
    if not cursor:
        return (None, None)
    else:
        return None

def parse_or(cursor):
    if cursor(0) != "{":
        return None
    else:
        branches = []
        new_cursor = cursor

        # scoop up expressions separated by commas
        while new_cursor and new_cursor(0) != "}":            
            (next_expr, new_cursor) = parse_expr(tail(cursor))
            if new_cursor(0) == ",":
                branches.append(next_expr)

        # return an Or if we've reached the } and collected at least one branch
        return new_cursor(0) == "}" and branches and (Or(branches), tail(new_cursor))

def parse_and(cursor):
    pass

def parse_literal(cursor):
    pass
    
def bash_cartesian_product(spec):
    """

    Returns the "bash cartesian product", a space-delimited string
    of permutations, as described by the specification string `spec`.

    todo: define bash cartesian product

    >>> bash_cartesian_product("a{b,c}d{e,f,g}hi")
    abdehi abdfhi abdghi acdehi acdfhi acdghi

    >>> bash_cartesian_product("a{b,c{d,e,f}g,h}ij{k,l}")
    abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl
    """
    andExpr = parse_bash_cp(spec)
    strings = andExpr.product()
    return " ".join(strings)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: bash_cartesian_product '<input string>'\n")
        sys.exit(1)
    else:
        spec = sys.argv[1]
        print(bash_cartesian_product(spec))
        sys.exit(0)
    
            
