import logging
import os
import tempfile
import unittest

import mock

import bin.retrieve_dns


logging.basicConfig(level=logging.WARN)


class RetrieveDnsTestCase(unittest.TestCase):

    def setUp(self):
        # Mock out logging
        mock.patch('bin.retrieve_dns.set_up_logging', autospec=True).start()

        # Mock out config
        mock_config = mock.patch('bin.retrieve_dns.get_config',
                                 autospec=True).start()

        # Mock out retrieving xml
        self.mock_xml = mock.patch('bin.retrieve_dns.get_xml',
                                   autospec=True).start()

        # Set up temp files
        self.files = {}
        for item in ('dn', 'extra', 'ban'):
            self.files[item] = dict(zip(('handle', 'path'), tempfile.mkstemp()))

        os.write(self.files['dn']['handle'], "/dn1\n/dn2\n")
        os.write(self.files['extra']['handle'], "/extra_dn\n/banned_dn")
        os.write(self.files['ban']['handle'], "/banned_dn")

        for item in self.files.values():
            os.close(item['handle'])

        # Set up config using temp files
        c = bin.retrieve_dns.Configuration()
        c.dn_file = self.files['dn']['path']
        c.extra_dns = self.files['extra']['path']
        c.banned_dns = self.files['ban']['path']
        c.expire_hours = 1
        mock_config.return_value = c

    def test_basics(self):
        self.mock_xml.return_value = """<results>
        <SERVICE_ENDPOINT><HOSTDN>/basic_dn</HOSTDN></SERVICE_ENDPOINT>
        <SERVICE_ENDPOINT><HOSTDN>/banned_dn</HOSTDN></SERVICE_ENDPOINT>
        </results>"""
        bin.retrieve_dns.runprocess("fake_config_file", "fake_log_config_file")
        dns = open(self.files['dn']['path'])
        try:
            self.assertEqual(dns.read(), "/basic_dn\n/extra_dn\n")
        finally:
            dns.close()

    def test_gocdb_fail(self):
        """
        If there isn't a good response from GOCDB we want to keep the old
        list of DNs for a configurable amount of time until a good response is
        obtained.
        """
        self.mock_xml.return_value = ""
        self.assertRaises(SystemExit, bin.retrieve_dns.runprocess, "fake_config_file", "fake_log_config_file")
        dns = open(self.files['dn']['path'])
        try:
            self.assertEqual(dns.read(), "/dn1\n/dn2\n")
        finally:
            dns.close()

    def tearDown(self):
        # Delete temp files
        for item in self.files.values():
            os.remove(item['path'])
        # Stop all patchers so that they're reset for the next test
        mock.patch.stopall()


if __name__ == '__main__':
    unittest.main()
