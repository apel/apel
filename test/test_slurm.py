from datetime import datetime
from time import mktime
import unittest

from apel.parsers import SlurmParser
#from apel.parsers.slurm import parse_local_timestamp


class ParserSlurmTest(unittest.TestCase):
    '''
    Test case for SLURM parser
    '''

    def setUp(self):
        self.parser = SlurmParser('testSite', 'testHost', True)

    def test_parse_local_timestamp(self):
        '''
        The output of this function depends on the timezone of the testing
        computer.
        '''
        # Not yet implemented
        pass

    def test_parse_line(self):

        keys = ('JobName', 'LocalUserID', 'LocalUserGroup', 'WallDuration',
                'CpuDuration', 'StartTime', 'StopTime', 'MemoryReal',
                'MemoryVirtual', 'NodeCount', 'Processors')

        lines = (
            ('1000|cream_176801680|dteam005|dteam|2013-03-27T17:13:24|2013-03-27T17:13:26|00:00:02|2|prod|1|1|cert-40|||COMPLETED'),
            ('278952.batch|batch|||2013-10-23T21:37:24|2013-10-25T00:01:37|1-02:24:13|95053||1|1|wn36|438.50M|1567524K|COMPLETED'),
            ('297720.batch|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn37|3228K|23820K|COMPLETED'),)

        values = (
            ('1000', 'dteam005', 'dteam', 2, 2,
             datetime.utcfromtimestamp(mktime((2013, 3, 27, 17, 13, 24, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 3, 27, 17, 13, 26, 0, 1, -1))),
             None, None, 1, 1),
            ('278952.batch', None, None, 95053, 95053,
             datetime.utcfromtimestamp(mktime((2013, 10, 23, 21, 37, 24, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 10, 25, 00, 01, 37, 0, 1, -1))),
             449024, 1567524, 1, 1),
            ('297720.batch', None, None, 16, 16,
             datetime.utcfromtimestamp(mktime((2013, 10, 25, 12, 11, 20, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 10, 25, 12, 11, 36, 0, 1, -1))),
             3228, 23820, 1, 1))

        cases = {}
        for line, value in zip(lines, values):
            cases[line] = dict(zip(keys, value))

        for line in cases.keys():
            record = self.parser.parse(line)
            cont = record._record_content

            self.assertTrue("Site" in cont)
            self.assertTrue("JobName" in cont)
            self.assertTrue("LocalUserID" in cont)
            self.assertTrue("LocalUserGroup" in cont)
            self.assertTrue("WallDuration" in cont)
            self.assertTrue("CpuDuration" in cont)
            self.assertTrue("StartTime" in cont)
            self.assertTrue("StopTime" in cont)
            self.assertTrue("MemoryReal" in cont)
            self.assertTrue("MemoryReal" in cont)

            for key in cases[line].keys():
                self.assertEqual(cont[key], cases[line][key], "%s != %s for key %s" % (cont[key], cases[line][key], key))

if __name__ == '__main__':
    unittest.main()
