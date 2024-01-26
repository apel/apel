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

    #def test_parse_local_timestamp(self):
    #    '''
    #    The output of this function depends on the timezone of the testing
    #    computer.
    #    '''
    #    # Test not implemented
    #    pass

    def test_parse_line(self):

        keys = ('JobName', 'LocalUserID', 'LocalUserGroup', 'WallDuration',
                'CpuDuration', 'StartTime', 'StopTime', 'Queue', 'MemoryReal',
                'MemoryVirtual', 'NodeCount', 'Processors')

        # sacct output:
        # JobID|JobName|User|Group|Start|End|Elapsed|CPUTimeRAW|Partition|NCPUS|NNodes|NodeList|MaxRSS|MaxVMSize|State

        # Examples for lines that should raise ValueError
        value_fails = ('324543.batch|batch|||2013-10-28T04:27:26|2013-10-28T04:27:27|00:00:01|1||1|1|wn65|0|0|COMPLETED',  # Zero memory
                       '324554.batch|batch|||2013-10-28T04:28:30|2013-10-28T04:28:33|00:00:03|3||1|1|wn65|0|0|COMPLETED',  # Zero memory
                       '324554.batch|batch|||2013-10-28T04:28:30|2013-10-28T04:28:33|00:00:03|3||1|1|wn65|20H|54J|COMPLETED',  # Invalid unit prefix
                       '324554.batch|batch|||2013-10-28T04:28:33|2013-10-28T04:28:30|00:00:03|3||1|1|wn65|28K|80K|COMPLETED',  # StopTime < StartTime
                       '297720.batch|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|-16||1|1|wn37|3228K|23820K|COMPLETED',)  # -ve CpuDuration

        # Examples for correct lines
        lines = (
            ('1000|cream_176801680|dteam005|dteam|2013-03-27T17:13:24|2013-03-27T17:13:26|00:00:02|2|prod|1|1|cert-40|||COMPLETED'),
            ('278952.batch|batch|||2013-10-23T21:37:24|2013-10-25T00:01:37|1-02:24:13|95053||1|1|wn36|438.50M|1567524K|COMPLETED'),
            ('297720.batch|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn37|3228K|23820K|COMPLETED'),
            ('321439.batch|batch|||2013-10-27T17:09:35|2013-10-28T04:47:20|11:37:45|41865||1|1|wn16|770728K|1.40G|COMPLETED'),
            ('320816.batch|batch|||2013-10-27T14:56:03|2013-10-28T05:03:50|14:07:47|50867||1|1|wn33|1325232K|2.22G|COMPLETED'),
            # These lines use TotalCPU rather than CPUTimeRAW which uses a
            # different time format to the integer seconds of CPUTimeRAW.
            # d-h:m:s format:
            ('5940815|cream_877733810|user1|group1|2018-06-03T02:11:12|'
             '2018-06-05T03:36:08|2-01:24:56|8-15:40:36|partition|8|1|'
             'wn1|||COMPLETED'),
            # h:m:s format:
            ('5961074|cream_538395496|user2|group2|2018-06-05T13:30:17|'
             '2018-06-05T14:40:05|01:09:48|01:09:18|partition|1|1|wn2|'
             '||COMPLETED'),
            # m:s.s format:
            ('5979785|cream_636487219|user3|group3|2018-06-05T14:59:34|'
             '2018-06-05T15:02:59|00:03:25|01:05.753|partition|1|1|wn3|'
             '||COMPLETED'),
        )

        values = (
            ('1000', 'dteam005', 'dteam', 2, 2,
             datetime.utcfromtimestamp(mktime((2013, 3, 27, 17, 13, 24, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 3, 27, 17, 13, 26, 0, 1, -1))),
             'prod', None, None, 1, 1),
            ('278952.batch', None, None, 95053, 95053,
             datetime.utcfromtimestamp(mktime((2013, 10, 23, 21, 37, 24, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 10, 25, 00, 01, 37, 0, 1, -1))),
             None, int(438.50*1024), 1567524, 1, 1),
            ('297720.batch', None, None, 16, 16,
             datetime.utcfromtimestamp(mktime((2013, 10, 25, 12, 11, 20, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 10, 25, 12, 11, 36, 0, 1, -1))),
             None, 3228, 23820, 1, 1),
            ('321439.batch', None, None, 41865, 41865,
             datetime.utcfromtimestamp(mktime((2013, 10, 27, 17, 9, 35, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 10, 28, 4, 47, 20, 0, 1, -1))),
             None, 770728, int(1.40*1024*1024), 1, 1),
            ('320816.batch', None, None, 50867, 50867,
             datetime.utcfromtimestamp(mktime((2013, 10, 27, 14, 56, 3, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2013, 10, 28, 5, 3, 50, 0, 1, -1))),
             None, 1325232, int(2.22*1024*1024), 1, 1),
            ('5940815', 'user1', 'group1', ((2*24+1)*60+24)*60+56, ((8*24+15)*60+40)*60+36,
             datetime.utcfromtimestamp(mktime((2018, 6, 3, 2, 11, 12, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2018, 6, 5, 3, 36, 8, 0, 1, -1))),
             'partition', None, None, 1, 8),
            ('5961074', 'user2', 'group2', (1*60+9)*60+48, (1*60+9)*60+18,
             datetime.utcfromtimestamp(mktime((2018, 6, 5, 13, 30, 17, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2018, 6, 5, 14, 40, 5, 0, 1, -1))),
             'partition', None, None, 1, 1),
            ('5979785', 'user3', 'group3', 3*60+25, 1*60+6,
             datetime.utcfromtimestamp(mktime((2018, 6, 5, 14, 59, 34, 0, 1, -1))),
             datetime.utcfromtimestamp(mktime((2018, 6, 5, 15, 2, 59, 0, 1, -1))),
             'partition', None, None, 1, 1),
        )

        cases = {}
        for line, value in zip(lines, values):
            cases[line] = dict(list(zip(keys, value)))

        for line in list(cases.keys()):
            record = self.parser.parse(line)
            cont = record._record_content

            self.assertEqual(cont['Site'], 'testSite')
            self.assertEqual(cont['MachineName'], 'testHost')
            self.assertEqual(cont['Infrastructure'], 'APEL-CREAM-SLURM')

            # Queue is a special case as it gets deleted on parsing if empty.
            if 'Queue' not in cont:
                del cases[line]['Queue']

            for key in list(cases[line].keys()):
                self.assertTrue(key in cont, "Key '%s' not in record." % key)

            for key in list(cases[line].keys()):
                self.assertEqual(cont[key], cases[line][key], "%s != %s for key %s." % (cont[key], cases[line][key], key))

        for line in value_fails:
            self.assertRaises(ValueError, self.parser.parse, line)

    def test_job_status(self):
        """Check that the right statuses are accepted."""
        accepted = (  # These job statuses are all described as "terminated".
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|CANCELLED',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|COMPLETED',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|FAILED',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|NODE_FAIL',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|PREEMPTED',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|TIMEOUT',
        )

        rejected = (  # These jobs would be unstarted or still running.
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|BOOT_FAIL',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|CONFIGURING',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|COMPLETING',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|DEADLINE',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|PENDING',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|RUNNING',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|RESIZING',
            '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|16||1|1|wn|28K|20K|SUSPENDED',
        )
        for line in accepted:
            self.assertNotEqual(self.parser.parse(line), None,
                                "Line incorrectly rejected: %s" % line)

        for line in rejected:
            self.assertEqual(self.parser.parse(line), None,
                             "Line incorrectly accepted: %s" % line)


if __name__ == '__main__':
    unittest.main()
