from itertools import takewhile, islice

class Segment:
    """
    Represents one segment in the input to cartesian_product.
    A sort of AST produced from parsing an input string.
    """
    # __eq__ enables deep-equals of objects in tests
    # http://stackoverflow.com/questions/22332729/how-to-do-a-deepequals-on-a-object-in-python
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def toSets(self):
        raise AbstractMethodCall("Segment.toSets")

class AbstractMethodCall(Exception):
    pass

class ParseException(Exception):
    pass

class Static(Segment):
    """
    Represents a segment of static characters in a cartesian product string.
    """
    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return "Static({0})".format(self.string)

    def toSets(self):
        return [self.string]

class Multiplier(Segment):
    """
    Represents a set of "multiplier" characters in a cartesian product string.
    """
    def __init__(self, options):
        self.options = options

    def __repr__(self):
        return "Multiplier({0})".format(",".join(self.options))

    def toSets(self):
        return self.options

def cartesian_product(sets, index = 0):
    """     
    Returns the list of strings that is the cartesian product of `sets`,
    which is a list of lists of strings.

    # TODO: explain implementation
    
    """
    if index == len(sets):
        return []
    else:

        # branches at this level of the tree
        variations = sets[index]
    
        # the cartesian product of all branches one level down
        rest = cartesian_product(sets, index + 1)

        # we're at the leaves - start accumulating back up the tree
        if not rest:
            return variations
        else:
            # for each child string, create a variation for each variation at this level
            # TODO: I'll bet string concat is slow. could append segments and then join.
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
    return segments

def parse_segment(chars):
    if chars[0] == "}":
        raise ParseException("Closing brace found before open brace: " + str(chars))
    elif chars[0] == "{":
        return parse_multiplier(chars)
    else:
        return parse_static(chars)

def parse_static(chars):
    static = list(takewhile(lambda c: c not in ["{", "}"], chars))
    return (Static(''.join(static)), len(static))
        
def parse_multiplier(chars):
    rest = islice(chars, 1, None)
    spec = list(takewhile(lambda c: c != "}", rest))
    # TODO: turns out this is wrong - multipliers can nest!  they're full sub-expressions.  need to revamp the design a bit.
    if "{" in spec:
        raise ParseException("Second opening brace found before closing brace: " + str(chars))
    else:
        variations = "".join(spec).split(",")
        # 2 for the opening and closing brace
        return (Multiplier(variations), 2 + len(spec))

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
    units = parse_bash_cp(spec)
    multipliers =  [u.toSets() for u in units]
    permutations = cartesian_product(multipliers)
    return " ".join(permutations)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: bash_cartesian_product '<input string>'\n")
        sys.exit(1)
    else:
        spec = sys.argv[1]
        print(bash_cartesian_product(spec))
        sys.exit(0)
    
            
