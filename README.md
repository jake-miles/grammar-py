# grammar.py: a small parser combinator library in python

A barebones, toy parser combinator library in python, born of a coding exercise that required
some lightweight parsing.  Use it if you find it helpful, 
but for the moment it's just something for me to tinker with, an exercise in 
creating composable abstractions.  Contributors welcome.

`grammar.py` provides a simple grammar definition DSL in python, letting you compose a grammar
from smaller grammar components.  It will then parse an input string matching
that grammar, with facilities to map portions of it into your own abstract syntax tree
or model objects.

For example, assuming there exist AST classes `Addition` and `Number`, and functions `toNumber`, and `toAddition` to map a parser result into each of them (full example down the page a bit):

```
# a composed grammar component
addition = AllOf([AnyToken().map(toNumber).keep('left'), 
                  Token("+"), 
                  AnyToken().map(toNumber).keep('right')]).map(toAddition)

# `tokens` == ["2", "+", "3", "-", "1"]
tokens = re.split('([+-])', "2 + 3 - 1")

start = Cursor[tokens)

(result, end) = addition.parse(start)
```

`result` now equals `Addition("2", "3")`.  `end` is a `Cursor` positioned directly after the "3" (explained later).

## Inspiration

Inspired in part by:

1. Prolog
2. The powerful JavaScript contract library [rho-contracts.js](https://github.com/bodylabs/rho-contracts-fork)
3. [fast-parse](https://github.com/lihaoyi/fastparse)

This library doesn't come close to those giants in almost any respect.  Though it may match interpreted prolog in performance :)

## Repeat: this is only a test

In its current form, `grammar.py` isn't robust enough and doesn't
provide enough features to apply to industrial-strength uses.  

For example, no support for error conditions at the moment; 
like prolog, if it doesn't match it just sticks its tongue out at you.  There's
also zero effort made to make the parsing fast.  It's a recursive descent into 
the grammar tree, backtracking at disjunctions until it finds a match.

If you're looking for a real-world parser library in python, many offerings exist at (https://wiki.python.org/moin/LanguageParsing).

## How to use it
    
You compose a grammar by composing subtypes of `Grammar` into a tree,
tokenize the input string, create a `Cursor` with the tokens, 
and then call `parse` on it with an input Cursor (see `cursor.py`).

`Cursor` is a wrapper around a python list that holds an index into it.  

For example:

```
class Addition:
  "Represents an addition of two numbers"
  def __init__(self, left, right):
    self.left = left
    self.right = right
    
class Number:
  def __init__(self, value):
    self.value = value

# `keeps` is a dictionary of values marked for capturing during parsing using `keep(name)`
def toAddition(value, keeps):
    Addition(keeps['left'], keeps['right'])
    
def toNumber(value, keeps):
    Number(value)

# the grammar
addition = AllOf([AnyToken().map(toNumber).keep('left'), 
                  Token("+"), 
                  AnyToken().map(toNumber).keep('right')]).map(toAddition)

# tokenize however you like
tokens = re.split('([+-])', "2 + 3 - 1")

start = Cursor[tokens]

(result, end) = addition.parse(start)
```
   
`result` now equals `Addition("2", "3")`.  

`end` at that point is the cursor on the input just after parsing the `addition`, so
a Cursor pointing to ["-", "1"]. If there is no more string after matching
a Grammar, `end` would be an empty Cursor.  If it did not match the string,
`result` would be falsy and `end` would be a Cursor matching the original.

## Creating recursive grammars with the `Lazy` grammar

Most useful grammars include some recursive element.  For example, an addition
isn't just applicable to two numbers but to two full arithmetic expressions.
But if we write that grammar, some grammar element will have to refer to some
other grammar element that isn't defined yet - it's defined later down the page.

```
expr = OneOf([number, addition, subtraction])

number = AnyToken().map(int)
addition = AllOf([expr, Token("+"), expr]).map(toAddition)
subtraction = AllOf([expr, Token("-"), expr]).map(Subtraction)
```

`expr` refers to `number`, `addition` and `subtraction`, which don't exist yet.  Python
will complain while parsing the file.  To allow `expr` to refer to others, 
we wrap the forward references in `Lazy`s.

```
expr = OneOf([Lazy(lambda: number), Lazy(lambda: addition), Lazy(lambda: subtraction)])

addition = AllOf([expr, Token("+"), expr])
subtraction = AllOf([expr, Token("-"), expr])
```

`Lazy` is a special `Grammar` that wraps another Grammar and delegates
everything to it, but it doesn't obtain the wrapped `Grammar` until it's
parsing input, i.e. after the referenced `Grammar` has been defined.
To that end, its constructor takes a lambda that produces the wrapped `Grammar`.
It delegates the parsing to and returns the results of that `Grammar`.  So the 

## The Grammar types

These are the components you combine to compose the structure of your grammar:

- `Token`: matches a specific literal string

- `AnyToken`: matches any literal string

- `AllOf`: takes a list of Grammars, and only matches if they can be matched
      against the input in sequence.

- `OneOrMore`: takes a Grammar and matches one or more occurrences of that Grammar
      occurring in sequence in the input.

- `OneOf`: takes a list of Grammars and will try them in order until one
      matches the input.

- `Unless`: takes two Grammars.  The first is a Grammar whose match is negated, i.e.
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

`cursor.py` provides a Cursor class, representing a cursor along a generic list of items. 
It makes it easy to traverse the list in ways useful to parsing, and specifically do so
without modifying or copying the original list, enabling the backtrack parser 
to backtrack.  Provides the same functionality as a linked list, but backed by 
a python list and therefore providing constant-time access to any index as well.

### bash_cartesian_product_grammar.py

A sample grammar for the bash cartesian product input string, 
composed using `grammar.py`.

TODO: there's currently a bug in the grammar; it interprets a somewhat edge case
differently than the real bash cartesian product parser.








