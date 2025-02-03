import ban

import io
import unittest



def get_entry_equality_func(obj):
    """The comparator function is used to compare the ban.Entry objects"""
    def comparator(leftEntry, rightEntry, msg=None):
        if leftEntry.get_sha() != rightEntry.get_sha():
            raise obj.failureException(f'SHA "{leftEntry.get_sha()}" != "{rightEntry.get_sha()}"')

        if leftEntry.get_path() != rightEntry.get_path():
            raise obj.failureException(f'path "{leftEntry.getPath()}" != "{rightEntry.getPath()}"')
    return comparator



class TestEquality(unittest.TestCase):
    """Test the comparator function from this test suite"""

    def setUp(self):
        self.addTypeEqualityFunc(ban.Entry, get_entry_equality_func(self))

    def testEqual(self):
        left = ban.Entry('123', '/path')
        right = ban.Entry('123', '/path')

        self.assertEqual(left, right)

    def testUnEqual(self):
        left = ban.Entry('12', '/pa')
        right = ban.Entry('123', '/path')

        self.assertNotEqual(left, right)



class TestFiltering(unittest.TestCase):
    def testAllAllowed(self):
        pathToExclude = ['./some/path']
        entries = [ban.Entry('123', './path1'),
                   ban.Entry('234', './path2')]
        result = ban.filter_entries(entries, pathToExclude)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get_sha(), '123')
        self.assertEqual(result[0].get_path(), './path1')
        self.assertEqual(result[1].get_sha(), '234')
        self.assertEqual(result[1].get_path(), './path2')

    def testFilterOutSome(self):
        pathToExclude = ['./some/path']
        entries = [ban.Entry('123', './path1'),          # stays
                   ban.Entry('234', './some/path'),      # removed
                   ban.Entry('567', './path3'),          # stays
                   ban.Entry('890', './some/path/1'),    # removed
                   ban.Entry('901', './some/path/'),     # removed
                   ban.Entry('251', './some/path/file'), # removed
                   ban.Entry('982', './some/other')]     # stays
        result = ban.filter_entries(entries, pathToExclude)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].get_sha(), '123')
        self.assertEqual(result[0].get_path(), './path1')
        self.assertEqual(result[1].get_sha(), '567')
        self.assertEqual(result[1].get_path(), './path3')
        self.assertEqual(result[2].get_sha(), '982')
        self.assertEqual(result[2].get_path(), './some/other')

class TestAppleDoubleeFilesFiltering(unittest.TestCase):
    def teastAllAllowed(self):
        entries = [ban.Entry('123', './path1'),
                   ban.Entry('234', './p[ath2')]
        result = ban.filter_out_apple_doubles(entries)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get_sha(), '123')
        self.assertEqual(result[0].get_path(), './path1')
        self.assertEqual(result[1].get_sha(), '234')
        self.assertEqual(result[1].get_path(), './path2')

    def testFilterOutSome(self):
        entries = [ban.Entry('123', './path1'),
                   ban.Entry('143', './._path1'),
                   ban.Entry('345', './some/path.jpg'),
                   ban.Entry('945', './some/._path.jpg'),
                   ban.Entry('903', './other/._file.dng')]
        result = ban.filter_out_apple_doubles(entries)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get_sha(), '123')
        self.assertEqual(result[0].get_path(), './path1')
        self.assertEqual(result[1].get_sha(), '345')
        self.assertEqual(result[1].get_path(), './some/path.jpg')


class TestRead(unittest.TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(ban.Entry, get_entry_equality_func(self))

    def testReadNormal(self):
        """Test that a normal line is read just fine"""

        buf = io.StringIO('0123456789012345678901234567890123456789012345678901234567890123 /path/to/file')

        entries = ban.read_entries(buf)
        expected = ban.Entry('0123456789012345678901234567890123456789012345678901234567890123', '/path/to/file')

        self.assertEqual(entries[0], expected)


    def testReadWithSpaces(self):
        """Test that paths with space are read properly"""

        buf = io.StringIO('0123456789012345678901234567890123456789012345678901234567890123 /path/to/file with spaces')

        entries = ban.read_entries(buf)
        expected = ban.Entry('0123456789012345678901234567890123456789012345678901234567890123', '/path/to/file with spaces')

        self.assertEqual(entries[0], expected)


    def testReadTwoSpaces(self):
        '''
        Two spaces are the separator between the hash and the file path.
        Emited by sha256sum, two spaces mean that the file was read in a text mode,
        as opposed to the * separator used for binary reading mode.
        '''

        buf = io.StringIO('0123456789012345678901234567890123456789012345678901234567890123  /path/to/file with spaces')

        entries = ban.read_entries(buf)
        expected = ban.Entry('0123456789012345678901234567890123456789012345678901234567890123', '/path/to/file with spaces')

        self.assertEqual(entries[0], expected)
