from cartesian_product_parse import parse

def bash_cartesian_product(spec):
    """

    Returns the "bash cartesian product", a space-delimited string
    of permutations, as described by the specification string `spec`.
    
    The string specifies a disjunction with a pair of curly braces
    containing comma-delimited variations to introduce at that point in
    the string.

    Note that curly braces not containing a comma denote literal curly braces,
    and a comma not contained within curly braces denotes a literal comma.

    >>> bash_cartesian_product("a{b,c}d{e,f,g}hi")
    abdehi abdfhi abdghi acdehi acdfhi acdghi

    >>> bash_cartesian_product("a{b,c{d,e,f}g,h}ij{k,l}")
    abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl
    """
    expression_tree = parse(spec)
    variations = expression_tree.cartesian_product()
    return " ".join(variations)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: bash_cartesian_product '<input string>'\n")
        sys.exit(1)
    else:
        spec = sys.argv[1]
        print(bash_cartesian_product(spec))
        sys.exit(0)
    
            
