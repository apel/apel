import unittest
import tempfile

try:
    import ConfigParser
except ImportError:
    # Renamed in Python 3
    import configparser as ConfigParser

import apel.common.unloader_utils as utils
from apel.common.unloader_utils import check_records_per_message as check


class UnloaderUtilsTest(unittest.TestCase):
    '''
    Test case for check function from apel.common.unloader_utils
    '''

    def setUp(self):
        """Create config files with range of failure modes"""

        # Responses in fail cases
        self.resp_lower = utils.RECORDS_PER_MESSAGE_MIN
        self.resp_upper = utils.RECORDS_PER_MESSAGE_MAX
        self.resp_default = utils.RECORDS_PER_MESSAGE_DEFAULT

        self.valid_header = 'unloader'
        self.valid_key = 'records_per_message'
        self.valid_value = 3456

        self.invalid_header = 'notunloader'
        self.invalid_key = 'notrecords_per_message'
        self.invalid_value = None

    def test_read_config(self):
        """Check that ConfigParser can read the true config file"""

        self.client_config = '../conf/client.cfg'
        cp = ConfigParser.ConfigParser()
        cp.read(self.client_config)

        self.assertEqual(self.resp_default, check(cp))

    def mkconfig(self, value, header='unloader', key='records_per_message'):
        try:  # Python 3
            cfgstr = bytes('[%s]\n%s = %s' % (header, key, value), 'utf-8')
        except TypeError:  # Python 2.7
            cfgstr = bytes('[%s]\n%s = %s' % (header, key, value))
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(cfgstr)
        # Avoid closing temporary file, which deletes it immediately.
        tmp.seek(0)
        return tmp

    def _assertCase(self, header, key, value, exp):
        """Create a config and check that returned value is valid"""

        tmpf = self.mkconfig(value, header=header, key=key)

        cp = ConfigParser.ConfigParser()
        cp.read(tmpf.name)
        tmpf.close()

        self.assertEqual(exp, check(cp))

    def test_check_records_per_message_valid(self):
        """Check helper function output for valid config"""

        header = self.valid_header
        key = self.valid_key
        value = self.valid_value
        exp = self.valid_value

        self._assertCase(header, key, value, exp)

    def test_check_records_per_message_low_value(self):
        """Check helper function output for too low config value"""

        header = self.valid_header
        key = self.valid_key
        value = self.resp_lower - 1
        exp = self.resp_lower

        self._assertCase(header, key, value, exp)

    def test_check_records_per_message_high_value(self):
        """Check helper function output for too high config value"""

        header = self.valid_header
        key = self.valid_key
        value = self.resp_upper + 1
        exp = self.resp_upper

        self._assertCase(header, key, value, exp)

    def test_check_records_per_message_invalid_value(self):
        """Check helper function output for invalid config value"""

        header = self.valid_header
        key = self.valid_key
        value = self.invalid_value
        exp = self.resp_default

        self._assertCase(header, key, value, exp)

    def test_check_records_per_message_invalid_header(self):
        """Check helper function output for missing config header"""

        header = self.invalid_header
        key = self.valid_key
        value = self.valid_value
        exp = self.resp_default

        self._assertCase(header, key, value, exp)

    def test_check_records_per_message_invalid_key(self):
        """Check helper function output for invalid config key"""

        header = self.valid_header
        key = self.invalid_key
        value = self.valid_value
        exp = self.resp_default

        self._assertCase(header, key, value, exp)


if __name__ == '__main__':
    unittest.main()
