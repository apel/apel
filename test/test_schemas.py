import os
from subprocess import Popen, PIPE
import unittest


class SchemaTest(unittest.TestCase):
    # These test cases require a local MySQL db server
    def setUp(self):
        Popen(['mysql', "-e 'DROP DATABASE IF EXISTS apel_unittest; CREATE DATABASE apel_unittest;'"])

    def tearDown(self):
        Popen(['mysql', "-e 'DROP DATABASE apel_unittest;'"]).wait()


def make_schema_test(schema):
    def schema_test(self):
        if schema == 'server-extra':
            schema_path = os.path.abspath(os.path.join('..', 'schemas', 'server.sql'))
            schema_handle = open(schema_path)
            Popen(['mysql', 'apel_unittest'], stdin=schema_handle).wait()
            schema_handle.close()
        schema_path = os.path.abspath(os.path.join('..', 'schemas', schema + '.sql'))
        schema_handle = open(schema_path)
        p = Popen(['mysql', 'apel_unittest'], stdin=schema_handle, stderr=PIPE)
        p.wait()
        schema_handle.close()
        self.assertFalse(p.returncode, p.communicate()[1])
    return schema_test

for schema in ('client', 'cloud', 'server', 'server-extra', 'storage'):
    test_method = make_schema_test(schema)
    test_method.__name__ = 'test_%s_schema' % schema
    setattr(SchemaTest, test_method.__name__, test_method)


if __name__ == '__main__':
    unittest.main()
