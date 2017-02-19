import unittest
from cursor import Cursor

class CursorTest(unittest.TestCase):

    def suite():
        return unittest.TestSuite(map(loadTests, [
            CursorTestTraversal,
            CursorTestFind,
            CursorTestMapWhile,
            CursorTestCrawlWhile
        ]))

class CursorTestTraversal(unittest.TestCase):
    
    def test_start_empty_true(self):
        self.assertEqual(Cursor([]).empty(), True)

    def test_start_empty_false(self):
        self.assertEqual(Cursor([1]).empty(), False)

    def test_tail_empty_false(self):
        self.assertEqual(Cursor([1,2]).tail().empty(), False)

    def test_tail_empty_true(self):
        self.assertEqual(Cursor([2]).tail().empty(), True)

    def test_head(self):
        self.assertEqual(Cursor([1,2,3]).head(), 1)

    def test_tail(self):
        self.assertEqual(Cursor([1,2,3]).tail(), Cursor([1,2,3], 1))

    def test_traversal(self):
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
        

class CursorTestMapWhile(unittest.TestCase):
    
    def test_empty_returns_empty(self):
        start = Cursor([])
        (mappings, end) = start.map_while(lambda n: n == 1 and (n * -1))
        self.assertEqual(mappings, [])
        self.assertTrue(end.empty())

    def test_first_false(self):
        start = Cursor([1,2,3])
        (mappings, end) = start.map_while(lambda n: n < 1 and (n * -1))
        self.assertEqual(mappings, [])
        self.assertEqual(end, start)

    def test_fails_midway(self):
        start = Cursor([1,2,3])
        (mappings, end) = start.map_while(lambda n: n < 3 and (n * -1))
        self.assertEqual(mappings, [-1, -2])
        self.assertEqual(end, Cursor([1,2,3], 1))

    def test_maps_all(self):
        start = Cursor([1,2,3])
        (mappings, end) = start.map_while(lambda n: n < 4 and (n * -1))
        self.assertEqual(mappings, [-1, -2, -3])
        self.assertTrue(end.empty())

        
class CursorTestFind(unittest.TestCase):
            
    def test_find_fails_on_empty(self):
        start = Cursor([])
        (match, end) = start.find(lambda n: n == 1)
        self.assertFalse(match)
        self.assertTrue(end.empty())
                
    def test_find_fails_on_first(self):
        start = Cursor([1,2,3])
        (match, end) = start.find(lambda n: n == 1)
        self.assertEqual(match, 1)
        self.assertEqual(end, start)
        
    def test_find_finds_element_midway(self):
        start = Cursor([1,2,3])
        (match, end) = start.find(lambda n: n == 2)
        self.assertEqual(match, 2)
        self.assertEqual(end, Cursor([1,2,3], 1))
                             
    def test_find_fails_to_find(self):
        start = Cursor([1,2,3])
        (match, end) = start.find(lambda n: n == 4)
        self.assertFalse(match)
        self.assertTrue(end.empty())


class CursorTestCrawlWhile(unittest.TestCase):

    # this (contrived) crawl function collects alternating segments
    # of odd and even numbers until it hits a number >= 10.
    # To ensure that `crawl_while` is collecting the values we return
    # and not groups of the original cursor values, this also negates the numbers.
    def crawl(cursor):

        collect_odd = False
        def collect_group(cursor):
            collect_odd = not collect_odd
            return (collect_odd and cursor.head() % 2 != 0 and cursor.head() * -1)
            
        return cursor.crawl_while(cursor.head() <= 10 and
                                  cursor.map_while(collect_group))

                
    def test_empty_returns_empty(self):
        start = Cursor([])              
        (mappings, end) = CursorTestCrawlWhile.crawl(start)
        self.assertEqual(mappings, [])
        self.assertTrue(end.empty())
        
    def test_false_on_first(self):
        start = Cursor([1,2,3])
        (mappings, end) = CursorTestCrawlWhile.crawl(start)
        self.assertEqual(mappings, [])
        self.assertEqual(end, start)
        
    def test_crawl_once(self):
        start = Cursor([1,3,5,11,2,4,7,9,10,12,13])
        (mappings, end) = CursorTestCrawlWhile.crawl(start)
        self.assertEqual(mappings, [[1,-3,-5]])
        self.assertEqual(end, start.at(3))

    def test_multiple_crawls(self):
        start = Cursor([1,3,5,2,4,7,9,10,12,11,13])
        (mappings, end) = CursorTestCrawlWhile.crawl(start)
        self.assertEqual(mappings, [[1,-3,-5], [-2, -4], [-7,-9]])
        self.assertEqual(end, start.at(7))

    def test_crawls_to_end(self):
        start = Cursor([1,3,5,2,4,7,9])
        (mappings, end) = CursorTestCrawlWhile.crawl(start)
        self.assertEqual(mappings, [[1,-3,-5], [-2, -4], [-7,-9]])
        self.assertTrue(end.empty())

    
if __name__ == '__main__':
    unittest.main()
