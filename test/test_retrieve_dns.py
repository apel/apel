import logging
import os
import tempfile
import unittest

import mock

import bin.retrieve_dns


logging.basicConfig(level=logging.INFO)


class RetrieveDnsTestCase(unittest.TestCase):

    def setUp(self):
        # Mock out logging
        mock.patch('bin.retrieve_dns.set_up_logging', autospec=True).start()

        # Mock out config
        mock_config = mock.patch('bin.retrieve_dns.get_config', autospec=True).start()

        # Mock out retrieving xml
        self.mock_xml = mock.patch('bin.retrieve_dns.get_xml', autospec=True).start()

        # Set up temp files
        self.files = {}
        for item in ('dn', 'extra', 'ban'):
            self.files[item] = dict(zip(('handle', 'path'), tempfile.mkstemp()))
            os.write(self.files[item]['handle'], '/wobble')
        for item in self.files.values():
            os.close(item['handle'])

        # Set up config using temp files
        c = bin.retrieve_dns.Configuration()
        c.dn_file = self.files['dn']['path']
        c.extra_dns = self.files['extra']['path']
        c.banned_dns = self.files['ban']['path']
        mock_config.return_value = c

    def test_basics(self):
        self.mock_xml.return_value = "<HOSTDN>/wibble</HOSTDN>"
        bin.retrieve_dns.runprocess("fakefile", "fakefile")
        dns = open(self.files['dn']['path'])
        self.assertEqual(dns.read(), '/wibble\n')
        dns.close()

    def tearDown(self):
        # Delete temp files
        for item in self.files.values():
            os.remove(item['path'])

        mock.patch.stopall()


if __name__ == '__main__':
    unittest.main()
