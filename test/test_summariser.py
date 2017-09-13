"""This file contains the BinSummariserTest class."""

import os
import shutil
import tempfile
import unittest

from subprocess import Popen, PIPE


class BinSummariserTest(unittest.TestCase):
    """A class to test the bin/summariser.py file."""

    def setUp(self):
        """Create tempory config files and populate the db config."""
        # Create a directory for temporary files
        self._tmp_dir = tempfile.mkdtemp(prefix='summariser')

        # Create an empty database config file
        self.db_cfg, self.db_cfg_path = tempfile.mkstemp(prefix='db',
                                                         dir=self._tmp_dir)

        # Create an empty summariser config file
        self.sum_cfg, self.sum_cfg_path = tempfile.mkstemp(prefix='sum',
                                                           dir=self._tmp_dir)

        # Populate the database config (with junk)
        os.write(self.db_cfg, DB_CONF)
        os.close(self.db_cfg)

    def test_lock_file(self):
        """Test a existing Pidfile prevents a summariser from starting."""
        # Create the Pidfile.
        # We don't have to worry about cleaning it up as tearDown deletes
        # everything in self._tmp_dir
        _pid_file, pid_path = tempfile.mkstemp(prefix='pid',
                                               dir=self._tmp_dir)

        # Create a temporary log file for the summariser
        _sum_log, sum_log_path = tempfile.mkstemp(prefix='sum',
                                                  dir=self._tmp_dir)

        # Create a temporary summariser config that refers to the Pidfile above
        sum_conf = ('[summariser]\n'
                    'pidfile = %s\n'
                    '\n'
                    '[logging]\n'
                    'logfile = %s\n'
                    'level = INFO\n'
                    'console = true\n' % (pid_path, sum_log_path))

        # Write temporary config to the temporary file
        os.write(self.sum_cfg, sum_conf)
        os.close(self.sum_cfg)

        # Run the summariser with the temporary config files
        summariser = Popen(['python', '../bin/summariser.py',
                            '-d', self.db_cfg_path,
                            '-c', self.sum_cfg_path],
                           stdout=PIPE)

        output, error = summariser.communicate()

        if error is not None:
            # Then it errored in some unforseen way
            self.fail(error)

        if 'pidfile exists' not in output:
            if 'Created Pidfile' in output:
                # Then we have errored in an expected way
                # and a summariser was started
                self.fail('A summariser started despite existing pidfile.')
            else:
                # Something else has happened.
                self.fail('An unexpected summariser error has occured.\n'
                          'See output below:\n'
                          '%s' % output)

    def tearDown(self):
        """Remove test directory and all contents."""
        try:
            shutil.rmtree(self._tmp_dir)
        except OSError, error:
            print 'Error removing temporary directory %s' % self._tmp_dir
            print error

DB_CONF = """[db]
# type of database
backend = Tutorial D
# host with database
hostname = Darwen
# port to connect to
port = 3306
# database name
name = hugh
# database user
username = hugh
# password for database
password = duck
# how many records should be put/fetched to/from database
# in single query
records = 1000
# option for summariser so that SummariseVMs is called
type = birds
"""

if __name__ == '__main__':
    unittest.main()
