from apel.common import valid_from, valid_until, parse_timestamp, \
    iso2seconds
from unittest import TestCase
import datetime


class DateTimeUtilsTest(TestCase):
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
        txt1, txt2, txt3 = 'P1Y', 'P1M', 'P1D'
        
        self.assertTrue(iso2seconds(txt1), 3600*24*365)
        self.assertTrue(iso2seconds(txt2), 3600*24*30)
        self.assertTrue(iso2seconds(txt3), 3600*24)