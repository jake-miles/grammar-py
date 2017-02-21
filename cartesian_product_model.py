import abc
from cursor import Cursor

"""
These classes define the syntax tree produced by the parser, 
which is also the data model for calculating the cartesian product - 
an expression tree composed of a sort of "cartesian product algebra" of
literal strings, conjunctions and disjunctions (classes Lit, And, and Or).

To calculate the cartesian product (a list of strings), 
call an Expression's `cartesian_product` method. 

An Expression also provides an `append` method, which allows the
parser to construct a simpler syntax tree, to make tests and debugging
easier, and the logic easier to follow.
"""

class Expression:
    """
    Represents an expression tree that can produce a 
    cartesian product of strings.
    """

    @abc.abstractmethod
    def cartesian_product(self):
        "Produces the list of strings that is this expression's cartesian product"
        
    # comparing two Expressions is a deep-equals.
    # http://stackoverflow.com/questions/22332729/how-to-do-a-deepequals-on-a-object-in-python
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    
class Empty(Expression):
    "Represents an empty disjunction branch"

    def __init__(self):
        pass
    
    def __repr__(self):
        return "Empty"
        
    def cartesian_product(self):
        return None


class Lit(Expression):
    "Represents a literal string, whose cartesian product is that string"
    
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Lit({0})".format(",".join(self.value))

    def cartesian_product(self):
        return [self.value]


class Or(Expression):
    """
    Represents a disjunction of expressions, whose
    cartesian product is the flattening of their individual
    cartesian products.  For example, the string 

    {c,{d,e},f} 

    becomes 

    Or([Lit("c"), Or([Lit("d"), Lit("e")]), Lit("f")])

    which produces the cartesian product

    ["c", "d", "e", "f"]

    """
    
    def __init__(self, branches):
        self.branches = branches

    def __repr__(self):
        return "Or({0})".format(",".join([str(s) for s in self.branches]))

    def cartesian_product(self):
        acc = []
        for branch in self.branches:
            acc.extend(branch.cartesian_product())
        return acc

    
class And(Expression):
    """
    Represents the conjunction of expressions, which multiply in
    sequence to produce the cartesian product.

    For example, 

    the string "abc{1,2}de" 

    becomes

    And([Lit("abc"), Or(["1","2"]), List("de")])

    which produces the cartesian product

    ["abc1de", "abc2de"]
    """
    
    def __init__(self, terms):
        self.terms = terms

    def __repr__(self):
        return "And({0})".format(",".join([str(s) for s in self.terms]))

    def cartesian_product(self):
        acc = []
        for term in self.terms:
            if not acc:
                acc = term.cartesian_product()
            else:
                acc = [acc_string + extension for acc_string in acc for extension in term.cartesian_product()]
        return acc
