from datetime import datetime
import unittest

from apel.parsers import SlurmParser
from apel.parsers.slurm import parse_local_timestamp


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

        line1 = ('1000|cream_176801680|dteam005|dteam|2013-03-27T17:13:24|2013-03-27T17:13:26|00:00:02|2|prod|1|1|cert-40|||COMPLETED')

        line1_values = {"JobName": "1000",
                        "LocalUserID": "dteam005",
                        "LocalUserGroup": "dteam",
                        "WallDuration": 2,
                        "CpuDuration": 2,
                        "StartTime": datetime(2013, 3, 27, 17, 13, 24),
                        "StopTime": datetime(2013, 3, 27, 17, 13, 26),
                        "MemoryReal": None,
                        "MemoryVirtual": None,
                        "NodeCount": 1,
                        "Processors": 1
                        }

        cases = {line1: line1_values}

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
