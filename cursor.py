from itertools import islice

class Cursor:
    
    def __init__(self, _list, index = 0):
        self._list = _list
        self.index = index

    def __repr__(self):
        return "Cursor: " + ",".join([str(self._list[c]) for c in range(self.index, len(self._list))])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def empty(self):
        return self.index == len(self._list)

    def head(self):
        return self._list[self.index]
    
    def tail(self):
        if self.empty():
            return self
        else:
            return Cursor(self._list, self.index + 1)
