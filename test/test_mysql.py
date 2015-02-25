import datetime
import os
import subprocess
import unittest

import apel.db.apeldb
import apel.db.records.job


class MysqlTest(unittest.TestCase):
    # These test cases require a local MySQL db server with a apel_unittest db
    def setUp(self):
        schema_path = os.path.abspath(os.path.join('..', 'schemas',
                                                   'server.sql'))
        schema_handle = open(schema_path)
        subprocess.Popen(['mysql', 'apel_unittest'], stdin=schema_handle).wait()
        schema_handle.close()

        self.db = apel.db.apeldb.ApelDb('mysql', 'localhost', 3306, 'root', '',
                                        'apel_unittest')

    def test_connection(self):
        self.db.test_connection()

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


if __name__ == '__main__':
    unittest.main()
