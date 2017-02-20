from cartesian_product_calc import And, Or, Lit
from grammar import *

# a grammar for the input string of a bash cartesian product

def toLit(literals, keeps):
    return Lit("".join(literals))

def toOr(value, keeps):
    branches = result.keeps['branches'].copy()
    last = result.keeps['last_branch']
    if last:
        branches.append(last)        
    return Or(branches)

def toAnd(terms, keeps):
    return And(terms)

open_curly = Token("{")
close_curly = Token("}")
comma = Token(",")

parse_literal = OneOrMore(AnyToken()).map(toLit)    

# Lazy takes a thunk that produces the grammar, allowing forward references
parse_branch = OneOf([Lazy(lambda: parse_and),
                      Lazy(lambda: parse_or),
                      parse_literal])

parse_or = AllOf([
    open_curly,
    OneOrMore(AllOf([parse_branch.keep('branches'), comma])),
    OneOf([
        AllOf([parse_branch.keep('last_branch'), close_curly]),
        close_curly
    ])
]).map(toOr)

parse_term = OneOf([parse_or, parse_literal])
parse_and = MoreThanOne(parse_term).map(toAnd)

parse_expr = OneOf([parse_and, parse_or, parse_literal])


    



    

    
    
    
