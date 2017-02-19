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

    def notEmpty(self):
        return not self.empty()
    
    def head(self):
        return self._list[self.index]
    
    def tail(self):
        if self.empty():
            raise Exception("tail called on empty Cursor")
        else:
            return Cursor(self._list, self.index + 1)

    def isAt(self, other_cursor):
        return self.index == other_cursor.index
        
    def find(self, isMatch):
        """
        Returns None if `isMatch` does not return a truthy value 
        for any item in this cursor, or a pair if it does: 
        the truthy value returned from `isMatch`, and the cursor at the matching item.
        """
        match = None
        cursor = self
        while cursor.notEmpty() and (cursor.isAt(self) or not match):
            match = isMatch(cursor.head())
            cursor = cursor.tail()
        return (match, cursor)

    def map_while(self, map_fn):
        """
        Maps elements of this cursor via `map_fn` until `map_fn` returns falsy.
        """
        mappings = []
        cursor = self
        mapping = None
        while cursor.notEmpty() and (cursor.isAt(self) or mapping):
            mapping = map_fn(cursor.head())
            if mapping:
                mappings.append(mapping)
            cursor = cursor.tail()
        return (mappings, cursor)
            
    def crawl_while(self, crawl):
        mappings = []
        cursor = self
        mapping = None
        while cursor.notEmpty() and (cursor.isAt(self) or mapping):
            (mapping, cursor) = crawl(cursor)
            if mapping:
                mappings.append(mapping)
        return (mappings, cursor)
    

    
    
