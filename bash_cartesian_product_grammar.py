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

end_of_branch = OneOf([comma, close_curly])

parse_literal = AnyToken().map(toLit).rename("parse_literal")

# Lazy takes a thunk that produces the grammar, allowing forward references
parse_branch = OneOf([Lazy(lambda: parse_and),
                      Lazy(lambda: parse_or),
                      parse_literal]).rename("parse_branch")

parse_or = AllOf([
    open_curly,
    OneOrMore(AllOf([parse_branch.keep('branches'), comma])).rename("branches"),
    OneOf([
        AllOf([parse_branch.keep('last_branch'), close_curly]).rename("last_branch"),
        close_curly
    ])
]).map(toOr).rename("parse_or")

parse_term = OneOf([parse_or, parse_literal]).rename("parse_term")
parse_and = MoreThanOne(parse_term).map(toAnd).rename("parse_and")

parse_expr = OneOf([parse_and, parse_or, parse_literal]).rename("parse_expr")


    



    

    
    
    
