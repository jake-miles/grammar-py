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

    def test_false_midway(self):
        start = Cursor([1,2,3])
        (mappings, end) = start.map_while(lambda n: n < 3 and (n * -1))
        self.assertEqual(mappings, [-1, -2])
        self.assertEqual(end, start.at(2))

    def test_maps_all(self):
        start = Cursor([1,2,3])
        (mappings, end) = start.map_while(lambda n: n < 4 and (n * -1))
        self.assertEqual(mappings, [-1, -2, -3])
        self.assertTrue(end.empty())

        
class CursorTestNextMap(unittest.TestCase):
            
    def test_false_on_empty(self):
        start = Cursor([])
        (match, end) = start.next_map(lambda n: n == 1 and n * -1)
        self.assertFalse(match)
        self.assertTrue(end.empty())
                
    def test_matches_first(self):
        start = Cursor([1,2,3])
        (match, end) = start.next_map(lambda n: n == 1 and n * -1)
        self.assertEqual(match, -1)
        self.assertEqual(end, start)
        
    def test_matches_midway(self):
        start = Cursor([1,2,3])
        (match, end) = start.next_map(lambda n: n == 2 and n * -1)
        self.assertEqual(match, -2)
        self.assertEqual(end, Cursor([1,2,3], 1))
                             
    def test_fails_to_match(self):
        start = Cursor([1,2,3])
        (match, end) = start.next_map(lambda n: n == 4 and n * -1)
        self.assertFalse(match)
        self.assertTrue(end.empty())



# This contrived crawl example collects lists of cursor elements
# where each list is one larger than the previous one, until it hits a number >= 10.
# To ensure that `crawl_while` is collecting the values we return
# and not just groups of the original cursor values, this also negates the numbers.
def crawl(start):

    # a hack to let collect_group modify a closure variable.
    class count: pass
    count.val = 2
    
    def collect_next_group(cursor):
        collected = []
        while cursor.not_empty() and cursor.head() < 10 and len(collected) < count.val:
            collected.append(cursor.head() * -1)
            cursor = cursor.tail()
        count.val = count.val + 1
        return (collected, cursor)
        
    return start.crawl_while(collect_next_group)

        
class CursorTestCrawlWhile(unittest.TestCase):
                
    def test_empty_returns_empty(self):
        start = Cursor([])              
        (mappings, end) = crawl(start)
        self.assertEqual(mappings, [])
        self.assertTrue(end.empty())
        
    def test_false_on_first(self):
        start = Cursor([10, 9, 8])
        (mappings, end) = crawl(start)
        self.assertEqual(mappings, [])
        self.assertEqual(end, start)
        
    def test_crawl_once(self):
        start = Cursor([1,2,10,11,12])
        (mappings, end) = crawl(start)
        self.assertEqual(mappings, [[-1,-2]])
        self.assertEqual(end, start.at(2))

    def test_multiple_crawls(self):
        start = Cursor(range(15))
        (mappings, end) = crawl(start)
        self.assertEqual(mappings, [[0,-1], [-2,-3,-4], [-5,-6,-7,-8], [-9]])
        self.assertEqual(end, start.at(10))

    def test_crawls_to_end(self):
        start = Cursor(range(10))
        (mappings, end) = crawl(start)
        self.assertEqual(mappings, [[0,-1], [-2,-3,-4], [-5,-6,-7,-8], [-9]])
        self.assertTrue(end.empty())

    
if __name__ == '__main__':
    unittest.main()
