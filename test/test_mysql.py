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

    def test_load_and_get_job(self):
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

    def test_load_and_get_cloud(self):
        '''
        Test a CloudV0.2/0.4 message can be loaded into the database.

        It currently can't test for pre/post database load equality
        as the two are currently not the same for V0.2.
        i.e Benchmark 'None', which gets set to 0.0
        '''
        schema_path = os.path.abspath(os.path.join('..', 'schemas',
                                                   'cloud.sql'))
        schema_handle = open(schema_path)
        subprocess.call(['mysql', '-u', 'root', 'apel_unittest'],
                        stdin=schema_handle)
        schema_handle.close()

        # loading messages like this does indirectly test
        # the load_from_msg() code, but it also ensures
        # we this test checks we can load a message,
        # and not just what we think the message
        # looks like as a python dictionary
        cloud2 = apel.db.records.cloud.CloudRecord()
        cloud2.load_from_msg(CLOUD2)

        cloud4 = apel.db.records.cloud.CloudRecord()
        cloud4.load_from_msg(CLOUD4)

        # Test a BenchmarkType/Benchmark - less Cloud v0.4 Record
        cloud4_nb = apel.db.records.cloud.CloudRecord()
        cloud4_nb.load_from_msg(CLOUD4_NULL_BENCHMARKS)

        # Test a Cloud V0.4 Record with mising fields
        cloud4_mf = apel.db.records.cloud.CloudRecord()
        cloud4_mf.load_from_msg(CLOUD4_MISSING_FIELDS)

        items_in = cloud2._record_content.items()
        items_in += cloud4._record_content.items()
        items_in += cloud4_nb._record_content.items()
        items_in += cloud4_mf._record_content.items()

        record_list = [cloud2, cloud4, cloud4_nb, cloud4_mf]

        # load_records changes the 'cloud' cloud record as it calls _check_fields
        # which adds placeholders to empty fields
        try:
            self.db.load_records(record_list, source='testDN')
        except apel.db.apeldb.ApelDbException as err:
            self.fail(err.message)

        # this code block would check for equality between the message passed
        # to the database and the message retrieved from the database.
        # but at the moment they are fundementally unequal, for example
        # a cloud 0.2 message has Benchmark 'None', which gets saved to 0.0
        # in the database

        # records_out = self.db.get_records(apel.db.records.cloud.CloudRecord)
        # # record_out_list is a list of lists, i.e. [[record0.2],[[record0.4]]
        # record_out_list = list(records_out)
        # items_out = []
        # for record in record_out_list[0]:
        #     items_out += record._record_content.items()
        # Check that items_in is a subset of items_out
        # Can't use 'all()' rather than comparing the length as Python 2.4
        # self.assertEqual([item in items_out for item in items_in].count(True),
        #                   len(items_in))

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

    def test_mixed_storage_records(self):
        """
        Check that the loader will accept mixed types in one case.

        The loader should work when passed mixed record types if they are
        Storage and GroupAttribute records.
        """
        schema_path = os.path.abspath(os.path.join('..', 'schemas',
                                                   'storage.sql'))
        schema_handle = open(schema_path)
        subprocess.call(['mysql', '-u', 'root', 'apel_unittest'],
                        stdin=schema_handle)
        schema_handle.close()

        storage_rec = apel.db.records.StorageRecord()
        storage_rec._record_content = {
            'RecordId': 'c698',
            'CreateTime': datetime.datetime.fromtimestamp(654321),
            'StorageSystem': 'test-sys.ac.uk',
            'StartTime': datetime.datetime.fromtimestamp(123456),
            'EndTime': datetime.datetime.fromtimestamp(654321),
            'ResourceCapacityUsed': '10'
        }

        grpattr_rec = apel.db.records.GroupAttributeRecord()
        grpattr_rec._record_content = {
            'StarRecordID': 'c698',
            'AttributeType': 'authority',
            'AttributeValue': '/O=Grid/OU=example.org/CN=Joe Bloggs'
        }

        record_list = [storage_rec, grpattr_rec]

        # Try loading both with and without a source set. Both record types
        # should ignore that field.
        self.db.load_records(record_list, source='testDN')
        self.db.load_records(record_list)

    def test_last_update(self):
        """
        Check that the LastUpdated table can be set and queried.

        It should not be set initially, so should return None, then should
        return a time after being set.
        """
        self.assertTrue(self.db.get_last_updated() is None)
        self.assertTrue(self.db.set_updated())
        self.assertTrue(type(self.db.get_last_updated()) is datetime.datetime)

CLOUD2 = '''VMUUID: 12345 Site1 vm-1
SiteName: Site1
MachineName: '1'
LocalUserId: 1
LocalGroupId: 1
GlobalUserName: NULL
FQAN: NULL
Status: completed
StartTime: 1318842264
EndTime: 1318849976
SuspendDuration: NULL
WallDuration: NULL
CpuDuration: NULL
CpuCount: 1
NetworkType: NULL
NetworkInbound: 0
NetworkOutbound: 0
Memory: 512
Disk: NULL
StorageRecordId: NULL
ImageId: 1
CloudType: Cloud Technology 1
'''

CLOUD4 = '''VMUUID: 12345 Site2 Accounting Test
SiteName: Site2
CloudComputeService: Cloud Technology 2 Instance 1
MachineName: Accounting Test
LocalUserId: 1
LocalGroupId: 1
GlobalUserName: /DC=XX/DC=XX/O=XX/CN=XX
FQAN: /ops/Role=NULL/Capability=NULL
Status: started
StartTime: 1343362725
EndTime: NULL
SuspendDuration: NULL
WallDuration: 1582876
CpuDuration: 437
CpuCount: 1
NetworkType: NULL
NetworkInbound: NULL
NetworkOutbound: NULL
PublicIPCount: 1
Memory: 512
Disk: 0
BenchmarkType: Si2k
Benchmark: 200
StorageRecordId: NULL
ImageId: 1
CloudType: Cloud Technology 2
'''

# A Cloud V0.4 Record, but with NULL Benchmark / BenchmarkType fields
CLOUD4_NULL_BENCHMARKS = '''VMUUID: 12346 Site2 Accounting Test
SiteName: Site2
CloudComputeService: Cloud Technology 2 Instance 1
MachineName: Accounting Test 2
LocalUserId: 1
LocalGroupId: 1
GlobalUserName: /DC=XX/DC=XX/O=XX/CN=XX
FQAN: /ops/Role=NULL/Capability=NULL
Status: started
StartTime: 1343362825
EndTime: NULL
SuspendDuration: NULL
WallDuration: 1583876
CpuDuration: 438
CpuCount: 1
NetworkType: NULL
NetworkInbound: NULL
NetworkOutbound: NULL
PublicIPCount: 1
Memory: 512
Disk: 0
BenchmarkType: NULL
Benchmark: NULL
StorageRecordId: NULL
ImageId: 1
CloudType: Cloud Technology 2
'''

# A Cloud V0.4 Record, but missing a lot of fields.
# We need to check we can load this record as we receive
# messages with records like this and currently
# load them.
CLOUD4_MISSING_FIELDS = '''
BenchmarkType: HEPSPEC06
Status: completed
SiteName: Test Site
MachineName: Test Machine
ImageId: Test Image ID
LocalUserId: Test Local User ID
FQAN: NULL
LocalGroupId: Test Local Group ID
VMUUID: Test VM ID
CloudType: caso/0.3.4 (OpenStack)
GlobalUserName: Test User
CloudComputeService: Test Service
'''

if __name__ == '__main__':
    unittest.main()
