from future.builtins import zip

import datetime
import unittest

from apel.parsers.htcondor import HTCondorParser


class HTCondorParserTest(unittest.TestCase):
    """
    Test case for HTCondor parser
    """

    def setUp(self):
        self.parser = HTCondorParser('testSite', 'testHost', True)

    def test_parse_line_no_cputmult(self):
        """Check parsing of original 10 item long log line."""

        keys = ('JobName', 'LocalUserID', 'LocalUserGroup', 'WallDuration',
                'CpuDuration', 'StartTime', 'StopTime', 'MemoryReal',
                'MemoryVirtual', 'NodeCount', 'Processors')

        # condor_history output (line split):
        #   GlobalJobId|Owner|RemoteWallClockTime|RemoteUserCpu|RemoteSysCpu|
        #   JobStartDate|EnteredCurrentStatus|ResidentSetSize_RAW|ImageSize_RAW|
        #   RequestCpus

        # Examples for correct lines
        lines = (
            '1234567|opssgm|19|18|8|1412688273|1412708199|712944|2075028|1',
            'arcce.rl.ac.uk#2376.0#1589|tatls011|287|107|11|1435671643|1435671930|26636|26832|1|1',
            'arcce.rl.ac.uk#2486.0#1888|t2k016|4|0|0|1435671919|1435671922|0|11|1|1',
            'arcce.rl.ac.uk#2478.0#1874|snoplus014|2|0|0|1435671918|1435671920|0|11|1|1',
        )

        values = (
            ('1234567', 'opssgm', None, 19, 26,
             datetime.datetime(2014, 10, 7, 13, 24, 33),
             datetime.datetime(2014, 10, 7, 18, 56, 39),
             712944, 2075028, 0, 1),
            ('arcce.rl.ac.uk#2376.0#1589', 'tatls011', None, 287, 118,
             datetime.datetime(2015, 6, 30, 13, 40, 43),
             datetime.datetime(2015, 6, 30, 13, 45, 30),
             26636, 26832, 0, 1),
            ('arcce.rl.ac.uk#2486.0#1888', 't2k016', None, 4, 0,
             datetime.datetime(2015, 6, 30, 13, 45, 19),
             datetime.datetime(2015, 6, 30, 13, 45, 22),
             0, 11, 0, 1),
            ('arcce.rl.ac.uk#2478.0#1874', 'snoplus014', None, 2, 0,
             datetime.datetime(2015, 6, 30, 13, 45, 18),
             datetime.datetime(2015, 6, 30, 13, 45, 20),
             0, 11, 0, 1),
        )

        cases = {}
        for line, value in zip(lines, values):
            cases[line] = dict(zip(keys, value))

        for line in list(cases.keys()):
            record = self.parser.parse(line)
            cont = record._record_content

            self.assertEqual(cont['Site'], 'testSite')
            self.assertEqual(cont['MachineName'], 'testHost')
            self.assertEqual(cont['Infrastructure'], 'APEL-CREAM-HTCONDOR')

            for key in list(cases[line].keys()):
                self.assertTrue(key in cont, "Key '%s' not in record." % key)

            for key in list(cases[line].keys()):
                self.assertEqual(cont[key], cases[line][key],
                                 "%s != %s for key %s." %
                                 (cont[key], cases[line][key], key))

    def test_parse_line_with_cputmult(self):
        """Check parsing of 11 item line (scaling factor of 1.5 appended)."""

        keys = ('JobName', 'LocalUserID', 'LocalUserGroup', 'WallDuration',
                'CpuDuration', 'StartTime', 'StopTime', 'MemoryReal',
                'MemoryVirtual', 'NodeCount', 'Processors')

        # condor_history output (line split):
        #   GlobalJobId|Owner|RemoteWallClockTime|RemoteUserCpu|RemoteSysCpu|
        #   JobStartDate|EnteredCurrentStatus|ResidentSetSize_RAW|ImageSize_RAW|
        #   RequestCpus

        # Examples for correct lines
        lines = (
            '1234567|opsgm|19|18|8|1412688273|1412708199|712944|2075028|1|1.5',
            'ce.ac.uk#7|l011|287|107|12|1435671643|1435671930|6636|6832|1|1.5',
            'ce.ac.uk#2486.0|t2k016|4|0|0|1435671919|1435671922|0|11|1|1.5',
            'ce.ac.uk#278.0|snoplus014|2|0|0|1435671918|1435671920|0|11|1|1.5',
        )

        values = (
            ('1234567', 'opsgm', None, 28, 39,
             datetime.datetime(2014, 10, 7, 13, 24, 33),
             datetime.datetime(2014, 10, 7, 18, 56, 39),
             712944, 2075028, 0, 1),
            ('ce.ac.uk#7', 'l011', None, 430, 178,
             datetime.datetime(2015, 6, 30, 13, 40, 43),
             datetime.datetime(2015, 6, 30, 13, 45, 30),
             6636, 6832, 0, 1),
            ('ce.ac.uk#2486.0', 't2k016', None, 6, 0,
             datetime.datetime(2015, 6, 30, 13, 45, 19),
             datetime.datetime(2015, 6, 30, 13, 45, 22),
             0, 11, 0, 1),
            ('ce.ac.uk#278.0', 'snoplus014', None, 3, 0,
             datetime.datetime(2015, 6, 30, 13, 45, 18),
             datetime.datetime(2015, 6, 30, 13, 45, 20),
             0, 11, 0, 1),
        )

        cases = {}
        for line, value in zip(lines, values):
            cases[line] = dict(zip(keys, value))

        for line in list(cases.keys()):
            record = self.parser.parse(line)
            cont = record._record_content

            self.assertEqual(cont['Site'], 'testSite')
            self.assertEqual(cont['MachineName'], 'testHost')
            self.assertEqual(cont['Infrastructure'], 'APEL-CREAM-HTCONDOR')

            for key in list(cases[line].keys()):
                self.assertTrue(key in cont, "Key '%s' not in record." % key)

            for key in list(cases[line].keys()):
                self.assertEqual(cont[key], cases[line][key],
                                 "%s != %s for key %s." %
                                 (cont[key], cases[line][key], key))


if __name__ == '__main__':
    unittest.main()
