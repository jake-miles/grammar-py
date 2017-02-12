# Jake Miles Energy Hub Assignment

Python implementation of a bash cartesian product.

## Command-line usage:
```
> python cartesian_product '<input string>'
```

Be sure to enclose <input string> in single quotes so bash doesn't interpret it :)

## Examples
```
$ python cartesian_product 'a{b,c}d{e,f,g}hi'
abdehi abdfhi abdghi acdehi acdfhi acdghi

$ python cartesian_product 'a{b,c{d,e,f}g,h}ij{k,l}'
abijk abijl acdgijk acdgijl acegijk acegijl acfgijk acfgijl ahijk ahijl
```

## To run tests:

```
python cartesian_product_test.py
```
