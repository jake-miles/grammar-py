from itertools import islice

class Cursor:
    
    def __init__(self, _list, index = 0):
        self._list = _list
        self.index = index

    def __repr__(self):
        return "Cursor: " + str([str(self._list[c]) for c in range(self.index, len(self._list))])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def empty(self):
        return self.index == len(self._list)

    def not_empty(self):
        return not self.empty()
    
    def head(self):
        return self._list[self.index]
    
    def tail(self):
        if self.empty():
            raise Exception("tail called on empty Cursor")
        else:
            return Cursor(self._list, self.index + 1)

    def at(self, index):
        return Cursor(self._list, index)
        
    def is_at(self, other_cursor):
        return self.index == other_cursor.index
                
    def map_while(self, map_fn, while_falsy = False):
        """
        Maps elements of this cursor via `map_fn` until `map_fn` returns falsy.
        If `while_falsy` is true, does the inverse: maps elements
        until `map_fn` returns a non-falsy value.  This is useful
        mainly to implement `find`.
        """
        mappings = []
        cursor = self
        mapping = None
        while cursor.not_empty() and (cursor.is_at(self) or mapping):
            mapping = map_fn(cursor.head())
            if mapping or while_falsy:
                mappings.append(mapping)
            cursor = cursor.tail()
        return (mappings, cursor)

    def next_map(self, map_fn):
        """
        Returns None if `map_fn` does not return a truthy value 
        for any item in this cursor, or a pair if it does: 
        the truthy value returned from `map_fn`, and the cursor at the matching item.

        This is similar to python's built-in `next` except that it returns the
        truthy mapped value, not the element that produced the truthy mapped value.
        """
        (_, cursor) = self.map_while(map_fn, while_falsy = True)
        return (cursor.nonEmpty() and cursor.head(), cursor)
    
    def crawl_while(self, crawl):
        """
        Similar to map_while, but the map function `crawl` returns
        a mapping to add to the collected list of mappings and a
        cursor to continue crawling at.  So it doesn't call `crawl`
        with every element in this cursor, rather lets `crawl` traverse the cursor
        to collect the mapping for that step and specify where to continue the crawl.
        
        Although the cursor you want to return is probably one of this cursor's tails, 
        you could also switch midway to an entirely different cursor if you like 
        and this will still behave as expected, continuing the crawl on the returned
        cursor and stopping when `crawl` returns a falsy match or an empty cursor.
        """
        mappings = []
        cursor = self
        mapping = None
        while cursor.not_empty() and (cursor.is_at(self) or mapping):
            result = crawl(cursor)
            if result:
                (mapping, cursor) = result
                if mapping:
                    mappings.append(mapping)
        return (mappings, cursor)
    

    
    
