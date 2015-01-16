import os
import tempfile
import unittest

import mock

import bin.retrieve_dns


class SimpleTestCase(unittest.TestCase):
    """Test fixture for simple test cases."""

    def test_verify_valid_dns(self):
        valid_dns = ("/C=UK/O=eScience/OU=CLRC/L=RAL/CN=apel-test.esc.rl.ac.uk",
                     "/C=UK/O=eScience/OU=CLRC/L=RAL/CN=sctapel.esc.rl.ac.uk",
                     "/C=UK/O=eScience/OU=CLRC/L=RAL/CN=uas.esc.rl.ac.uk",
                     "/smallest/acceptable")

        for dn in valid_dns:
            self.assertTrue(bin.retrieve_dns.verify_dn(dn),
                            "Valid DN rejected: %s" % dn)

    def test_verify_invalid_dns(self):
        invalid_dns = ("# Some comment",
                       "/C=UK, /O=eScience, /OU=Lanchester, /L=Physics",
                       "/too-few-elements")

        for dn in invalid_dns:
            self.assertFalse(bin.retrieve_dns.verify_dn(dn),
                             "Invalid DN accepted: %s" % dn)


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

        os.write(self.files['dn']['handle'], "/dn/1\n/dn/2\n")
        os.write(self.files['extra']['handle'], "/extra/dn\n/banned/dn")
        os.write(self.files['ban']['handle'], "/banned/dn")

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
        <SERVICE_ENDPOINT><HOSTDN>/basic/dn</HOSTDN></SERVICE_ENDPOINT>
        <SERVICE_ENDPOINT><HOSTDN>/banned/dn</HOSTDN></SERVICE_ENDPOINT>
        </results>"""
        bin.retrieve_dns.runprocess("fake_config_file", "fake_log_config_file")
        dns = open(self.files['dn']['path'])
        try:
            self.assertEqual(dns.read(), "/basic/dn\n/extra/dn\n")
        finally:
            dns.close()

    def test_gocdb_fail(self):
        """
        If there isn't a good response from GOCDB we want to keep the old
        list of DNs for a configurable amount of time until a good response is
        obtained.
        """
        self.mock_xml.return_value = ""
        self.assertRaises(SystemExit, bin.retrieve_dns.runprocess,
                          "fake_config_file", "fake_log_config_file")
        dns = open(self.files['dn']['path'])
        try:
            self.assertEqual(dns.read(), "/dn/1\n/dn/2\n")
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
