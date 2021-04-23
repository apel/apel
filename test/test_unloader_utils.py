import apel.common.unloader_utils as utils
from apel.common.unloader_utils import check_records_per_message as check
import unittest
import os, shutil, pathlib

try:
    import ConfigParser
except ImportError:
    # Renamed in Python 3
    import configparser as ConfigParser


class UnloadingUtilsTest(unittest.TestCase):
    '''
    Test case for check function from apel.common.unloader_utils
    '''

    def mkconfig(self, file, value, header='unloader', key='records_per_message'):
        cfgstr = f'[{header}]\n{key} = {value}'
        with open(file, 'w') as f:
            f.write(cfgstr)

    def setUp(self):
        """Create config files with range of failure modes"""

        self.tmpdir = pathlib.Path(f'/tmp/{__name__}')
        self.tmpdir.mkdir(exist_ok=False)

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

    def tearDown(self):
        """Remove config files"""

        [os.remove(self.tmpdir/f) for f in os.listdir(self.tmpdir)]
        os.rmdir(self.tmpdir)


    def test_read_config(self):
        """Check that ConfigParser can read the true config file"""

        self.client_config = '../conf/client.cfg'
        cp = ConfigParser.ConfigParser()
        cp.read(self.client_config)

        self.assertEqual(self.resp_default, check(cp)) # TODO assumes default matches cfg


    def assertCase(self, file, key, value, header, exp):
        """Create a config and check that returned value is valid"""

        path = self.tmpdir / file
        self.mkconfig(path, value, header=header, key=key)

        cp = ConfigParser.ConfigParser()
        cp.read(path)

        self.assertEqual(exp, check(cp))

    def test_check_records_per_message_valid(self):
        """Check helper function output for valid config"""

        file = 'valid'
        header = self.valid_header 
        key = self.valid_key 
        value = self.valid_value
        exp = self.valid_value

        self.assertCase(file, key, value, header, exp)

    def test_check_records_per_message_low_value(self):
        """Check helper function output for too low config value"""

        file = 'low_value'
        header = self.valid_header 
        key = self.valid_key 
        value = self.resp_lower - 1
        exp = self.resp_lower

        self.assertCase(file, key, value, header, exp)

    def test_check_records_per_message_high_value(self):
        """Check helper function output for too high config value"""

        file = 'high_value'
        header = self.valid_header 
        key = self.valid_key 
        value = self.resp_upper + 1
        exp = self.resp_upper

        self.assertCase(file, key, value, header, exp)

    def test_check_records_per_message_invalid_value(self):
        """Check helper function output for invalid config value"""

        file = 'invalid_value'
        header = self.valid_header 
        key = self.valid_key 
        value = self.invalid_value
        exp = self.resp_default

        self.assertCase(file, key, value, header, exp)

    def test_check_records_per_message_invalid_header(self):
        """Check helper function output for missing config header"""

        file = 'invalid_header'
        header = self.invalid_header 
        key = self.valid_key 
        value = self.valid_value
        exp = self.resp_default

        self.assertCase(file, key, value, header, exp)

    def test_check_records_per_message_invalid_key(self):
        """Check helper function output for invalid config key"""

        file = 'invalid_key'
        header = self.valid_header 
        key = self.invalid_key 
        value = self.valid_value
        exp = self.resp_default

        self.assertCase(file, key, value, header, exp)
        

if __name__ == '__main__':
    unittest.main()
