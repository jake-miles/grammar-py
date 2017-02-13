from itertools import takewhile, islice

class Expression:
    """
    Represents one segment in the input to cartesian_product.
    A sort of AST produced from parsing an input string.
    """
    # __eq__ enables deep-equals of objects in tests
    # http://stackoverflow.com/questions/22332729/how-to-do-a-deepequals-on-a-object-in-python
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # returns a set of strings to multiply with other sets of strings
    def branches(self):
        raise AbstractMethodCall("Expression.branches")

class AbstractMethodCall(Exception):
    pass

class ParseException(Exception):
    pass

class Lit(Expression):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Lit({0})".format(",".join(self.value))
        
    def branches(self):
        return [self.value]

class Or(Expression):

    def __init__(self, variations):
        self.variations = variations

    def __repr__(self):
        return "Or({0})".format(",".join([str(s) for s in self.variations]))
        
    # flattens any sub-Ors into a single list of variations
    def branches(self):
        all = []
        for v in self.variations:
            all.extend(v.branches())
        return all

class And(Expression):

    def __init__(self, ors):
        self.ors = ors

    def __repr__(self):
        return "And({0})".format(",".join([str(s) for s in self.ors]))

    def branches(self):
        return product(self)

    def product(self, index = 0):
        if index == len(self.ors):
            return []
        else:
            
            # branches at this level of the tree
            variations = self.ors[index].branches()
            
            # the cartesian product of all the ors to the right of the one at index
            rest = self.product(index + 1)
            
            # we're at the leaves - start accumulating back up the tree
            if not rest:
                return variations
            else:
                # for each string to the right, create a string for each variation at this level
                # TODO: I'll bet string concat is slow. could append segments and then reverse and join.
                return [v + result for v in variations for result in rest]

def parse_bash_cp(spec):
    """
     `spec` is the input string to `bash_cartestian_product`.
     Parses `spec` into a list of Segments.
     """
    segments = []
    remaining = list(spec)
    while remaining:
        (segment, length) = parse_segment(remaining)
        segments.append(segment)
        remaining = list(islice(remaining, length, None))
    return And(segments)

def parse_segment(chars):
    if chars[0] == "}":
        raise ParseException("Closing brace found before open brace: " + str(chars))
    elif chars[0] == "{":
        return parse_or(chars)
    else:
        return parse_literal(chars)

def parse_literal(chars):
    static = list(takewhile(lambda c: c not in ["{", "}"], chars))
    return (Lit(''.join(static)), len(static))
        
def parse_or(chars):
    rest = islice(chars, 1, None)
    spec = list(takewhile(lambda c: c != "}", rest))
    # TODO: turns out this is wrong - multipliers can nest!  and they're full sub-expressions, and curlies without commas denote literal curlies.  need to revamp the parser.
    if "{" in spec:
        raise ParseException("Second opening brace found before closing brace: " + str(chars))
    else:
        variations = "".join(spec).split(",")
        # 2 for the opening and closing brace
        return (Or([Lit(v) for v in variations]), 2 + len(spec))

def bash_cartesian_product(spec):
    """

    Returns the "bash cartesian product", a space-delimited string
    of permutations, as described by the specification string `spec`.

    todo: define bash cartesian product

    >>> bash_cartesian_product("a{b,c}d{e,f,g}hi")
    abdehi abdfhi abdghi acdehi acdfhi acdghi

    >>> bash_cartesian_product("a{b,c{d,e,f}g,h}ij{k,l}")
    abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl
    """
    andExpr = parse_bash_cp(spec)
    strings = andExpr.product()
    return " ".join(strings)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: bash_cartesian_product '<input string>'\n")
        sys.exit(1)
    else:
        spec = sys.argv[1]
        print(bash_cartesian_product(spec))
        sys.exit(0)
    
            
