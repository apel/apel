import datetime
import shutil
import tempfile
import unittest

from apel.db.apeldb import ApelDbException
from apel.db.records import StorageRecord
from apel.db.unloader import DbUnloader, get_start_of_previous_month


class TestDbUnloader(unittest.TestCase):
    '''
    Test case for DbUnloader.
    '''

    def setUp(self):
        # Create temporary directory for dirq to write to
        self.dir_path = tempfile.mkdtemp()
        self.unloader = DbUnloader(None, self.dir_path)

    def test_write_star_to_apel(self):
        """Check that unloading StAR records to APEL format is prevented."""
        self.assertRaises(ApelDbException, self.unloader._write_messages,
                          StorageRecord, 'table', 'query', ur=False)

    def tearDown(self):
        shutil.rmtree(self.dir_path)


class TestFunctions(unittest.TestCase):

    def test_get_start_of_previous_month(self):

        dt = datetime.datetime(2012, 1, 1, 1, 1, 1)
        dt2 = datetime.datetime(2011, 12, 1, 0, 0, 0)
        ndt = get_start_of_previous_month(dt)
        self.assertEqual(dt2, ndt)

        dt3 = datetime.datetime(2012, 3, 1, 1, 1, 1)
        dt4 = datetime.datetime(2012, 2, 1, 0, 0, 0)
        ndt = get_start_of_previous_month(dt3)
        self.assertEqual(dt4, ndt)

if __name__ == '__main__':
    unittest.main()
