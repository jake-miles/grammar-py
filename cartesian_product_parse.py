import re
from cartesian_product_calc import And, Or, Lit
from cursor import Cursor

def parse_bash_cp(string):
    """
    The entry point to parse a bash cartesian product string in a syntax tree,
    which will be a subtype of class `Expression`,
    defined in "cartesian_product_calc.py"
    """
    cursor = create_cursor(string)
    (expression, empty_cursor) = parse_expr(cursor)
    # make sure we return an Expression
    return expression or And([])

def create_cursor(string):
    # includes the delimiters and characters between them
    tokens = re.split('([{},])', string)
    non_empty = [token for token in tokens if token != ""]
    return Cursor(non_empty)
    
    
"""
All the following `parse_` functions take a "cursor", 
which` is the list of remaining tokens.

They all return a pair containing 
1) the expression beginning with the first token in `cursor`, and
2) the cursor to continue parsing.

They return (None, None) if no expression can be parsed (cursor has run out of tokens).

Since the input string will be fairly small, and the token at the start of an expression
does not by itself tell the full story of what type of expression tree
we're about to parse, this implementation uses a backtracking approach,
i.e. a depth-first search through an imaginary tree of potential expressions
starting at `cursor`, implemented as a recursive descent.

In other words, just try to parse each possibility starting at the current token
until one matches.  

An expression can be a Lit (string literal), an Or (a disjunction of sub-expressions), 
or an And (a sequence of expressions).
"""    


def parse_expr(cursor):
    print("parse_expr", cursor)
    return (parse_nothing(cursor) or
            parse_and(cursor))


def parse_nothing(cursor):
    print("parse_nothing", cursor)
    """
    Returns (None, None) if `cursor` is out of tokens.  
    Otherwise returns None, because this parse_ function didn't match 
    the contents of the cursor.
    """
    if cursor.empty():
        # None here means "not nothing", so something left to parse
        return (None, None)
    else:
        # "no expression parsed"
        return None


def parse_and(start):
    print("parse_and", start)
    """
    Parses the expression at `start` into a sequence of terms.  
    If only one term can be collected, returns that expression on its own.
    Otherwise returns the sequence of parsed expressions as an And.
    Unless `start` is empty, this will always return an expression, not None.
    """
    cursor = start
    terms = TermSequence()

    # the And is finished when we reach the end of the top-level expression
    # or the end of the current sub-expression.
    def is_end_of_and():
        return cursor.empty() or cursor.head() == "}"

    while not is_end_of_and():
        print("not is_end_of_and")
        (new_term, cursor) = parse_term(cursor)
        print("new_term: " + str(new_term))
        if new_term:
            terms.append(new_term)

    return (terms.toExpression(), cursor)


def parse_term(cursor):
    print("parse_term", cursor)
    "Parses one term in an And expression"
    return (parse_nothing(cursor) or
            parse_or(cursor) or
            parse_literal(cursor))


def parse_literal(cursor):
    print("parse_literal", cursor)
    "Parses one character to be included as a literal in the syntax tree."
    return (Lit(cursor.head()), cursor.tail())


def parse_or(start):
    print("parse_or", start)
    """
    Parses a disjunction of sub-expressions, returning them as an Or.

    For example, "{a,b,c}" becomes the expression Or([Lit("a"),Lit("b"),Lit("c")]).

    This is a bit tricky primarily because things that look almost like an Or
    in the sequence of tokens will turn out to be literals.  We don't know if we 
    have an Or in our hand until we've reached an opening curly brace, 
    a comma, and the closing curly brace.

    For example, "{a,c" is not a disjunction but the literal "{a,c",
    and "{abc}" is not the disjunction of "a", "b" and "c", but the literal "{abc}".

    In addition, the string "{ab,{c,d}" becomes the string literal "{ab,"
    followed by the disjunction of "c" and "d", because only the sub-expression "{c,d}"
    is closed, not the top-level curly brace.  However, this case is handled by
    the overall recursive-descent/backtracking scheme, not any details in this function.

    In that example, this function would identity the {, find the comma,
    identifying a potential branch, keep trying to parse the rest into an Or,
    capturing the sub-expression {c,d} in its recursive call to `parse_expr`,
    and then reach the end of the string without finding its closing }, returning None.
    """
    cursor = start
    
    # if `branches` becomes non-empty, then we found a comma
    branches = []
    
    def looks_like_start_of_or():
        return (not cursor.empty()) and cursor.head() == "{"

    def looks_like_end_of_or():
        return (not cursor.empty()) and cursor.head() == "}"

    def is_definitely_end_of_or():
        return looks_like_end_of_or() and branches

    # we're at the end of a branch if we hit its comma or end of the Or.
    def at_end_of_branch():
        return (not cursor.empty() and
                (cursor.head() == "," or is_definitely_end_of_or()))

    if not looks_like_start_of_or():
        return None
    else:
        while (not cursor.empty()) and not looks_like_end_of_or():

            (next_branch, cursor) = parse_expr(cursor.tail())

            # empty branch - hold onto it to denote that this could be an Or
            if next_branch == Lit(","):
                branches.append(Lit(""))
            elif at_end_of_branch():
                branches.append(next_branch)

    return is_definitely_end_of_or() and (Or(branches), cursor.tail())


class TermSequence:
    """
    Used by parse_and to collect the sequence of terms.
    To simplify the resulting syntax tree this imposes two optimizations:
    1) When adding a term to the sequence, first it sees if it can 
       simply append it to the previous term via the Expression's `append` method.
    2) If in the end we only captured one term, returns that term instead of
       wrapping it in its own And.
    """
    terms = []
            
    def append(self, new_term):
        print("TermSequence.append: " + str(new_term))
        "Incorporates `new_term` into the sequence of collected terms."
        last_term_extended = self.terms and self.terms[0].append(new_term)
        if last_term_extended:
            print("extending last term")
            self.terms.pop()
            self.terms.append(last_term_extended)
        else:
            print("appending new term")
            self.terms.append(new_term)

    def toExpression(self):
        "Returns the Expression representing the collected sequence of terms."
        if len(self.terms) == 1:
            return self.terms[0]
        else:
            return And(self.terms)
    

