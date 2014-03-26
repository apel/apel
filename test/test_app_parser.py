"""Test cases for the application parser."""

from datetime import datetime
from time import mktime
import unittest

from apel.parsers.application import ApplicationParser


def convert_time(*time):
    if len(time) != 6:
        raise ValueError('Wrong number of arguments: 6 required, %i provided' % len(time))
    time += (0, 1, -1)
    return datetime.utcfromtimestamp(mktime(time))


class TestApplicationParser(unittest.TestCase):
    """Test case for Application parser."""

    def setUp(self):
        self.parser = ApplicationParser('unusedSite', 'unusedHost')  # These don't seem to be used by the parser

    def test_parser(self):
        keys = ('BinaryPath', 'ExitInfo', 'User', 'StartTime', 'EndTime')

        good_lines = ('{"binary path": "/bin/ls", "exit_info": {"exited_normally": "true", "signal": "0"}, "user": {"uid": "501", "gid": "20"}, "start_time": "Tue Mar 25 17:43:58 2014", "end_time": "Tue Mar 25 17:43:58 2014"}',
                      '{"binary path": "/bin/sleep", "exit_info": {"exited_normally": "true", "signal": "0"}, "user": {"uid": "501", "gid": "20"}, "start_time": "Tue Mar 25 17:44:12 2014", "end_time": "Tue Mar 25 17:44:12 2014"}',
                      '{"binary path": "/bin/sleep", "exit_info": {"exited_normally": "false", "signal": "2", "signal_str": "Interrupt: 2"}, "user": {"uid": "501", "gid": "20"}, "start_time": "Tue Mar 25 17:44:38 2014", "end_time": "Tue Mar 25 17:44:38 2014"}',
                      '{"binary path": "/usr/bin/uptime", "exit_info": {"exited_normally": "true", "signal": "0"}, "user": {"uid": "501", "gid": "20"}, "start_time": "Tue Nov  5 15:05:01 2013", "end_time": "Tue Nov  5 15:05:01 2013"}',)

        good_values = (
            ('/bin/ls', '"exited_normally": "true", "signal": "0"', '"uid": "501", "gid": "20"', convert_time(2014, 3, 25, 17, 43, 58), convert_time(2014, 3, 25, 17, 43, 58)),
            ('/bin/sleep', '"exited_normally": "true", "signal": "0"', '"uid": "501", "gid": "20"', convert_time(2014, 3, 25, 17, 44, 12), convert_time(2014, 3, 25, 17, 44, 12)),
            ('/bin/sleep', '"exited_normally": "false", "signal": "2", "signal_str": "Interrupt: 2"', '"uid": "501", "gid": "20"', convert_time(2014, 3, 25, 17, 44, 38), convert_time(2014, 3, 25, 17, 44, 38)),
            ('/usr/bin/uptime', '"exited_normally": "true", "signal": "0"', '"uid": "501", "gid": "20"', convert_time(2013, 11, 5, 15, 05, 01), convert_time(2013, 11, 5, 15, 05, 01)),
            )

        cases = {}

        for line, value in zip(good_lines, good_values):
            cases[line] = dict(zip(keys, value))

        for line in cases.keys():
            record = self.parser.parse(line)
            content = record._record_content

            for key in cases[line].keys():
                self.assertTrue(key in content, "Key '%s' not in record." % key)

            for key in cases[line].keys():
                self.assertEqual(content[key], cases[line][key], "%s != %s for key %s." % (content[key], cases[line][key], key))


if __name__ == '__main__':
    unittest.main()
