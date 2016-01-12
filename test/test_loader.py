import dirq
import mock
import os
import shutil
import tempfile
import unittest

import apel.db.loader


schema = {"body": "string", "signer": "string",
          "empaid": "string?", "error": "string?"}


class LoaderTest(unittest.TestCase):

    def setUp(self):
        # Create temporary directory for message queues and pidfiles
        self.dir_path = tempfile.mkdtemp()

        # Mock out the database as we're not testing that here
        # Note that as it's a class it needs instantiating
        self.mock_db = mock.patch('apel.db.ApelDb', autospec=True,
                                  spec_set=True).start()()

    def test_startup_fail(self):
        """Check that startup fails due to extant pidfile."""
        handle, extant_pid = tempfile.mkstemp()
        os.close(handle)
        loader = apel.db.loader.Loader(self.dir_path, False, 'mysql', 'host',
                                       1234, 'db', 'user', 'pwd', extant_pid)
        self.assertRaises(apel.db.loader.LoaderException, loader.startup)
        os.remove(extant_pid)

    def test_startup_shutdown(self):
        """Check that pidfile is created on startup and removed on shutdown."""
        pidfile = os.path.join(self.dir_path, 'pidfile')
        loader = apel.db.loader.Loader(self.dir_path, False, 'mysql', 'host',
                                       1234, 'db', 'user', 'pwd', pidfile)

        loader.startup()
        self.assertTrue(os.path.exists(pidfile))

        loader.shutdown()
        self.assertFalse(os.path.exists(pidfile))

    def test_load_all(self):
        """Check that load_records is called with the right arguments."""
        pidfile = os.path.join(self.dir_path, 'pidfile')

        in_q = dirq.queue.Queue(os.path.join(self.dir_path, 'incoming'),
                                schema=schema)
        in_q.add({"body": "bad message", "signer": "test signer", "empaid": "",
                  "error": ""})
        in_q.add({"body": "APEL-summary-job-message: v0.3",
                  "signer": "test signer", "empaid": "", "error": ""})

        self.loader = apel.db.loader.Loader(self.dir_path, True, 'mysql',
                                            'host', 1234, 'db', 'user', 'pwd',
                                            pidfile)
        self.loader.load_all_msgs()
        self.mock_db.load_records.assert_called_once_with([],
                                                          source='test signer')

    def tearDown(self):
        shutil.rmtree(self.dir_path)
        mock.patch.stopall()

if __name__ == '__main__':
    unittest.main()
