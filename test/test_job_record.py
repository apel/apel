'''
Created on 2 Mar 2011

@author: will
'''

from apel.db.records import JobRecord, InvalidRecordException
import unittest
import datetime

class TestJobRecord(unittest.TestCase):
    '''Tests for the JobRecord class.'''

    def test_check_factor(self):
        '''
        Tests _check_factor method.
        '''
        
        record = JobRecord()
        self.assertRaises(InvalidRecordException, record._check_factor, 'unknown', 1)
        # currently only si2k and hepspec are supported
        # add values here if you need to add
        factors = ['si2k', 'hepspec']
        for factor in factors:
            try:
                record._check_factor(factor, 1)
            except:
                self.fail('Unsupported service level type: %s' % factor)
    
    
    def test_check_start_end_times(self):
        '''
        Tests _check_start_end_times method.
        '''
        record = JobRecord()
        record.set_field('StartTime', 10)
        record.set_field('EndTime', 5)
        
        # error: StartTime > EndTime
        self.assertRaises(InvalidRecordException, record._check_start_end_times)
        
        # EndTime is in future
        record.set_field('EndTime', datetime.datetime.now() + datetime.timedelta(days=4))
        self.assertRaises(InvalidRecordException, record._check_start_end_times)
    
    
    def test_check_fields(self):
        
        record = JobRecord()
        # empty record
        self.assertRaises(InvalidRecordException, record._check_fields)
        
        # minimal record must be accepted
        record.set_field('Site', 'some_site')
        record.set_field('SubmitHost', 'submithost.pl')
        record.set_field('LocalJobId', 'localjob')
        record.set_field('WallDuration', 3600)
        record.set_field('CpuDuration', 3600)
        record.set_field('StartTime', 1234)
        record.set_field('EndTime', 14234)
        
        try:
            record._check_fields()
        except:
            self.fail('Minimal record was not accepted!')

    def test_get_ur(self):
        """Check that get_ur outputs correct XML."""
        jr = JobRecord()
        jr.load_from_msg('''
Site: UK-UTOPIA
LocalJobId: some-id
WallDuration: 6704
CpuDuration: 19872
StartTime: 1504779367
EndTime: 1504786071''')

        xml = (
            '<urf:UsageRecord><urf:RecordIdentity urf:createTime="xxxx-xx-xxTxx'
            ':xx:xx" urf:recordId="None some-id 2017-09-07 12:07:51"/><urf:JobI'
            'dentity><urf:LocalJobId>some-id</urf:LocalJobId></urf:JobIdentity>'
            '<urf:UserIdentity><urf:GlobalUserName urf:type="opensslCompat">Non'
            'e</urf:GlobalUserName><urf:Group>None</urf:Group><urf:GroupAttribu'
            'te urf:type="FQAN">None</urf:GroupAttribute><urf:GroupAttribute ur'
            'f:type="vo-group">None</urf:GroupAttribute><urf:GroupAttribute urf'
            ':type="vo-role">None</urf:GroupAttribute><urf:LocalUserId>None</ur'
            'f:LocalUserId></urf:UserIdentity><urf:Status>completed</urf:Status'
            '><urf:Infrastructure urf:type="None"/><urf:WallDuration>PT6704S</u'
            'rf:WallDuration><urf:CpuDuration urf:usageType="all">PT19872S</urf'
            ':CpuDuration><urf:ServiceLevel urf:type="custom">1</urf:ServiceLev'
            'el><urf:EndTime>2017-09-07T12:07:51Z</urf:EndTime><urf:StartTime>2'
            '017-09-07T10:16:07Z</urf:StartTime><urf:MachineName>None</urf:Mach'
            'ineName><urf:SubmitHost>None</urf:SubmitHost><urf:Queue>None</urf:'
            'Queue><urf:Site>UK-UTOPIA</urf:Site></urf:UsageRecord>'
        )
        xml_out = jr.get_ur()

        # We have to avoid comparing the createTime as that changes.
        self.assertEqual(xml_out[:53], xml[:53])
        self.assertEqual(xml_out[72:], xml[72:])

if __name__ == '__main__':
    unittest.main()
