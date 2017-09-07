import unittest

from apel.db.apeldb import ApelDb, ApelDbException, Query


class TestApelDb(unittest.TestCase):
    def test_unknown_db(self):
        """Check that trying to use an unknown db raises an exception."""
        self.assertRaises(ApelDbException, ApelDb, 'wibble',
                          'testhost', 1234, 'groot', '', 'badtest')


class TestQuery(unittest.TestCase):
    """These test cases check the workings of the Query.get_where method."""

    def setUp(self):
        self.query = Query()

    def test_bad_relation(self):
        self.query.TestField_bad = 3
        self.assertRaises(ApelDbException, self.query.get_where)

    def test_empty_where(self):
        self.assertEqual(self.query.get_where(), "")

    def test_get_lt(self):
        self.query.TestField_lt = 0
        self.assertEqual(self.query.get_where(), " WHERE TestField < '0'")

    def test_get_gt(self):
        self.query.TestField_gt = 13
        self.assertEqual(self.query.get_where(), " WHERE TestField > '13'")

    def test_get_le(self):
        self.query.TestField_le = 10
        self.assertEqual(self.query.get_where(), " WHERE TestField <= '10'")

    def test_get_ge(self):
        self.query.TestField_ge = 12
        self.assertEqual(self.query.get_where(), " WHERE TestField >= '12'")

    def test_get_e(self):
        self.query.TestField = 7
        self.assertEqual(self.query.get_where(), " WHERE TestField = '7'")

    def test_in(self):
        self.query.TestField_in = ('one', 'two')
        self.assertEqual(self.query.get_where(),
                         ' WHERE TestField IN ("one","two")')

    def test_notin(self):
        self.query.TestField_notin = ('one', 'two')
        self.assertEqual(self.query.get_where(),
                         ' WHERE TestField NOT IN ("one","two")')


if __name__ == '__main__':
    unittest.main()
