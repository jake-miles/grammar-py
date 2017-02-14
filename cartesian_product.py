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

    def product(self):
        raise Exception("Call to abstract method Expression.branches")

    def append(self, other):
        raise Exception("Call to abstract method Expression.append")

class ParseException(Exception):
    pass

class Lit(Expression):
    "Represents a literal character"
    
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Lit({0})".format(",".join(self.value))
        
    def product(self):
        return [self.value]

    def append(self, other):
        other is Lit and Lit(self.value + other.value)

class Or(Expression):
    "Represents a disjunction of expressions that multiply the results"
    
    def __init__(self, variations):
        self.variations = variations

    def __repr__(self):
        return "Or({0})".format(",".join([str(s) for s in self.variations]))

    def append(self, other):
        return None
    
    # flattens any sub-Ors into a single list of variations
    def product(self):
        all = []
        for v in self.variations:
            all.extend(v.branches())
        return all

class And(Expression):
    "Represents a sequence of terms to multiply"
    
    def __init__(self, terms):
        self.terms = terms

    def __repr__(self):
        return "And({0})".format(",".join([str(s) for s in self.terms]))

    def append(self, other):
        new_terms = this.terms.copy()
        new_terms.append(other)
        return And(new_terms)
    
    # this is the main calculation of the cartesian product
    # TODO: instead of recursion to the end, loop from right to left
    def product(self, index = 0):
        if index == len(self.terms):
            return []
        else:
            
            # branches at this level of the tree
            variations = self.terms[index].branches()
            
            # the cartesian product of all the terms to the right of the one at index
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
        # designates "nothing to parse"
        return (None, None)
    else:
        # None here means "not nothing", so something there to parse
        return None

def parse_or(cursor):

    # if `branches` becomes non-empty, then we found a comma and this could be an Or.
    # It's definitely an Or if we then find the closing "}".
    # Otherwise it's just a suspiciously Or-looking literal.
    branches = []
    new_cursor = cursor
    
    def looks_like_start_of_or():
        return cursor(0) == "{"
        
    def looks_like_end_of_or():
        return new_cursor and new_cursor(0) == "}"
        
    def is_defintely_end_of_or():
        return looks_like_end_of_or() and branches
        
    def at_end_of_branch():
        return new_cursor and (new_cursor(0) == "," or is_definitely_end_of_or())

    if not looks_like_start_of_or():
        return None
    else:
        while new_cursor and not looks_like_end_of_or():

            (next_expr, new_cursor) = parse_expr(tail(new_cursor))

            # empty branch - keep it so we know this could be an Or
            if next_expr == Lit(","):
                branches.append(Lit(""))
            elif at_end_of_branch():
                branches.append(next_expr)

        return is_definitely_end_of_or() and (Or(branches), tail(new_cursor))

def parse_and(start_cursor):
    cursor = start_cursor
    terms = []
    last_term = None

    # the And is finished when we reach the end of the top-level expression
    # or the end of the current sub-expression
    def is_end_of_and():
        return (not cursor) or cursor(0) == "}"

    if is_end_of_and():
        return None
    else:
        while not is_end_of_and():

        (next_expr, cursor) = parse_expr(cursor)
        
        # to avoid wrapping everything in an And,
        # see if the new term can be appended to the last
        new_last_term = (next_expr and last_term and last_term.append(next_expr))
        if new_last_term:
            last_term = new_last_term
        else:
            terms.append(next_expr)

    if not last_term:
        return None

    # avoid wrapping everything in an And
    elif (not terms) and last_term:
        return (last_term, cursor)
    else:
        return (And(terms), cursor)
            
    
def parse_literal(cursor):
    return (Lit(cursor(0)), tail(cursor))
    
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
    
            
