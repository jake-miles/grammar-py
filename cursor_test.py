import unittest
from cursor import Cursor

class CursorTest(unittest.TestCase):

    def test_cursor_start_empty_true(self):
        self.assertEqual(Cursor([]).empty(), True)

    def test_cursor_start_empty_false(self):
        self.assertEqual(Cursor([1]).empty(), False)

    def test_cursor_tail_empty_false(self):
        self.assertEqual(Cursor([1,2]).tail().empty(), False)

    def test_cursor_tail_empty_true(self):
        self.assertEqual(Cursor([2]).tail().empty(), True)

    def test_cursor_head(self):
        self.assertEqual(Cursor([1,2,3]).head(), 1)

    def test_cursor_tail(self):
        self.assertEqual(Cursor([1,2,3]).tail(), Cursor([1,2,3], 1))

    def test_cursor_traversal(self):
        items = []

        cursor = Cursor([1,2,3])
        items.append(cursor.head())

        tail1 = cursor.tail()
        items.append(tail1.head())
        
        tail2 = tail1.tail()
        items.append(tail2.head())
        
        tail3 = tail2.tail()

        self.assertEqual(items, [1,2,3])
        self.assertTrue(tail3.empty())
        self.assertTrue(tail3.tail().empty())

        
if __name__ == '__main__':
    unittest.main()
