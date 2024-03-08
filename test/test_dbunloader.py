"""Test cases for private funtion in dbunloader."""

import configparser
import logging
import unittest

import bin.dbunloader as dbu


logging.basicConfig()
logger = logging.getLogger('test_dbunloader')


class TestBoundedRecordsPerMessage(unittest.TestCase):

    def setUp(self):
        self.cp = configparser.ConfigParser()
        self.cp.add_section('unloader')

    def test_too_small(self):
        """Check that too small a value gets increased to min."""
        self._helper('0', 1)

    def test_too_large(self):
        """Check that too large a value gets reduced to max."""
        self._helper('7500', 5000)

    def test_just_right(self):
        """Check that value within bounds gets kept."""
        self._helper('150', 150)

    def test_non_number(self):
        """Check that a non-number results in the default value."""
        self._helper('Not a number', 1000)

    def test_no_option(self):
        """check that not having the config option results in the default value."""
        recs_per_msg = dbu._bounded_records_per_message(self.cp, logger)
        self.assertEqual(recs_per_msg, 1000, "No config did not result in a default"
                         " of 1000, but gave %s." % recs_per_msg)

    def _helper(self, conf, target):
        """Helper method to set the config and check the result."""
        self.cp.set('unloader', 'records_per_message', conf)
        recs_per_msg = dbu._bounded_records_per_message(self.cp, logger)
        self.assertEqual(
            recs_per_msg, target, "Config value of '%s' did not result in bounded "
            "result of %s as expected, but gave %s." % (conf, target, recs_per_msg)
        )


if __name__ == "__main__":
    unittest.main()
