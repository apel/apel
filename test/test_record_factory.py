'''
Created on 4 Jul 2011

@author: Will Rogers

Tests for the RecordFactory.
'''
import unittest

from apel.db.loader.record_factory import RecordFactory, RecordFactoryException
from apel.db.records import (CloudRecord, CloudSummaryRecord, JobRecord,
                             NormalisedSummaryRecord, StorageRecord,
                             SummaryRecord, SyncRecord, JobRecord04,
                             SummaryRecord04, NormalisedSummaryRecord04)


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
        self.assertIsInstance(record_list[0], JobRecord)

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
        self.assertIsInstance(record_list[0], StorageRecord)

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
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertIsInstance(record, JobRecord)

    def test_create_srs(self):
        """Check that creating summary records returns SummaryRecords."""
        records = self._rf.create_records(self._sr_text)
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertIsInstance(record, SummaryRecord)

    def test_create_normalised_summary(self):
        """Check that creating a normalised summary returns the right record."""
        records = self._rf.create_records(self._nsr_text)
        self.assertIsInstance(records[0], NormalisedSummaryRecord)

    def test_create_jrs_04(self):
        """Check that creating v0.4 job records returns JobRecords04."""
        records = self._rf.create_records(self._jr_04_text)
        self.assertTrue(len(records), 2)
        for record in records:
            self.assertTrue(isinstance(record, JobRecord04))

    def test_create_srs_04(self):
        """Check that creating v0.4 summary records returns SummaryRecords."""
        records = self._rf.create_records(self._sr_04_text)
        self.assertTrue(len(records), 2)
        for record in records:
            self.assertTrue(isinstance(record, SummaryRecord04))

    def test_create_normalised_summary_04(self):
        """Check that creating v0.4 normalised summaries returns the right record."""
        records = self._rf.create_records(self._nsr_04_text)
        self.assertTrue(isinstance(records[0], NormalisedSummaryRecord04))


    def test_create_sync(self):
        """Check that creating a sync record returns a SyncRecord."""
        records = self._rf.create_records(self._sync_text)
        self.assertIsInstance(records[0], SyncRecord)

    def test_create_cloud(self):
        """Check that creating a cloud record returns a CloudRecord."""
        records = self._rf.create_records(self._cr_text)
        self.assertIsInstance(records[0], CloudRecord)

    def test_create_cloud_summary(self):
        """Check that creating a cloud summary returns a CloudSummaryRecord."""
        records = self._rf.create_records(self._csr_text)
        self.assertIsInstance(records[0], CloudSummaryRecord)

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

        self._jr_04_text = '''\
APEL-individual-job-message: v0.4
Site: SOME-SITE
SubmitHost: host.ac.uk/cluster
LocalJobId: 9aef372d-e26f-42ce-7acb-5e1c479dc47f
LocalUserId: bob
GlobalUserName:/DC=ac/DC=uni/DC=/DC=vac
FQAN: /host.org/Role=NULL/Capability=NULL
WallDuration: 47248
CpuDuration: 46871
Processors: 1
InfrastructureDescription: APEL-CREAM-HTCONDOR
InfrastructureType: grid
StartTime: 1531869580
EndTime: 1623693622
ServiceLevel: {hepspec: 11.4, HEPscore23: 15.3}
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
ServiceLevel: {hepspec: 11.3, HEPscore23: 10.3}
%%'''

        self._sr_04_text = '''\
APEL-summary-job-message: v0.4
Site: SOME-SITE
SubmitHost: host.ac.uk/cluster
Month: 7
Year: 2018
GlobalUserName:/DC=ac/DC=uni/DC=/DC=vac
WallDuration: 47248
CpuDuration: 46871
Processors: 1
NumberOfJobs: 3
InfrastructureType: grid
EarliestEndTime: 1531869580
LatestEndTime: 1531879580
ServiceLevel: {hepspec: 11.4, HEPscore23: 15.3}
%%
'''

        self._nsr_04_text = '''APEL-normalised-summary-message: v0.4
Site: SOME-SITE
SubmitHost: host.ac.uk/cluster
Month: 7
Year: 2018
GlobalUserName:/DC=ac/DC=uni/DC=/DC=vac
WallDuration: 47248
CpuDuration: 46871
NormalisedWallDuration: {hepspec: 519728, HEPscore23: 708720}
NormalisedCpuDuration: {hepspec: 515581, HEPscore23: 703065}
Processors: 1
NumberOfJobs: 3
Infrastructure: grid
EarliestEndTime: 1531869580
LatestEndTime: 1531879580
%%
Site: LBL_HPCS
SubmitHost: hepscore-hosts
VO: alice
EarliestEndTime: 1675209600
LatestEndTime: 1677628799
Month: 02
Year: 2023
Infrastructure: Gratia-OSG
GlobalUserName: generic alice user
Processors: 1
NodeCount: 1
WallDuration: 3653301632
CpuDuration: 2374660406
NormalisedWallDuration: {HEPscore23: 61192802343}
NormalisedCpuDuration: {HEPscore23: 39775561794}
NumberOfJobs: 160475
%%
Site: LBL_HPCS
SubmitHost: hepspec-hosts
VO: alice
EarliestEndTime: 1675209600
LatestEndTime: 1677628799
Month: 02
Year: 2023
Infrastructure: Gratia-OSG
GlobalUserName: generic alice user
Processors: 1
NodeCount: 1
WallDuration: 1565700700
CpuDuration: 1017711602
NormalisedWallDuration: {hepspec: 26225486718}
NormalisedCpuDuration: {hepspec: 17046669340}
NumberOfJobs: 68775
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


if __name__ == '__main__':
    unittest.main()
