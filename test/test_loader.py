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
        self.queue_path = tempfile.mkdtemp()
        mock.patch('apel.db.ApelDb').start()
        in_q = dirq.Queue(os.path.join(self.queue_path, 'incoming'),
                          schema=schema)
        in_q.add({"body": "test body", "signer": "test signer",
                  "empaid": "", "error": ""})

        self.loader = apel.db.loader.Loader(self.queue_path, False, 'mysql',
                                            'host', 1234, 'db', 'user', 'pwd',
                                            'somefile')

    def test_basic_load_all(self):
        """Check that load_all_msgs runs without problems."""
        self.loader.load_all_msgs()

    def tearDown(self):
        shutil.rmtree(self.queue_path)
        mock.patch.stopall()

if __name__ == '__main__':
    unittest.main()
