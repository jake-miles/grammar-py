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

    # produces the list of strings that is this expression's cartesian product
    def cartesian_product(self):
        raise Exception("Call to abstract method Expression.product")

    # TODO: could take a function to yield to to define the cartesian product
    # multiplication step.
    
    """ 
    Returns the result of appending `other` to this expression,
    however "append" is defined for this type,
    or None if it can't be appended.  The intention here is to let the
    parser simplify the resulting syntax tree, to combine adjacent expressions
    that can be combined.
    """
    def append(self, other):
        raise Exception("Call to abstract method Expression.append")

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

    def append(self, other):
        return other

    
class Lit(Expression):
    "Represents a literal string, whose cartesian product is that string"
    
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Lit({0})".format(",".join(self.value))
        
    def cartesian_product(self):
        return [self.value]

    # consolidate adjacent Lit's into one 
    def append(self, other):
        return other is Lit and Lit(self.value + other.value)

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
    
    def __init__(self, variations):
        self.variations = variations

    def __repr__(self):
        return "Or({0})".format(",".join([str(s) for s in self.variations]))

    # Or's don't concatenate.  two adjacent Ors remain separate and multiply togethere.
    def append(self, other):
        return None
    
    # flattens the results of evaluating the disjunction's branches
    def cartesian_product(self):
        all = []
        for v in self.variations:
            all.extend(v.cartesian_product())
        return all

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

    # consolidates adjacent Ands into one 
    def append(self, other):
        new_terms = this.terms.copy()
        new_terms.append(other)
        return And(new_terms)
    
    # this is the main calculation of the cartesian product

    def cartesian_product(self, index = 0):
        if index == len(self.terms):
            return []
        else:
            
            # branches at this level of the tree
            sub_product = self.terms[index].cartesian_product()
            
            # the cartesian product of all the terms to the right of the one at index
            product_of_rest = self.cartesian_product(index + 1)
            
            # we're at the leaves - start accumulating back up the tree
            if not product_of_rest:
                return sub_product
            else:
                # for all the strings produced by the rest of the And,
                # create one variation per string in this term's cartesian product.
                # TODO: I'll bet string concat is slow. could concat segments and then reverse and join.
                return [sub_result + rest_result for sub_result in sub_product for rest_result in product_of_rest]
