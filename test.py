import ban

import io
import unittest



def getEntryEqualityFunc(obj):
    """The comparator function is used to compare the ban.entry objects"""
    def comparator(leftEntry, rightEntry, msg=None):
        if leftEntry.getSha() != rightEntry.getSha():
            raise obj.failureException(f'SHA {leftEntry.getSha()} != {rightEntry.getSha()}')

        if leftEntry.getPath() != rightEntry.getPath():
            raise obj.failureException(f'path {leftEntry.getPath()} != {rightEntry.getPath()}')
    return comparator



class testEquality(unittest.TestCase):
    """Test the comparator function from this test suite"""

    def setUp(self):
        self.addTypeEqualityFunc(ban.entry, getEntryEqualityFunc(self))

    def testEqual(self):
        left = ban.entry('123', '/path')
        right = ban.entry('123', '/path')

        self.assertEqual(left, right)

    def testUnEqual(self):
        left = ban.entry('12', '/pa')
        right = ban.entry('123', '/path')

        self.assertNotEqual(left, right)



class TestRead(unittest.TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(ban.entry, getEntryEqualityFunc(self))

    def testReadNormal(self):
        """Test that a normal line is read just fine"""

        buf = io.StringIO('0123456789012345678901234567890123456789012345678901234567890123 /path/to/file')

        what = ban.readEntries(buf)
        expected = ban.entry('0123456789012345678901234567890123456789012345678901234567890123', '/path/to/file')

        self.assertEqual(what[0], expected)

    # def testReadWithSpaces(self):
