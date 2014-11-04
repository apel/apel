import tempfile
import unittest

import mock

import bin.parser


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.tf = tempfile.TemporaryFile()
        #print self.tf.name
        #self.tf.write('Test text.')
        ## Reset file position to start so it can be read
        #self.tf.seek(0)
        #print self.tf.readline()
        self.patcher = mock.patch('apel.db.apeldb.ApelDb')
        self.mock_db = self.patcher.start()

    def test_parse_empty_file(self):
        """An empty file should be ignored and no errors raised."""
        bin.parser.parse_file(None, self.mock_db, self.tf, False)

    def tearDown(self):
        self.tf.close()
        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()
