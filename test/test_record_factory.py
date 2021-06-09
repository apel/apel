'''
Created on 4 Jul 2011

@author: Will Rogers

Tests for the RecordFactory.
'''
from datetime import datetime
import unittest

from apel.db.loader.record_factory import RecordFactory, RecordFactoryException
from apel.db.records import (CloudRecord, CloudSummaryRecord, JobRecord,
                             NormalisedSummaryRecord, StorageRecord,
                             SummaryRecord, SyncRecord)


class TestRecordFactory(unittest.TestCase):
    """Unit tests for the record factory class."""

    def setUp(self):
        """Create message variables and record factory instance."""
        self._get_msg_text()
        self._rf = RecordFactory()

    def test_create_records(self):
        """Check that a nonsense message raises an exception."""
        self.assertRaises(RecordFactoryException,
                          self._rf.create_records, self._rubbish_text)

    def test_create_car(self):
        """Check that creating a CAR record returns a JobRecord."""
        record_list = self._rf.create_records(
            '<urf:UsageRecord xmlns:urf="http://eu-emi.eu/namespaces/2012/11/co'
            'mputerecord"></urf:UsageRecord>'
        )
        self.assertTrue(isinstance(record_list[0], JobRecord))

    def test_create_aur(self):
        """Check that trying to create an AUR record fails."""
        self.assertRaises(RecordFactoryException, self._rf.create_records, (
            '<aur:SummaryRecord xmlns:aur="http://eu-emi.eu/namespaces/2012/11'
            '/aggregatedcomputerecord"></aur:SummaryRecord>')
        )

    def test_create_star(self):
        """Check that creating a StAR record returns a StorageRecord."""
        record_list = self._rf.create_records(
            '<sr:StorageUsageRecord xmlns:sr="http://eu-emi.eu/namespaces/2011/'
            '02/storagerecord"><sr:RecordIdentity sr:createTime="2016-06-09T02:'
            '42:15Z" sr:recordId="c698"/></sr:StorageUsageRecord>'
        )
        self.assertTrue(isinstance(record_list[0], StorageRecord))

    def test_create_bad_xml(self):
        """Check that trying to create a record from non-record XML fails."""
        self.assertRaises(RecordFactoryException, self._rf.create_records,
                          '<nonrecordxml></nonrecordxml>')

    def test_create_bad_apel(self):
        """Check that an incorrect header raises an exception."""
        self.assertRaises(RecordFactoryException, self._rf.create_records,
                          'APEL-individual-bad-message: v0.1')

    def test_create_jrs(self):
        """Check that creating job records returns JobRecords."""
        records = self._rf.create_records(self._jr_text)
        self.assertTrue(len(records), 2)
        for record in records:
            self.assertTrue(isinstance(record, JobRecord))

    def test_create_srs(self):
        """Check that creating summary records returns SummaryRecords."""
        records = self._rf.create_records(self._sr_text)
        self.assertTrue(len(records), 2)
        for record in records:
            self.assertTrue(isinstance(record, SummaryRecord))

    def test_create_normalised_summary(self):
        """Check that creating a normalised summary returns the right record."""
        records = self._rf.create_records(self._nsr_text)
        self.assertTrue(isinstance(records[0], NormalisedSummaryRecord))

    def test_create_sync(self):
        """Check that creating a sync record returns a SyncRecord."""
        records = self._rf.create_records(self._sync_text)
        self.assertTrue(isinstance(records[0], SyncRecord))

    def test_create_cloud(self):
        """Check that creating a cloud record returns a CloudRecord."""
        records = self._rf.create_records(self._cr_text)
        self.assertTrue(isinstance(records[0], CloudRecord))

    def test_create_cloud_summary(self):
        """Check that creating a cloud summary returns a CloudSummaryRecord."""
        records = self._rf.create_records(self._csr_text)
        self.assertTrue(isinstance(records[0], CloudSummaryRecord))

    def test_create_records_json_malformed(self):
        """Test the expected error is raised on handling malformed JSON."""
        malformed_json = '{"Key": "Value}'

        with self.assertRaisesRegexp(RecordFactoryException,
                                     "^Malformed JSON:"):
            self._rf.create_records(malformed_json)

    def test_create_records_json_unknown_type(self):
        """Test the expected error is raised on messages without a type."""
        unknown_type_json = '{"Key": "Value"}'

        with self.assertRaisesRegexp(RecordFactoryException, 
                                     "^Type of JSON message not provided."):
            self._rf.create_records(unknown_type_json)

    def test_create_records_json_unsupported_type(self):
        """Test the expected error is raised on unsupported message types."""
        unsupported_json = self._generate_json_message(
            "Spammy Type", "ignored version", "[{'Key': 'Value'}]"
        )

        with self.assertRaisesRegexp(RecordFactoryException,
                                     "^Unsupported JSON message type:"):
            self._rf.create_records(unsupported_json)

    # TODO invalid GPU entries 

    def test_create_records_gpu(self):
        """Test creation of GPURecords from a JSON message."""
        # Create some records for a test message.
        record0 = {
            "MeasurementTime": 1536070129,
            "MeasurementMonth": 9,
            "MeasurementYear": 2018,
            "AssociatedRecordType": "cloud",
            "AssociatedRecord": "TEST-FakeVMUUID",
            "GlobalUserName": "GlobalUser1",
            "FQAN": "FQAN1",
            "SiteName": "TEST-SITE",
            "Count": 0.5,
            "Cores": 64,
            "ActiveDuration": 600,
            "AvailableDuration": 6000,
            "BenchmarkType": "BenchmarkType1",
            "Benchmark": 1005,
            "Type": "GPU",
            "Model": "Model1",
        }

        record1 = {
            "MeasurementTime": 1536070129,
            "MeasurementMonth": 9,
            "MeasurementYear": 2018,
            "AssociatedRecordType": "cloud",
            "AssociatedRecord": "TEST-FakeVMUUID2",
            "GlobalUserName": "GlobalUser2",
            "FQAN": "FQAN2",
            "SiteName": "TEST-SITE",
            "Count": 1,
            "Cores": 8,
            "ActiveDuration": 30,
            "AvailableDuration": 600,
            "BenchmarkType": "BenchmarkType2",
            "Benchmark": 995,
            "Type": "GPU",
            "Model": "Model2",
        }

        # Create a list of records and build a GPU accounting message.
        usage_records = [record0, record1]
        gpu_accounting_message_v00 = self._generate_json_message(
            "APEL GPU message", "0.1", usage_records
        )

        # Create the record objects, using the RecordFactory.
        record_object_list = self._rf.create_records(gpu_accounting_message_v00)

        # Compare the generated record objects with the dictionary provided
        # as input.
        self._compare_record_to_dictionary(record_object_list[0], record0)
        self._compare_record_to_dictionary(record_object_list[1], record1)

    def _generate_json_message(self, type, version, usage_records):
        """Helper function to generate JSON messages."""
        message = JSON_MSG_BOILERPLATE % (type, version, usage_records)
        # The above will put single quotes into the created message, but
        # JSON is strictly double quotes. So replace single quotes.
        message = message.replace("'", '"')
        return message

    def _compare_record_to_dictionary(self, record_object, dictionary):
        """Helper function to compare a record object and a dictionary."""
        # Loop through the record content of the record object.
        for key, value in record_object._record_content.items():
            # Compare the value in the record object to the corresponding key
            # in the dictionary. Handle datetime fields differently because in
            # the message they are expressed as seconds-since-epoch, but in the
            # object they are datetime objects.
            if key in record_object._datetime_fields:
                self.assertEqual(
                    value,
                    datetime.utcfromtimestamp(dictionary[key])
                )
            # This test fails when the local clock uses daylight savings time.
            else:
                self.assertEqual(value, dictionary[key])


    def _get_msg_text(self):
    # Below, I've just got some test data hard-coded.
        self._rubbish_text = '''In 1869, the stock ticker was invented.
        It was an electro-mechanical machine consisting of a typewriter,
        a long pair of wires and a ticker tape printer,
        and its purpose was to distribute stock prices over long
        distances in realtime. This concept gradually evolved into
        the faster, ASCII-based teletype.'''

        self._jr_text = '''\
APEL-individual-job-message: v0.1
Site: RAL-LCG2
SubmitHost: ce01.ncg.ingrid.pt:2119/jobmanager-lcgsge-atlasgrid
LocalJobId: 31564872
LocalUserId: atlasprd019
GlobalUserName: /C=whatever/D=someDN
FQAN: /voname/Role=NULL/Capability=NULL
WallDuration: 234256
CpuDuration: 2345
Processors: 2
NodeCount: 2
StartTime: 1234567890
EndTime: 1234567899
MemoryReal: 1000
MemoryVirtual: 2000
ServiceLevelType: Si2k
ServiceLevel: 1000
%%
Site: RAL-LCG2
SubmitHost: ce01.ncg.ingrid.pt:2119/jobmanager-lcgsge-atlasgrid
LocalJobId: 31564873
LocalUserId: atlasprd019
GlobalUserName: /C=whatever/D=someDN
FQAN: /voname/Role=NULL/Capability=NULL
WallDuration: 234256
CpuDuration: 2345
Processors: 2
NodeCount: 2
StartTime: 1234567890
EndTime: 1234567899
MemoryReal: 1000
MemoryVirtual: 2000
ServiceLevelType: Si2k
ServiceLevel: 1000
%%'''

        self._sr_text = '''\
APEL-summary-job-message: v0.2
Site: RAL-LCG2
Month: 3
Year: 2010
GlobalUserName: /C=whatever/D=someDN
VO: atlas
VOGroup: /atlas
VORole: Role=production
WallDuration: 234256
CpuDuration: 2345
NumberOfJobs: 100
%%
Site: RAL-LCG2
Month: 4
Year: 2010
GlobalUserName: /C=whatever/D=someDN
VO: atlas
VOGroup: /atlas
VORole: Role=production
WallDuration: 234256
CpuDuration: 2345
NumberOfJobs: 100
%%
'''

        self._nsr_text = '''APEL-summary-job-message: v0.3
Site: RAL-LCG2
Month: 3
Year: 2010
WallDuration: 234256
CpuDuration: 244435
NormalisedWallDuration: 234256
NormalisedCpuDuration: 244435
NumberOfJobs: 100
%%
'''

        self._sync_text = '''APEL-sync-message: v0.1
Site: RAL-LCG2
Month: 3
SubmitHost: sub.rl.ac.uk
Year: 2010
NumberOfJobs: 100
%%
'''

        self._cr_text = '''APEL-cloud-message: v0.4
VMUUID: 2013-11-14 19:15:21+00:00 CESNET vm-1
SiteName: CESNET
%%
'''

        self._csr_text = '''APEL-cloud-summary-message: v0.4
SiteName: CESNET
Month: 10
Year: 2011
NumberOfVMs: 1
%%
'''


JSON_MSG_BOILERPLATE = """{
    "Type": "%s",
    "Version": "%s",
    "UsageRecords": %s
}"""


if __name__ == '__main__':
    unittest.main()
