import os
import subprocess
import unittest

import apel.db.apeldb


class MysqlTest(unittest.TestCase):
    # These test cases require a local MySQL db server with a apel_unittest db
    def setUp(self):
        schema_path = os.path.abspath(os.path.join('..', 'schemas',
                                                   'server.sql'))
        schema_handle = open(schema_path)
        subprocess.Popen(['mysql', 'apel_unittest'], stdin=schema_handle).wait()
        schema_handle.close()

        self.db = apel.db.apeldb.ApelDb('mysql', 'localhost', 3306, 'root', '',
                                        'apel_unittest')

    def test(self):
        self.db.test_connection()


if __name__ == '__main__':
    unittest.main()
