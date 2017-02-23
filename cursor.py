from itertools import islice

class Cursor:
    """
    Represents a cursor on a python list.  Provides non-destructive iteration
    over the list using a `head` and `tail` method, akin to a linked list,
    and a few other methods to enable iteration over the list.

    The intention is to allow iteration over a list and holding onto different 
    tails in the list without copying or modifying anything.
    """
    
    def __init__(self, _list, index = 0):
        self._list = _list
        self.index = index

    def __repr__(self):
        return "Cursor: " + str([str(self._list[c]) for c in range(self.index, len(self._list))])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def empty(self):
        "Returns true if this cursor is at the end of its list or its list is empty."
        return self.index == len(self._list)

    def not_empty(self):
        "Returns true if this cursor is not yet at the end of its list."
        return not self.empty()
    
    def head(self):
        "Returns the head of the list."
        return self._list[self.index]
    
    def tail(self):
        """
        Returns the tail of the list, i.e. the rest of the list without `self.head()`.
        Does not modify the underlying list.
        """
        if self.empty():
            raise Exception("tail called on empty Cursor")
        else:
            return Cursor(self._list, self.index + 1)

    def at(self, index):
        """
        Returns a new Cursor on this Cursor's list, at the specified index.
        Does not copy the underlying list.
        """
        return Cursor(self._list, index)
        
    def map_while(self, map_fn):
        """
        Maps elements of this cursor via `map_fn` until `map_fn` returns falsy.
        Returns the collected list of mapped elements, and a
        Cursor positioned at the first element in the list that 
        mapped to a falsy value.
        """
        mappings = []
        cursor = self
        mapping = True
        while cursor.not_empty() and mapping:
            mapping = map_fn(cursor.head())
            if mapping:
                mappings.append(mapping)
                cursor = cursor.tail()
        return (mappings, cursor)

    
    def crawl_while(self, crawl):
        """
        Similar to map_while, but lets the `crawl` function specify
        a Cursor at which to continue mapping elements.

        `crawl` returns a pair containing:
        1) a non-falsy value to add to the collected list of values, 
           or a falsy value to stop the traversal of the list.
        2) the Cursor on which to continue the mapping (i.e. representing
           some later position in the list).  
        
        Unlike `map_while`, this does not map each element of the list in turn
        to a new value, but lets `crawl` map the next n elements of the list
        into a new value.  So `crawl` traverses as much of the list as it needs
        to produce the next element in the resulting list, and returns
        the Cursor at which to call it with on the next step of the crawl.

        Although the cursor returned by `crawl` will probably be one of this 
        cursor's tails, you could theoretically switch midway to an entirely 
        different cursor if you like, and this will still behave as expected, 
        continuing the crawl on the returned cursor and stopping when `crawl` 
        returns a falsy match or an empty cursor.  However, this might be a bit
        confusing to the reader.
        """
        mappings = []
        cursor = self
        result = True
        mapping = True                
        while cursor.not_empty() and result and mapping:
            result = crawl(cursor)
            if result:                
                (mapping, cursor) = result
                if mapping:
                    mappings.append(mapping)
        return (mappings, cursor)
    

    
    
