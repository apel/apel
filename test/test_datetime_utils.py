from apel.common import valid_from, valid_until, parse_timestamp, iso2seconds
import unittest
import datetime


class DateTimeUtilsTest(unittest.TestCase):
    '''
    Test case for date/time functions from apel.common
    '''

    def test_valid_from(self):
        now = datetime.datetime.now()
        result = now-datetime.timedelta(days=1)
        self.assertEqual(result, valid_from(now))

    def test_valid_until(self):
        now = datetime.datetime.now()
        result = now+datetime.timedelta(days=28)
        self.assertEqual(result, valid_until(now))

    def test_parse_timestamp(self):
        '''
        Checks that the different time formats that we might have to parse
        are handled correctly.  Note that we convert into datetime objects
        with no timezone information for internal use.
        '''

        valid_dates = ['2010-01-01 10:01:02','2010-01-01T10:01:02Z','2010-01-01T11:01:02+01:00']
        dts = [ parse_timestamp(date) for date in valid_dates ]
        for dt in dts:
            self.assertEqual(dt.year, 2010)
            self.assertEqual(dt.month, 1)
            self.assertEqual(dt.day, 1)
            self.assertEqual(dt.hour, 10)
            self.assertEqual(dt.minute, 1)
            self.assertEqual(dt.second, 2)
            self.assertEqual(dt.tzinfo, None)

    def test_iso2seconds(self):
        """iso2seconds should be able to parse most iso 8601 duration strings"""
        durations = (('P1Y', 3600*24*365),
                     ('P1M', 2628000),
                     ('P1W', 3600*24*7),
                     ('P1D', 3600*24),
                     ('PT10H20M30S', 10*3600+20*60+30),
                     ('PT1H2M4.567S', 3600+2*60+5),
                     ('PT1H2M4,567S', 3600+2*60+5),
                     )

        for iso_in, seconds_out in durations:
            self.assertEqual(iso2seconds(iso_in), seconds_out,
                             "Duration '%s' converts to %s when it should be %s"
                             % (iso_in, iso2seconds(iso_in), seconds_out))

if __name__ == '__main__':
    unittest.main()
