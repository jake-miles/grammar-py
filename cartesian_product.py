class CPUnit:
    """
    Represents one segment in the input to cartesian_product.
    """
    # enables deep-equals in tests
    # http://stackoverflow.com/questions/22332729/how-to-do-a-deepequals-on-a-object-in-python
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class AbstractMethodCall(Exception):
    def __init__(self, method_name):
        super("Call to abstract method " + method_name) 

class Static(CPUnit):
    """
    Represents a segment of static characters in a cartesian product string.
    """
    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return "Static({0})".format(self.string)

class Multiplier(CPUnit):
    """
    Represents a set of "multiplier" characters in a cartesian product string.
    """
    def __init__(self, chars):
        self.chars = chars

    def __repr__(self):
        return "Multiplier({0})".format(",".join(self.chars))

def cartesian_product(segments):
    """    
    Takes a list of CPUnit, returns a list of strings.
    """
    pass

def parse_bash_cp(spec):
    """
    `spec` is the input string to `bash_cartestian_product`.
    Parses `spec` into a list of CPUnit (input to cartesian_product)
    """
    pass

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
    segments = parse_bash_cp(spec)
    permutations = cartesian_product(segments)
    return permutations.join(" ")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: bash_cartesian_product '<input string>'\n")
        sys.exit(1)
    else:
        spec = sys.argv[1]
        print(bash_cartesian_product(spec))
        sys.exit(0)
    
            
