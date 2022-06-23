import datetime
import shutil
import tempfile
import unittest

from mock import mock

from apel.db.apeldb import ApelDbException
from apel.db.backends.mysql import ApelMysqlDb
from apel.db.records import StorageRecord
from apel.db.unloader import DbUnloader, get_start_of_previous_month


class TestDbUnloader(unittest.TestCase):
    '''
    Test case for DbUnloader.
    '''

    def setUp(self):
        # Create temporary directory for dirq to write to
        self.dir_path = tempfile.mkdtemp()

        # Mock out the database as we're not testing that here
        # Note that as it's a class it needs instantiating
        self.mock_db = mock.patch(__name__ + '.ApelMysqlDb', autospec=True, spec_set=True)
        self.mock_db.start()

        self._apeldb = ApelMysqlDb('host', 1234, 'user', 'pwd', 'db')

        self.unloader = DbUnloader(self._apeldb, self.dir_path)

    def tearDown(self):
        shutil.rmtree(self.dir_path)

    def test_write_star_to_apel(self):
        """Check that unloading StAR records to APEL format is prevented."""
        self.assertRaises(ApelDbException, self.unloader._write_messages,
                          StorageRecord, 'table', 'query', ur=False)

    def test_gap_unload_vstar_fails(self):
        """Check that trying to gap unload unsupported record type fails"""
        dtStart = '2011-01-01'
        dtEnd = '2011-12-01'

        self.assertRaises(ApelDbException, self.unloader.unload_gap, 'VStarRecords', dtStart, dtEnd, ur=False)

    def test_gap_unload_summaries(self):
        """Check summary gap unload query"""
        dtStart = '2011-01-01'
        dtEnd = '2011-12-01'

        msgs, records = self.unloader.unload_gap('VSummaries', dtStart, dtEnd, ur=False)

        self._apeldb.get_records.assert_called_once()

        callArgs, callKWArgs = self._apeldb.get_records.call_args

        self.assertEqual('VSummaries', callArgs[1])

        expected = " WHERE EarliestEndTime > '2011-01-01 00:00:00' AND LatestEndTime <= '2011-12-02 00:00:00' AND InfrastructureType = 'grid'"

        self.assertEqual(expected, callKWArgs['query'].get_where())


class TestFunctions(unittest.TestCase):
    """Test cases for non-class functions."""

    def test_get_start_of_previous_month(self):
        """Check that get_start_of_previous_month gives the correct datetime."""
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
