"""Test cases for classes in apel.db.apeldb."""

import unittest

from apel.db.apeldb import ApelDb, ApelDbException, Query


class TestApelDb(unittest.TestCase):
    """Test case(s) for base ApelDb class functionality."""
    def test_unknown_db(self):
        """Check that trying to use an unknown db raises an exception."""
        self.assertRaises(ApelDbException, ApelDb, 'wibble',
                          'testhost', 1234, 'groot', '', 'badtest')


class TestQuery(unittest.TestCase):
    """These test cases check the workings of the Query.get_where method."""

    def setUp(self):
        """Create an instance of apeldb.Query for use in test cases."""
        self.query = Query()

    def test_bad_relation(self):
        """Check that nonsense relationships lead to a raised exception."""
        self.query.TestField_bad = 3
        self.assertRaises(ApelDbException, self.query.get_where)

    def test_empty_where(self):
        """Check that a query with no relationships gives no WHERE clause."""
        self.assertEqual(self.query.get_where(), "")

    def test_get_lt(self):
        """Check that a less than gives the correct WHERE."""
        self.query.TestField_lt = 0
        self.assertEqual(self.query.get_where(), " WHERE TestField < '0'")

    def test_get_gt(self):
        """Check that a greater than gives the correct WHERE."""
        self.query.TestField_gt = 13
        self.assertEqual(self.query.get_where(), " WHERE TestField > '13'")

    def test_get_le(self):
        """Check that a less than or equal gives the correct WHERE."""
        self.query.TestField_le = 10
        self.assertEqual(self.query.get_where(), " WHERE TestField <= '10'")

    def test_get_ge(self):
        """Check that a greater than or equal gives the correct WHERE."""
        self.query.TestField_ge = 12
        self.assertEqual(self.query.get_where(), " WHERE TestField >= '12'")

    def test_get_e(self):
        """Check that an undecorated field gives an equal WHERE."""
        self.query.TestField = 7
        self.assertEqual(self.query.get_where(), " WHERE TestField = '7'")

    def test_in(self):
        """Check that an 'in' relationship gives the correct WHERE."""
        self.query.TestField_in = ('one', 'two')
        self.assertEqual(self.query.get_where(),
                         ' WHERE TestField IN ("one","two")')

    def test_notin(self):
        """Check that a 'not in' relationship gives the correct WHERE."""
        self.query.TestField_notin = ('one', 'two')
        self.assertEqual(self.query.get_where(),
                         ' WHERE TestField NOT IN ("one","two")')


if __name__ == '__main__':
    unittest.main()
