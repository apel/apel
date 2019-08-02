
'''
Created on 2 Mar 2011

@author: will
'''
from apel.db.records import SyncRecord
import unittest

class TestSummaryRecord(unittest.TestCase):
    '''
    Tests the SyncRecord class.
    '''

    def setUp(self):
        '''Run before each test.'''
        self._records = self._get_msg_text()
        self._tuples = self._get_tuples()


    def tearDown(self):
        '''Run after each test.'''
        pass

############################################################################
# Test methods below
############################################################################

    def test_load_from_tuple(self):
        # Not yet implemented
        pass


    def test_load_from_msg(self):
        '''This currently checks that an exception is not thrown.'''
        for record in self._records:
            sr = SyncRecord()
            sr.load_from_msg(record)


    def test_get_apel_db_insert(self):

        for rec_txt, rec_tuple in zip(self._records, self._tuples):

            sr = SyncRecord()
            sr.load_from_msg(rec_txt)

            test_dn = "This is a test DN."

            values = sr.get_db_tuple(test_dn)

            for item1, item2 in zip(values, rec_tuple):
                if not item1 == item2:
                    print "item 1 is: " + str(item1)
                    print "item 2 is: " + str(item2)
                    self.fail('Values changed when creating a sync record.')



    def test_get_msg(self):
        '''This currently checks that an exception is not thrown.'''
        for record in self._records:
            sr = SyncRecord()
            sr.load_from_msg(record)

            # not a proper test yet
            sr.get_msg()


############################################################################
# Private helper method below
############################################################################

    def _get_msg_text(self):
        '''Some sample sync messages, whose values should correspond
        with the tuples in _get_tuples().'''

        records = []
        msg_text = """Site: RAL-LCG2
            Month: 3
            SubmitHost: sub.rl.ac.uk
            Year: 2010
            NumberOfJobs: 100"""

        msg_text2 = """Site: RAL-LCG2
            Month: 4
            SubmitHost: sub.rl.ac.uk
            Year: 2010
            NumberOfJobs: 103"""

        msg_text3 = """Site: CERN-PROD
            Month: 5
            SubmitHost: sub.cern.ac.uk
            Year: 2010
            NumberOfJobs: 1030"""

        records.append(msg_text)
        records.append(msg_text2)
        records.append(msg_text3)
        return records

    def _get_tuples(self):
        '''Some sample sync message tuples, whose values should correspond
        with the tuples in _get_msg_text.'''

        tuples = []

        tuple1 = ('RAL-LCG2', 'sub.rl.ac.uk', 100, 3, 2010)
        tuple2 = ('RAL-LCG2', 'sub.rl.ac.uk', 103, 4, 2010)
        tuple3 = ('CERN-PROD', 'sub.cern.ac.uk', 1030, 5, 2010)

        tuples.append(tuple1)
        tuples.append(tuple2)
        tuples.append(tuple3)
        return tuples

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()



