import re
from cursor import Cursor
from bash_cartesian_product_grammar import top_level_expr
from cartesian_product_model import Empty

def parse(string):
    """
    The entry point to parse a bash cartesian product string in a syntax tree,
    which will be a subtype of class `Expression`,
    defined in "cartesian_product_calc.py"
    """
    cursor = create_cursor(string)
    (result, _) = top_level_expr.parse(cursor)
    return (result and result.value) or Empty()


def create_cursor(string):
    # includes the delimiters and characters between them
    tokens = re.split('([{},])', string)
    non_empty = [token for token in tokens if token != ""]
    return Cursor(non_empty)


