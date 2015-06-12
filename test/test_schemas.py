import os
from subprocess import call, Popen, PIPE
import unittest


class SchemaTest(unittest.TestCase):
    # These test cases require a local MySQL db server
    def setUp(self):
        query = ('DROP DATABASE IF EXISTS apel_unittest;'
                 'CREATE DATABASE apel_unittest;')
        call(['mysql', '-e', query])

    def tearDown(self):
        call(['mysql', '-e', 'DROP DATABASE apel_unittest;'])


def make_schema_test(schema):
    """Make a test case that will check the given schema."""
    def schema_test(self):
        if schema == 'server-extra':
            # server-extra.sql needs server.sql loaded first
            parent_schema_path = os.path.abspath(os.path.join('..', 'schemas',
                                                              'server.sql'))
            parent_schema_handle = open(parent_schema_path)
            call(['mysql', 'apel_unittest'], stdin=parent_schema_handle)
            parent_schema_handle.close()
        schema_path = os.path.abspath(os.path.join('..', 'schemas',
                                                   '%s.sql' % schema))
        schema_handle = open(schema_path)
        p = Popen(['mysql', 'apel_unittest'], stdin=schema_handle, stderr=PIPE)
        schema_handle.close()
        p.wait()
        self.assertFalse(p.returncode, p.communicate()[1])
    return schema_test


for schema in ('client', 'cloud', 'server', 'server-extra', 'storage'):
    test_method = make_schema_test(schema)
    test_method.__name__ = 'test_%s_schema' % schema
    setattr(SchemaTest, test_method.__name__, test_method)


if __name__ == '__main__':
    unittest.main()
