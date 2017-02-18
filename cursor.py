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

    def find(self, isMatch):
        """
        Returns None if `isMatch` does not return true for any item in this cursor,
        or a pair if it does: the matching item, and the cursor at the matching item.
        """
        (match, cursor) = (None, self)
        while cursor.notEmpty() and (cursor.isAt(self) or not isMatch(cursor.head()):
            (match, cursor) = (cursor.head(), cursor)
        return match and (match, cursor)

    def isAt(self, other_cursor):
        return self.index == other_cursor.index

    def crawl_while(self, crawl, keep_going):
        mappings = []
        cursor = self
        while cursor.notEmpty() and (cursor.isAt(self) or keep_going(cursor.head(), cursor)):
            (mapping, cursor) = crawl(cursor)
            if mapping:
                mappings.append(mapping)
        return (mappings, cursor)
    

    
    
