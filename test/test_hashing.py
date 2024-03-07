import tempfile
import unittest
import os

from apel.common import calculate_hash


class HashingTest(unittest.TestCase):
    '''
    Test case for calculate_hash method.
    '''

    def test_calculate_hash(self):

        data = b'01010101' * 200
        data_hash = '3d1eb00cc63828b36882f076f35c8cdd'

        tmpname = tempfile.mktemp('hashtest')
        fp = open(tmpname, 'wb')
        fp.write(data)
        fp.close()

        self.assertEqual(data_hash, calculate_hash(tmpname))

        os.unlink(tmpname)

if __name__ == '__main__':
    unittest.main()
