import abc
from cursor import Cursor

class Expression:
    """
    Represents an expression tree that can produce a 
    cartesian product of strings.

    The subclasses define the syntax tree produced by the parser, 
    which is also the data model for calculating the cartesian product - 
    an expression tree composed of a sort of "cartesian product algebra": 
    an empty product (Empty), a literal string (Lit), a conjunction of 
    subexpressions (And), and a disjunction of sub-expressions (Or).
    
    To calculate the cartesian product (a list of strings), 
    call an Expression's `cartesian_product` method. 
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
        return []


class Lit(Expression):
    "Represents a literal string, whose cartesian product is that string"
    
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Lit({0})".format(",".join(self.value))

    def cartesian_product(self):
        return [self.value]


class Or(Expression):
    "Represents a disjunction of expressions."
    
    def __init__(self, branches):
        self.branches = branches

    def __repr__(self):
        return "Or({0})".format(",".join([str(s) for s in self.branches]))

    def cartesian_product(self):
        "Build a flattened list of all the branches' products."
        acc = []
        for branch in self.branches:
            acc.extend(branch.cartesian_product())
        return acc

    
class And(Expression):
    """
    Represents the conjunction of expressions, which multiply in
    sequence to produce the cartesian product.
    """
    
    def __init__(self, terms):
        self.terms = terms

    def __repr__(self):
        return "And({0})".format(",".join([str(s) for s in self.terms]))

    def cartesian_product(self):
        """
        Builds up `acc` in a "breadth-first" fashion - produces one 
        sub-expression's product, appending each string in the sub-product
        to each string already in `acc`, and then doing the same for the 
        next sub-expression.
        
        For example, the string "abc{d,e}f{g,h}"
        produces the following iterations of the list `acc`:

        abc
        
        abcd
        abce

        abcdf
        abcef

        abcdfg
        abcdfh
        abcefg
        abcefh
        """        
        acc = []
        for term in self.terms:
            if not acc:
                acc = term.cartesian_product()
            else:
                acc = [acc_string + extension for acc_string in acc for extension in term.cartesian_product()]
        return acc
