import bz2
import gzip
import os
import re
import shutil
import tempfile
import unittest

import mock

import bin.parser


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.tf = tempfile.TemporaryFile()
        self.patcher = mock.patch('apel.db.apeldb.ApelDb')
        self.mock_db = self.patcher.start()

        self.mock_parser = mock.Mock()

    def test_parse_empty_file(self):
        """An empty file should be ignored and no errors raised."""
        bin.parser.parse_file(None, self.mock_db, self.tf, False)

    def test_scan_dir(self):
        """
        Check that scan dir works with bzip, gzip and normal files.
        """
        dir_path = tempfile.mkdtemp()

        try:
            # Create a bzip, gzip and normal file in turn in the temp directory
            for method, suffix in ((bz2.BZ2File, '.bzip2'),
                                   (gzip.open, '.gzip'),
                                   (open, '.normal')):
                handle, path = tempfile.mkstemp(suffix, dir=dir_path)
                os.close(handle)
                file_obj = method(path, 'wb')
                # Write three lines to the file
                file_obj.write("Line one.\nLine two.\nLine three.")
                file_obj.close()
            records = bin.parser.scan_dir(self.mock_parser, dir_path, False,
                                          re.compile('(.*)'), self.mock_db, [])
            for record in records:
                # Check that all three lines have been read
                self.assertEqual(record.get_field('StopLine'), 3,
                                 "Unable to read %s file"
                                 % record.get_field('FileName').split('.')[1])
        finally:
            shutil.rmtree(dir_path)

    def tearDown(self):
        self.tf.close()
        self.patcher.stop()


if __name__ == '__main__':
    unittest.main()
