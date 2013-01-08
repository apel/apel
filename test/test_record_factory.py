'''
Created on 4 Jul 2011

@author: Will Rogers

Tests for the RecordFactory.
'''
import unittest
from apel.db.loader.record_factory import RecordFactory, RecordFactoryException, \
        get_main_ns
from apel.db.records import JobRecord
from apel.db.records import SummaryRecord

class Test(unittest.TestCase):


    def setUp(self):
        self._get_msg_text()
        self._rf = RecordFactory()


    def tearDown(self):
        pass


    def test_create_records(self):
        
        try:
            self._rf.create_records(self._rubbish_text)
            self.fail('No exception thrown by nonsense message.')
        except RecordFactoryException:
            # We expect the nonsense message to fail.
            pass

    def test_create_jrs(self):
        try:
            records = self._rf.create_records(self._jr_text)
            if (len(records) != 2):
                self.fail('Expected two records from record text.')
            for record in records:
                if not isinstance(record, JobRecord):
                    self.fail('Expected JobRecord object.')
        except Exception, e:
            self.fail('Exception thrown when creating records from object: ' + str(e))

            
    def test_create_srs(self):
        try:
            records = self._rf.create_records(self._sr_text)
            if (len(records) != 2):
                self.fail('Expected two records from record text.')
            for record in records:
                if not isinstance(record, SummaryRecord):
                    self.fail('Expected SummaryRecord object.')
        except Exception, e:
            self.fail('Exception thrown when creating records from object: ' + str(e))
            
    def test_xml_type(self):
        test_xml = '<?xml version="1.0" ?><ur:UsageRecord xmlns:ur="booboob"/>'
        ns = get_main_ns(test_xml)
        self.assertEqual("booboob", ns)
        
    
    
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
APEL-summary-job-message: v0.1
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