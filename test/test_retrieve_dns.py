import os
import tempfile
import unittest
import mock
import xml.dom.minidom

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


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        # Mock out logging
        mock.patch('bin.retrieve_dns.set_up_logging', autospec=True).start()
        # Mock options.log_config as this isn't set if runprocess isn't run
        bin.retrieve_dns.options = mock.Mock(log_config="fake_file")

    def test_get_config(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                            'conf', 'auth.cfg'))
        conf = bin.retrieve_dns.get_config(path).__dict__

        settings = {'gocdb_url': ('https://goc.egi.eu/gocdbpi/public/?method=ge'
                                  't_service_endpoint&service_type=gLite-APEL'),
                    'extra_dns': os.path.normpath('/etc/apel/extra-dns'),
                    'banned_dns': os.path.normpath('/etc/apel/banned-dns'),
                    'dn_file': os.path.normpath('/etc/apel/dns'),
                    'proxy': 'http://wwwcache.rl.ac.uk:8080',
                    'expire_hours': 2}

        for key in settings:
            self.assertEqual(conf[key], settings[key],
                             "%s != %s for option %s" % (conf[key],
                                                         settings[key], key))

    def test_get_empty_config(self):
        # Make a temp file for blank [auth] config
        handle, path = tempfile.mkstemp()
        os.write(handle, "[auth]\n[logging]\nlogfile=_\nlevel=_\nconsole=False")
        os.close(handle)

        conf = bin.retrieve_dns.get_config(path).__dict__

        settings = {'gocdb_url': None, 'extra_dns': None, 'banned_dns': None,
                    'dn_file': None, 'proxy': None, 'expire_hours': 0}

        for key in settings:
            self.assertEqual(conf[key], settings[key],
                             "%s != %s for option %s" % (conf[key],
                                                         settings[key], key))
        os.remove(path)

    def tearDown(self):
        # Stop all patchers so that they're reset for the next test
        mock.patch.stopall()


class RunprocessTestCase(unittest.TestCase):

    def setUp(self):
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
        os.write(self.files['extra']['handle'], "#comment\n/extra/dn\n/banned/dn")
        os.write(self.files['ban']['handle'], "/banned/dn")

        for item in self.files.values():
            os.close(item['handle'])

        # Set up config using temp files
        c = bin.retrieve_dns.Configuration()
        c.dn_file = self.files['dn']['path']
        c.extra_dns = self.files['extra']['path']
        c.banned_dns = self.files['ban']['path']
        c.expire_hours = 1
        c.gocdb_url = "not.a.host"
        mock_config.return_value = c

    def test_next_link_from_dom(self):
        """Test a next link is correctly retrieved from a xml string."""
        xml_test_string = """<results>
        <meta>
        <link rel="self" href="not a next link"/>
        <link rel="prev" href="not this one either"/>
        <link rel="start" href="nor this one"/>
        <link rel="next" href="next link"/>
        </meta>
        <SERVICE_ENDPOINT><HOSTDN>/basic/dn</HOSTDN></SERVICE_ENDPOINT>
        <SERVICE_ENDPOINT><HOSTDN>/banned/dn</HOSTDN></SERVICE_ENDPOINT>
        <SERVICE_ENDPOINT><HOSTDN>invalid</HOSTDN></SERVICE_ENDPOINT>
        </results>"""

        # Parse the test XML into a Document Object Model
        dom = xml.dom.minidom.parseString(xml_test_string)

        result = bin.retrieve_dns.next_link_from_dom(dom)
        self.assertEqual(result, "next link")

    def test_basics(self):
        self.mock_xml.return_value = """<results>
        <SERVICE_ENDPOINT><HOSTDN>/basic/dn</HOSTDN></SERVICE_ENDPOINT>
        <SERVICE_ENDPOINT><HOSTDN>/banned/dn</HOSTDN></SERVICE_ENDPOINT>
        <SERVICE_ENDPOINT><HOSTDN>invalid</HOSTDN></SERVICE_ENDPOINT>
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
