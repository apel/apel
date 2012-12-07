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
                self.fatal('Unsupported service level type: %s' % factor)
    
    
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
        
        # minimal record mu be accepted
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
            self.fatal('Minimal record was not accepted!')
        