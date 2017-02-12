import itertools

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
    def __init__(self, method_name):
        super("Call to abstract method " + method_name) 

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
    print("cartesian_product: " + str(index))
    
    # `index` is the index of the current set in `sets`, i.e. the current node
    # in the tree.
    #
    if index == len(sets):
        return []
    else:

        variations = sets[index]
        
        rest = cartesian_product(sets, index + 1)

        if not rest:
            return variations
        else:
            # for each child string, create a variation for each path in `fork`
            return [v + result for result in rest for v in variations]

def parse_bash_cp(spec):
    """
    `spec` is the input string to `bash_cartestian_product`.
    Parses `spec` into a list of Segments.
    """
    return []

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
    multipliers =  [u.options() for u in units]
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
    
            
