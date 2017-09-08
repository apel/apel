"""Test cases for functionality given by base parser."""

import unittest

import apel.parsers


class BaseParserTest(unittest.TestCase):
    """Test cases for the base APEL parser class."""

    def setUp(self):
        self.parser = apel.parsers.Parser('testSite', 'testHost')

    def test_constants(self):
        """Check that the constants are set as expected."""
        self.assertEqual(self.parser.UNPROCESSED, '0')
        self.assertEqual(self.parser.PROCESSED, '1')

    def test_base_parse(self):
        """Check that parsing with the base parser fails with an error."""
        self.assertRaises(NotImplementedError, self.parser.parse, 'line')

    def test_base_recognize(self):
        """Check that using recognize with the base parser gives False."""
        self.assertFalse(self.parser.recognize('line'))


class AllParsersRecognizeTest(unittest.TestCase):
    """Test cases for the parser recognize method."""

    def test_good(self):
        """Check that each parser's recognize method works for a sample line."""
        tests = {
            'Blah': (
                '"timestamp=2012-05-20 23:59:47" "userDN=/O=Gd/OU=Un/CN=Chp" "u'
                'serFQAN=/atlas/Role=prod" "ceID=cream.grid.io" "jobID=CREAM123'
                '" "lrmsID=9575064.lrms1" "localUser=11999"'),
            'HTCondor': 'ce.rl#276.0#7189|ts11|287|107|11|1463|140|236|232|1|1',
            'LSF': (
                '"JOB_FINISH" "5.1" 1089407406 699195 283 33554482 1 1089290023'
                ' 0 0 1089406862 "raortega" "8nm" "" "" "" "lxplus015" "prog/st'
                'ep3c" "" "/step3c-362.txt" "/berr-step3c-362.txt" "1089290023.'
                '699195" 0 1 "tbed0079" 64 3.3 "" "/artEachset.j 362 7 8" 277.2'
                '10000 17.280000 0 0 -1 0 0 927804 87722 0 0 0 -1 0 0 0 0 0 -1 '
                '"" "default" 0 1 "" "" 0 310424 339112 "" "" ""'),
            'PBS': (
                '04/30/2014 15:36:20;E;5000.bob;user=dbeer group=dbeer jobname='
                'STDIN queue=batch ctime=1398892818 qtime=1398892818 etime=1398'
                '892818 start=1398893580 owner=dbeer@bob exec_host=bob/0 sessio'
                'n=22933 end=1398893780 Exit_status=0 resources_used.cput=00:00'
                ':00 resources_used.mem=2580kb resources_used.vmem=37072kb reso'
                'urces_used.walltime=00:03:20'),
            'SGE': (
                'dteam:testce.test:dteam:dteam041:STDIN:43:sge:19:1200093286:12'
                '00093294:1200093295:0:0:1:0:0:0.000000:0:0:0:0:46206:0:0:0.0:0'
                ':0:0:0:337:257:NONE:defaultdepartment:NONE:1:0:0.09:0.000213:0'
                '.0:-U dteam -q dteam:0.0:NONE:30171136.0'),
            'Slurm': (
                '1007|c_61|dt5|dtm|2013-03-27T17:13:41|2013-03-27T17:13:44|00:0'
                '0:03|3|prod|1|1|c-40|||COMPLETED'),
        }

        for test in tests:
            parser_object = getattr(apel.parsers, test + 'Parser')
            parser = parser_object('testSite', 'testHost', True)
            self.assertTrue(parser.recognize(tests[test]), test)

    def test_none(self):
        """
        Check that parsers that can return None fail on appropriate lines.

        Only these parsers have the extra functionality to return None when they
        parse a syntactically valid line that should be ignored e.g. unfinished.
        The others either return the record or raise an exception.
        """
        tests = {
            'LSF': (
                '"JOB_RESIZE" "5.1" 1089407406 699195 283 33554482 1 1089290023'
                ' 0 0 1089406862 "raortega" "8nm" "" "" "" "lxplus015" "prog/st'
                'ep3c" "" "/step3c-362.txt" "/berr-step3c-362.txt" "1089290023.'
                '699195" 0 1 "tbed0079" 64 3.3 "" "/artEachset.j 362 7 8" 277.2'
                '10000 17.280000 0 0 -1 0 0 927804 87722 0 0 0 -1 0 0 0 0 0 -1 '
                '"" "default" 0 1 "" "" 0 310424 339112 "" "" ""'),
            'PBS': '04/30/2014 15:33:00;S;5000.bob;the_rest',
            'Slurm': (
                '123|batch|||2013-10-25T12:11:20|2013-10-25T12:11:36|00:00:16|1'
                '6||1|1|wn|28K|20K|BOOT_FAIL'),
        }

        for test in tests:
            parser_object = getattr(apel.parsers, test + 'Parser')
            parser = parser_object('testSite', 'testHost', True)
            self.assertFalse(parser.recognize(tests[test]), test)


if __name__ == '__main__':
    unittest.main()
