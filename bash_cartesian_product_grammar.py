from cartesian_product_model import And, Or, Lit, Empty
from grammar import *

# a grammar for the input string of a bash cartesian product

"""
This uses the classes defined in `grammar.py` to describe
the grammar of the bash cartesian product intput string.
Doing so creates a tree of `Grammar` instances that then parse
an input string and produce a tree of the model classes
defined in `cartesian_product_model.py`: `Empty`, `Lit` `Or`, and `And`.

An input string, at any point during parsing, can represent:

1) a literal term, like "abc"

2) a disjunction of terms, i.e. branches to multiply by, like "{d,e}", becoming an `Or`

3) a conjunction of terms, i.e. a sequence of terms like "abc{d,e}", 
becoming an `And` of "abc" and "{d,e}".

4) an empty disjunction branch, for example in "{,d}", where the first branch is empty.

The calls to `rename` just rename a grammar for easier debugging when tracing the parse.

"""

# these "to" functions will be called with the current result value
# at a point in the parse tree, to map it into one of our model objects.
# each is called with the result value at the time, and a dictionary
# called `keeps`, which is a dictionary of values captured by the
# calls to `keep()` further down inthe grammar tree.

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
    # without this check, everything in the result tree
    # would get wrapped in its own `And`
    if len(terms) == 1:
        return terms[0]
    else:
        return And(terms)

# the delimiters
open_curly = Token("{")
close_curly = Token("}")
comma = Token(",")

# the `Lazy` wrapper just lets us refer to grammars defined later down the page
# without python complaining that it hasn't been defined yet.
literal = Lazy(lambda: AnyToken().map(toLit).rename("Lit"))    

# returns a grammar defining a branch of a disjunction
# ending in the given delimiter token, which will be , or }
def branch_ending_in(token):

    def keep_first(results, keeps):
        return results[0]

    # the contents of a branch is either one term of a conjunction of terms.
    # the `Unless` makes sure we don't capture the , or } as a literal.
    branch_contents = OneOrMore(OneOf([
        _or,
        Unless(OneOf([comma, close_curly]), literal)
    ])).map(toAnd).rename('And')
    
    return OneOf([
        token.map(toEmpty),
        AllOf([branch_contents, token]).map(keep_first)
    ])

# this defines the grammar of a disjunction, e.g. {d,e}, which becomes an `Or`
# e.g. "{d,e}" becomes a disjunction with branches "d" and "e".
_or = Lazy(lambda: AllOf([
    open_curly,
    # `keep` adds the parsed list of branches to the `keeps` dictionary as `branches`
    OneOrMore(branch_ending_in(comma)).keep('branches'),
    branch_ending_in(close_curly).keep('last_branch')
]).map(toOr).clear().rename('Or'))

# a conjunction, which becomes an `And`, at the "top level",
# i.e. not nested within a disjunction.  an `And` is a sequence of terms
# such as "abc{d,e}", which is the conjunction of "abc" and "{d,e}"
_and = Lazy(lambda: OneOrMore(OneOf([_or, literal])).map(toAnd).rename('And'))

# the root parser
top_level_expr = OneOf([_and,
                        _or,
                        literal]).rename("top_level_expr")



  





    



    

    
    
    
