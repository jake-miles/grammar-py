from cartesian_product_calc import And, Or, Lit, Empty
from grammar import *

# a grammar for the input string of a bash cartesian product

def toEmpty(value, keeps):
    return Empty()

def toLit(literals, keeps):
    return Lit("".join(literals))

def toOr(value, keeps):
    branches = list(keeps['branches'])
    last = keeps['last_branch']
    branches.append(last)
    return Or(branches)

def toAnd(terms, keeps):
    if len(terms) == 1:
        return terms[0]
    else:
        return And(terms)

# the Lazy wrapper just lets us refer to grammars defined later down the page
lazy_or = Lazy(lambda: _or)
lazy_top_level_and = Lazy(lambda: top_level_and)
lazy_literal = Lazy(lambda: literal)

top_level_expr = OneOf([lazy_top_level_and,
                        lazy_or,
                        lazy_literal]).rename("top_level_expr")

open_curly = Token("{")
close_curly = Token("}")
comma = Token(",")

literal = AnyToken().map(toLit).rename("Lit")

top_level_and = OneOrMore(OneOf([lazy_or, lazy_literal])).map(toAnd).rename('And')

def keep_first(results, keeps):
    return results[0]

# the contents of a branch is an And, making sure not to capture the
# end_token as a literal but to leave it to be interpreted as structural syntax.
branch_contents = OneOrMore(OneOf([
    lazy_or,
    Unless(OneOf([comma, close_curly]), lazy_literal)
])).map(toAnd).rename('And')
    
def branch_ending_in(token):
    return OneOf([
        token.map(toEmpty),
        AllOf([branch_contents, token]).map(keep_first)
    ])

_or = AllOf([
    open_curly,
    OneOrMore(branch_ending_in(comma)).keep('branches'),
    branch_ending_in(close_curly).keep('last_branch')
]).map(toOr).clear().rename('Or')


  





    



    

    
    
    
