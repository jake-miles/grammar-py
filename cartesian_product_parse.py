from cartesian_product_calc import And, Or, Lit
from itertools import islice

def parse_bash_cp(string):
    """
    The entry point to parse a bash cartesian product string in a syntax tree,
    which will be a subtype of class `Expression`,
    defined in "cartesian_product_calc.py"
    """
    tokens = re.split('([{},])', string)
    non_empty_tokens = filter(lambda c: c != '', tokens)
    return parse_expr(non_empty_tokens)
            
def parse_expr(cursor):
    """
    `cursor` is the list of remaining tokens

    Returns a pair - the expression beginning with the first token in `cursor`,
    and the cursor to continue parsing.
    
    Returns (None, None) if no expression can be parsed (cursor has run out of tokens).

    Since the input string will be fairly small, and the next token
    does not by itself tell the full story of what type of expression tree
    we're about to parse, this implementation uses a simple backtracking approach,
    i.e. a depth-first search through an imaginary tree of potential expressions
    starting at `cursor`, implemented as a recursive descent.

    In other words, just try to parse each possibility 
    (in a particular order) until one matches.  

    An expression can be a Lit (literal), an Or (a set of variations), 
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

def parse_or(start_cursor):
    cursor = start_cursor
    
    # if `branches` becomes non-empty, then we found a comma and this might be an Or
    # It's definitely an Or if we then find the closing "}".
    # Otherwise it's just a suspiciously Or-looking literal.
    branches = []
    
    def looks_like_start_of_or():
        return cursor(0) == "{"

    def looks_like_end_of_or():
        return cursor and cursor(0) == "}"
        
    def is_defintely_end_of_or():
        return looks_like_end_of_or() and branches
        
    def at_end_of_branch():
        return cursor and (cursor(0) == "," or is_definitely_end_of_or())

    if not looks_like_start_of_or():
        return None
    else:
        while cursor and not looks_like_end_of_or():

            (next_expr, new_cursor) = parse_expr(tail(new_cursor))

            # empty branch - keep it to signal that this could be an Or
            # TODO: it will never get here.  it will descend infinitely
            # into Ors and will never call parse_literal. hm.
            if next_expr == Lit(","):
                branches.append(Lit(""))
            elif at_end_of_branch():
                branches.append(next_expr)

        return is_definitely_end_of_or() and (Or(branches), tail(new_cursor))

def parse_and(start_cursor):
    cursor = start_cursor
    terms = []

    # the And is finished when we reach the end of the top-level expression
    # or the end of the current sub-expression
    def is_end_of_and():
        return (not cursor) or cursor(0) == "}"

    if is_end_of_and():
        return None
    else:
        prev_expr = None
        while not is_end_of_and():

        # TODO: will this descend infinitely into Ands without ever calling parse_literal?
        (next_expr, cursor) = parse_expr(cursor)
        
        # to avoid wrapping everything in an And,
        # see if the new term can be appended to the previous one
        new_prev_expr = (next_expr and prev_expr and prev_expr.append(next_expr))
        if new_prev_expr:
            terms.append(new_prev_expr)
        else:
            terms.append(next_expr)

    if not terms:
        return None

    # avoid wrapping everything in an And
    elif len(terms) == 1:
        return (last_term, cursor)
    else:
        return (And(terms), cursor)
            
    
def parse_literal(cursor):
    return (Lit(cursor(0)), tail(cursor))

# returns the tail of the list.  
def tail(iterator):
    return islice(iterator, 1, None)

