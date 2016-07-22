import datetime
import os
import subprocess
import unittest

import apel.db.apeldb
import apel.db.records


if os.name == 'nt':
    os.environ['PATH'] += ';C:/Program Files/MySQL/MySQL Server 5.1/bin/'


class MysqlTest(unittest.TestCase):
    # These test cases require a local MySQL db server with no password on root
    def setUp(self):
        query = ('DROP DATABASE IF EXISTS apel_unittest;'
                 'CREATE DATABASE apel_unittest;')
        subprocess.call(['mysql', '-u', 'root', '-e', query])

        schema_path = os.path.abspath(os.path.join('..', 'schemas',
                                                   'server.sql'))
        schema_handle = open(schema_path)
        subprocess.call(['mysql', '-u', 'root', 'apel_unittest'], stdin=schema_handle)
        schema_handle.close()

        self.db = apel.db.apeldb.ApelDb('mysql', 'localhost', 3306, 'root', '',
                                        'apel_unittest')

    # This method seems to run really slowly on Travis CI
    #def tearDown(self):
    #    query = "DROP DATABASE apel_unittest;"
    #    subprocess.call(['mysql', '-u', 'root', '-e', query])

    def test_test_connection(self):
        """Basic check that test_connection works without error."""
        self.db.test_connection()

    def test_bad_connection(self):
        """Check that initialising ApelDb fails if a bad password is used."""
        self.assertRaises(apel.db.apeldb.ApelDbException, apel.db.apeldb.ApelDb,
                          'mysql', 'localhost', 3306, 'root', 'badpassword',
                          'apel_badtest')

    def test_lost_connection(self):
        """
        Check that a lost connection to the db raises an exception.

        Simulate the lost connection by changing the host.
        """
        self.db._db_host = 'badhost'
        self.assertRaises(apel.db.apeldb.ApelDbException,
                          self.db.test_connection)

    def test_bad_loads(self):
        """Check that empty loads return None and bad types raise exception."""
        self.assertTrue(self.db.load_records([], source='testDN') is None)
        self.assertRaises(apel.db.apeldb.ApelDbException,
                          self.db.load_records, [1234], source='testDN')

    def test_load_and_get(self):
        job = apel.db.records.job.JobRecord()
        job._record_content = {'Site': 'testSite', 'LocalJobId': 'testJob',
                               'SubmitHost': 'testHost',
                               'WallDuration': 10, 'CpuDuration': 10,
                               'StartTime': datetime.datetime.fromtimestamp(123456),
                               'EndTime': datetime.datetime.fromtimestamp(654321),
                               'ServiceLevelType': 'HEPSPEC',
                               'ServiceLevel': 3}
        items_in = job._record_content.items()
        record_list = [job]
        # load_records changes the 'job' job record as it calls _check_fields
        # which adds placeholders to empty fields
        self.db.load_records(record_list, source='testDN')

        records_out = self.db.get_records(apel.db.records.job.JobRecord)
        items_out = list(records_out)[0][0]._record_content.items()
        # Check that items_in is a subset of items_out
        # Can't use 'all()' rather than comparing the length as Python 2.4
        self.assertEqual([item in items_out for item in items_in].count(True), len(items_in))

    def test_mixed_load(self):
        """
        Check that loader fails gracefully if passed mixed types in record list.
        """
        job = apel.db.records.job.JobRecord()
        job._record_content = {'Site': 'testSite', 'LocalJobId': 'testJob',
                               'SubmitHost': 'testHost',
                               'WallDuration': 10, 'CpuDuration': 10,
                               'StartTime': datetime.datetime.fromtimestamp(123456),
                               'EndTime': datetime.datetime.fromtimestamp(654321),
                               'ServiceLevelType': 'HEPSPEC',
                               'ServiceLevel': 3}
        summary = apel.db.records.SummaryRecord()
        summary._record_content = {'Site': 'testSite', 'Month': 1,
                                   'Year': 2016, 'WallDuration': 2000,
                                   'CpuDuration': 1000, 'NumberOfJobs': 3}
        record_list = [job, summary]

        self.assertRaises(apel.db.apeldb.ApelDbException,
                          self.db.load_records, record_list, source='testDN')

    def test_last_update(self):
        """
        Check that the LastUpdated table can be set and queried.

        It should not be set initially, so should return None, then should
        return a time after being set.
        """
        self.assertTrue(self.db.get_last_updated() is None)
        self.assertTrue(self.db.set_updated())
        self.assertTrue(type(self.db.get_last_updated()) is datetime.datetime)


if __name__ == '__main__':
    unittest.main()
