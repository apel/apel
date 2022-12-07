"""
Created on 4 Jul 2011

@author: Will Rogers

Tests for the RecordFactory.
"""
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
StartTime: 1000000
%%
'''

        self._csr_text = '''APEL-cloud-summary-message: v0.4
SiteName: CESNET
Month: 10
Year: 2011
NumberOfVMs: 1
%%
'''


if __name__ == '__main__':
    unittest.main()
