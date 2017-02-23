# Bash cartesian product in python

Python implementation of a bash cartesian product, intended as a drop-in
replacement for bash's cartesian product functionality (done as a coding exercise,
not intended to actually replace bash's implementation, which works quite well already).

## Command-line usage:
```
> python cartesian_product.py 'input string'
```

Be sure to enclose the input string in single quotes so bash doesn't interpret it :)

## Examples
```
$ python cartesian_product.py 'a{b,c}d{e,f,g}hi'
abdehi abdfhi abdghi acdehi acdfhi acdghi

$ python cartesian_product.py 'a{b,c{d,e,f}g,h}ij{k,l}'
abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl
```

## To run the tests:

```
python -m unittest discover -p "*_test.py" 
```

### TODO: One failing test

There is currently one failing test in `cartesian_product_parse_test.py`, which I'm
still investigating.  The pydoc in the test method explains the details of the 
failing case.  It was not quite clear to me from the original requirements 
whether handling that case was part of the scope; I did my best to produce 
a drop-in replacement for bash's behavior, which does handle that case, 
but differently than my code.  The two example inputs don't include anything like 
that case, so it was unclear how close a facsimile of bash's implementation 
was expected.  I did my best to reproduce it exactly.

## The design and implementation: parse / compute / pretty-print

The top-level script, `cartesian_product.py` glues together three steps:
1) parsing the input string into a model,
2) traversing the model to calculate the cartesian product strings,
3) joining the strings into a single string and outputting it (just a call to `join()`).

The functionality is split up among the following modules.  Each includes a corresponding unit test module.

### cartesian_product_model.py

The core calculation of the resulting strings is handled by a set of model classes -
subclasses of an abstract class `Expression`, representing the tree structure of the 
input and providing a method `cartesian_product()` that does the calculation.

The four subclasses used to calculate the cartesian product are:

- Empty: represents an empty cartesian product,
- Lit: represents a literal string like "a",
- And: represents a sequence of Expressions, such as "abc{d,e}" - a literal followed by a disjunction,
- Or: represents a disjunction of Expressions that multiply the results at that point in the input string.

For example, the string "abc{d,e}" would turn into the Expression:
```
And([Lit("abc"), 
     Or([Lit("d"), Lit("e")])])
```

### cursor.py

A Cursor class, representing a cursor along a generic list of items, making
it easy to traverse the list in ways useful to parsing, and specifically do so
without modifying or copying the original list, to enable the backtrack parser 
to backtrack.  Provides the same functionality as a linked list, but backed by 
a python list and therefore providing constant-time access to any index as well.

### grammar.py

A small parser combinator library, i.e. lets you compose a simple grammar
declaratively out of smaller grammar elements, that will parse an 
input string into your target model objects.  It's very barebones
and doesn't currently support any functionality not needed to parse 
the bash cartesian product input.

### bash_cartesian_product_grammar.py

A specific grammar for the bash cartesian product input string, 
composed using `grammar.py`.

### cartesian_product_parse.py

Tokenizes a bash cartesian product input string and parses it into an `Expression` model
using the grammar.

### cartesian_product.py

The top-level script that glues together the parse, compute, pretty-print steps.

## A note on the grammar library

The grammar library grew into a bit more code than I first anticipated,
and possibly more than you anticipated as well :)  Its value is partly
in solving this particular problem and partly just as a cool thing to have written
for my github page.  It was also a lot of fun.  
However, I'm aware that it was not strictly necessary 
to solve the bash cartesian product problem.  I had a "hand-cranked" solution working
when I decided to work out this other more generic approach.  If you'd like to see
that first approach, which is working but which I abandoned before refactoring
it into something more readable, it's [https://github.com/jake-miles/bash-cartesian-python/blob/3efe535a15146df514daaaf1c7a6bdc41ee2f07a/cartesian_product_parse.py](here).
It works for most cases, but fails on some cases involving literal 
curly braces and commas.  I switched to the generic approach when debugging those cases
became complicated, with the guess that solving a more general problem
would prove easier than solving a specific problem. 






