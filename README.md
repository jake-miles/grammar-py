# grammar.py: a small parser combinator library in python

A barebones parser combinator library in python, born of a coding exercise.
Use it if you find it helpful, but it's just a toy for me to tinker with.  

grammar.py provides a simple grammar definition DSL in python, letting you compose a grammar
from smaller grammar components.  It will then parse an input string matching
the grammar, with facilities to map the matched portions into your own model objects.

Inspired in part by:

1. Prolog
2. The powerful JavaScript contract library [rho-contracts.js](https://github.com/bodylabs/rho-contracts-fork)
3. Scala's parser combinator library and [fast-parse](https://github.com/lihaoyi/fastparse)

However, this library doesn't come close to those giants in any respect.
Though it may match interpreted prolog in performance :)

No support for error conditions at the moment; like prolog, if it doesn't match it just
sticks its tongue out at you.

## How to use it
    
You compose a grammar by composing subtypes of `Grammar` into a tree,
and then call `parse` on it with an input Cursor (see `cursor.py`).

For example:

```
class Addition:
  "Represents an addition of two numbers"
  def __init__(self, left, right):
    self.left = left
    self.right = right
    
def toAddition(value, keeps):
    Addition(keeps['left'], keeps['right'])
    
addition = AllOf([AnyToken().map(toNumber).keep('left'), 
                  Token("+"), 
                  AnyToken().map(toNumber).keep('right')]).map(toAddition)

(result, end) = addition.parse(Cursor["2", "+", "3", "-", "1"])

# result == Addition("2", "3")
```
   
`end` at that point is the cursor on the input just after parsing the `addition`, so
a Cursor pointing to ["-", "1"]. If there is no more string after matching
a Grammar, `end` would be an empty Cursor.  If it did not match the string,
`result` would be falsy and `end` would be a Cursor matching the original.

The subtypes you compose to create the structure of the grammar are:

- Token: matches a specific literal string

- AnyToken: matches any literal string

- AllOf: takes a list of Grammars, and only matches if they can be matched
      against the input in sequence.

- OneOrMore: takes a Grammar and matches one or more occurrences of that Grammar
      occurring in sequence in the input.

- OneOf: takes a list of Grammars and will try them in order until one
      matches the input.

- Unless: takes two Grammars.  The first is a Grammar whose match is negated, i.e.
if that Grammar matches, the Unless fails to match the input string.  The
second Grammar is applied only if the first fails, and its value is returned
as the result of the Unless.

When a Grammar matches, it returns a `Result`, which contains a `value`
and a dictionary called `keeps`.  You can modify this `Result` as it
returns up the stack using the following methods on `Grammar`:

`map`: takes a (lambda value, keeps) that is called with the `Result's` `value`
and `keeps` dictionary, and should return whatever the result should map into
(an abstract syntax tree node or other model object).

`keep`: takes a string, and will add the Result's `value` to the `keeps`
dictionary under that name.  This dictionary can then be used by the `map`
lambda of a grammar higher up the tree to create its model object.

`rename`: takes a string, and if you are debugging your grammar 
(set `Grammar.trace = True`), it will use that name instead of the 
Grammar's entire tree structure when logging it.    

For a sample grammar, see `bash_cartesian_product_grammar.py`.

## To run the tests:

```
python -m unittest discover -p "*_test.py" 
```

### cursor.py

`ursor.py` provides a Cursor class, representing a cursor along a generic list of items. 
It makes it easy to traverse the list in ways useful to parsing, and specifically do so
without modifying or copying the original list, enabling the backtrack parser 
to backtrack.  Provides the same functionality as a linked list, but backed by 
a python list and therefore providing constant-time access to any index as well.

### bash_cartesian_product_grammar.py

A sample grammar for the bash cartesian product input string, 
composed using `grammar.py`.

TODO: there's currently a bug in the grammar; it interprets a somewhat edge case
differently than the real bash cartesian product parser.








