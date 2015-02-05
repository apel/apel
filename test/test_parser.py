import bz2
import ConfigParser
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

    def test_handle_parsing(self):
        """Check handle_parsing in a basic way (i.e. no errors raised)."""
        # Construct the location of the parser config file.
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                            'conf', 'parser.cfg'))
        # Read the config and fill in empty values.
        self.cp = ConfigParser.ConfigParser()
        self.cp.read(path)
        self.cp.set('site_info', 'site_name', 'TestSite')
        self.cp.set('site_info', 'lrms_server', 'TestServer')
        # It's hard to test handle_parsing, but we can check that no erorrs are
        # raised and that the load_records method is called with an empty list.
        bin.parser.handle_parsing('SGE', self.mock_db, self.cp)
        self.mock_db.load_records.assert_called_once_with([])

    def tearDown(self):
        self.tf.close()
        mock.patch.stopall()


if __name__ == '__main__':
    unittest.main()
