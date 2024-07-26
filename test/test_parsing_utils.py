import unittest

from apel.common import parse_fqan


class ParsingUtilsTest(unittest.TestCase):
    '''
    Test case for test_parse_fqan method
    '''

    def test_parse_fqan(self):
        self.assertEqual((None, None, 'role=2'), parse_fqan('role=2'))
        self.assertEqual(('role=some', '/Test', 'Test'), parse_fqan('/Test/role=some/test'))

        wrong_fqan1 = "hello."
        wrong_fqan2 = "the/the/the"

        right_fqan1 = "/atlas/role=doer"
        right_fqan2 = "/atlas/somethingelse/role=doer"
        right_fqan3 = "/atlas/Role=production/Capability=NULL;/atlas/Role=NULL/Capability=NULL;/atlas/alarm/Role=NULL/Capability=NULL;/atlas/au/Role=NULL/Capability=NULL;/atlas/dataprep/Role=NULL/Capability=NULL;/atlas/lcg1/Role=NULL/Capability=NULL;/atlas/team/Role=NULL/Capability=NULL;/atlas/uk/Role=NULL/Capability=NULL"
        right_fqan4 = "/ilc/Role=NULL/Capability=NULL"
        right_fqan5 = "/wlcg"
        right_fqan6 = "/wlcg/Role=pilot/Capability=NULL"

        short_fqan1 = "/no/role/or/equals"
        short_fqan2 = "/someorg/somegroup"

        self.assertEqual(parse_fqan(wrong_fqan1), (None, None, wrong_fqan1))
        self.assertEqual(parse_fqan(wrong_fqan2), (None, None, wrong_fqan2))

        self.assertEqual(parse_fqan(right_fqan1), ("role=doer", "/atlas", "atlas"))
        self.assertEqual(parse_fqan(right_fqan2), ("role=doer", "/atlas/somethingelse", "atlas"))
        self.assertEqual(parse_fqan(right_fqan3), ("Role=production", "/atlas", "atlas"))
        self.assertEqual(parse_fqan(right_fqan4), ("Role=NULL", "/ilc", "ilc"))
        self.assertEqual(parse_fqan(right_fqan5), ("None", "/wlcg", "wlcg"))
        self.assertEqual(parse_fqan(right_fqan6), ("Role=pilot", "/wlcg", "wlcg"))

        self.assertEqual(parse_fqan(short_fqan1), ('None', '/no/role/or/equals', 'no'))
        self.assertEqual(parse_fqan(short_fqan2), ('None', '/someorg/somegroup', 'someorg'))

if __name__ == '__main__':
    unittest.main()
