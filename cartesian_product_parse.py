import re
from cartesian_product_calc import And, Or, Lit
from backtrack_parse import *
from cursor import Cursor

def parse_bash_cp(string):
    """
    The entry point to parse a bash cartesian product string in a syntax tree,
    which will be a subtype of class `Expression`,
    defined in "cartesian_product_calc.py"
    """
    cursor = create_cursor(string)
    (result, _) = parse_expr.parse(cursor)
    return result.value or And([])


def create_cursor(string):
    # includes the delimiters and characters between them
    tokens = re.split('([{},])', string)
    non_empty = [token for token in tokens if token != ""]
    return Cursor(non_empty)


# a grammar for the input string

# the parsers produce a dictionary of "kept" values after parsing the string.
# these 'to' functions each turn the expected dictionary of values into syntax tree nodes

def toLit(result):
    literals = keeps['literals']
    return Lit("".join(literals))

def toOr(result):
    branches = result.keeps['branches'].copy()
    last = result.keeps['last']
    if last:
        branches.append(last)        
    return Or(branches)

def toAnd(result):
    terms = result.keeps['terms']
    return And(terms)

open_curly = Token("{")
close_curly = Token("}")
comma = Token(",")

parse_literal = OneOrMore(AnyToken().keepAs('literals')).map(toLit)

parse_term = OneOf([parse_or, parse_literal])
parse_and = MoreThanOne(parse_term.keepAs('terms')).map(toAnd)

parse_branch = OneOf([parse_and, parse_or, parse_literal])
parse_or = AllOf([
    open_curly,
    OneOrMore(AllOf([parse_branch.keepAs('branches'), comma])),
    OneOf([
        AllOf([parse_term.keepAs('branches'), close_curly]),
        close_curly
    ])
]).map(toOr)

parse_expr = OneOf([parse_and, parse_or, parse_literal])


    



    

    
    
    
