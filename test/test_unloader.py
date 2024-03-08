import datetime
import shutil
import tempfile
import unittest

from mock import Mock, patch
from apel.db.apeldb import ApelDbException
from apel.db.records.storage import StorageRecord
from apel.db.unloader import DbUnloader, get_start_of_previous_month
from apel.db.records.storage_summary import StorageSummaryRecord


class TestDbUnloader(unittest.TestCase):
    """
    Test case for DbUnloader.
    """

    def setUp(self):
        # Create temporary directory for dirq to write to
        self.dir_path = tempfile.mkdtemp()
        self.unloader = DbUnloader(None, self.dir_path)

    def tearDown(self):
        shutil.rmtree(self.dir_path)

    def test_write_star_to_apel(self):
        """Check that unloading StAR records to APEL format is prevented."""
        self.assertRaises(ApelDbException, self.unloader._write_messages,
                          StorageRecord, 'table', 'query', ur=False)

    def test_write_yaml_with_storage_records(self):
        # Test for a valid record type
        records = [StorageSummaryRecord(), StorageSummaryRecord()]
        expected_yaml = '---'

        # Mock the necessary dependencies
        self.unloader._msgq = Mock()

        # Patch the necessary function
        mock_dump_all = Mock(return_value=expected_yaml)
        with patch('yaml.dump_all', mock_dump_all):
            self.unloader._write_yaml(records)

            # Assert that yaml.dump_all() method will make a call with the expected parameters.
            mock_dump_all.assert_called_once_with(
                [{'type': 'StorageRecord'}, records[0].get_ur(self.unloader._withhold_dns),
                records[1].get_ur(self.unloader._withhold_dns)],
                default_flow_style=False, explicit_start=True, explicit_end=True
            )

            # Assert that add() method will make a call with expected YAML
            self.unloader._msgq.add.assert_called_once_with(expected_yaml)

        # Test for a Invalid record type
        invalid_records = ['SomeRecord()']
        expected_error_msg = "Can only send records in YAML for StorageRecords"

        with self.assertRaises(ApelDbException) as exceptionContext:
            self.unloader._write_yaml(invalid_records)

        self.assertEqual(
            str(exceptionContext.exception),
            expected_error_msg
        )

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
