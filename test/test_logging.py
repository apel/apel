"""Test cases for logging function in apel.common.__init__."""

from io import StringIO
import logging
import os
import sys
import tempfile
import unittest

from apel.common import set_up_logging


class LoggingTest(unittest.TestCase):
    """Test cases for set_up_logging function."""
    def setUp(self):
        # Capture stdout in a StringIO object for inspection.
        self._stdout = sys.stdout
        sys.stdout = StringIO()
        # Create a temporary file to write log to
        handle, self.path = tempfile.mkstemp()
        os.close(handle)

    def tearDown(self):
        # Restore stdout to normal.
        sys.stdout.close()
        sys.stdout = self._stdout
        # Delete temporary file
        os.remove(self.path)

    def test_stdout_logging(self):
        """
        Check that logging to stdout and file works, ignoring timestamp.

        These are tested together as otherwise the logger setup conflicts.
        """
        set_up_logging(self.path, 'INFO', True)
        log = logging.getLogger('test_logging')
        log.info('out')

        # Retrieve output from StringIO object.
        output = sys.stdout.getvalue()
        # Shutdown logging to release log file for later deletion.
        logging.shutdown()

        # Only check bit after timestamp as that doesn't change.
        self.assertEqual(output[23:], " - test_logging - INFO - out\n")
        f = open(self.path)
        self.assertEqual(f.readline()[23:], " - test_logging - INFO - out\n")
        f.close()

    def test_boring_logging(self):
        """Check that logging without handlers at least runs without errors."""
        set_up_logging(None, 'INFO', False)


if __name__ == '__main__':
    unittest.main()
