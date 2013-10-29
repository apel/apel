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

        line1 = ('1000|cream_176801680|dteam005|dteam|2013-03-27T17:13:24|2013-03-27T17:13:26|00:00:02|2|prod|1|1|cert-40|||COMPLETED')
        line2 = ('278952.batch|batch|||2013-10-23T21:37:24|2013-10-25T00:01:37|1-02:24:13|95053||1|1|wn36|438.50M|1567524K|COMPLETED')
        line3 = ('297720.batch|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn37|3228K|23820K|COMPLETED')

        line1_values = {"JobName": "1000",
                        "LocalUserID": "dteam005",
                        "LocalUserGroup": "dteam",
                        "WallDuration": 2,
                        "CpuDuration": 2,
                        "StartTime": datetime.utcfromtimestamp(
                            mktime((2013, 3, 27, 17, 13, 24, 0, 1, -1))),
                        "StopTime": datetime.utcfromtimestamp(
                            mktime((2013, 3, 27, 17, 13, 26, 0, 1, -1))),
                        "MemoryReal": None,
                        "MemoryVirtual": None,
                        "NodeCount": 1,
                        "Processors": 1
                        }

        line2_values = {"JobName": "278952.batch",
                        "LocalUserID": None,
                        "LocalUserGroup": None,
                        "WallDuration": 95053,
                        "CpuDuration": 95053,
                        "StartTime": datetime.utcfromtimestamp(
                            mktime((2013, 10, 23, 21, 37, 24, 0, 1, -1))),
                        "StopTime": datetime.utcfromtimestamp(
                            mktime((2013, 10, 25, 00, 01, 37, 0, 1, -1))),
                        "MemoryReal": 449024,
                        "MemoryVirtual": 1567524,
                        "NodeCount": 1,
                        "Processors": 1
                        }

        line3_values = {"JobName": "297720.batch",
                        "LocalUserID": None,
                        "LocalUserGroup": None,
                        "WallDuration": 16,
                        "CpuDuration": 16,
                        "StartTime": datetime.utcfromtimestamp(
                            mktime((2013, 10, 25, 12, 11, 20, 0, 1, -1))),
                        "StopTime": datetime.utcfromtimestamp(
                            mktime((2013, 10, 25, 12, 11, 36, 0, 1, -1))),
                        "MemoryReal": 3228,
                        "MemoryVirtual": 23820,
                        "NodeCount": 1,
                        "Processors": 1
                        }

        cases = {line1: line1_values,
                 line2: line2_values,
                 line3: line3_values}

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
