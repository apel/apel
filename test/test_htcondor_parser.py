import datetime
import unittest

from apel.parsers.htcondor import HTCondorParser


class HTCondorParserTest(unittest.TestCase):
    """
    Test case for HTCondor parser
    """

    def setUp(self):
        self.parser = HTCondorParser('testSite', 'testHost', True)

    def test_parse_line(self):

        keys = ('JobName', 'LocalUserID', 'LocalUserGroup', 'WallDuration',
                'CpuDuration', 'StartTime', 'StopTime', 'MemoryReal',
                'MemoryVirtual', 'NodeCount', 'Processors')

        # condor_history output (line split):
        #   ClusterId|Owner|RemoteWallClockTime|RemoteUserCpu|RemoteSysCpu|
        #   JobStartDate|EnteredCurrentStatus|ResidentSetSize_RAW|ImageSize_RAW|
        #   RequestCpus

        # Examples for correct lines
        lines = (
            ('1234567|opssgm|19|18|8|1412688273|1412708199|712944|2075028|1'),
        )

        values = (
            ('1234567', 'opssgm', None, 19, 26,
             datetime.datetime(2014, 10, 7, 13, 24, 33),
             datetime.datetime(2014, 10, 7, 18, 56, 39),
             712944, 2075028, 0, 1),
        )

        cases = {}
        for line, value in zip(lines, values):
            cases[line] = dict(zip(keys, value))

        for line in cases.keys():
            record = self.parser.parse(line)
            cont = record._record_content

            self.assertEqual(cont['Site'], 'testSite')
            self.assertEqual(cont['MachineName'], 'testHost')
            self.assertEqual(cont['Infrastructure'], 'APEL-CREAM-HTCONDOR')

            for key in cases[line].keys():
                self.assertTrue(key in cont, "Key '%s' not in record." % key)

            for key in cases[line].keys():
                self.assertEqual(cont[key], cases[line][key],
                                 "%s != %s for key %s." %
                                 (cont[key], cases[line][key], key))

if __name__ == '__main__':
    unittest.main()
