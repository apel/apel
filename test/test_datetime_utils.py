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
        result = parse_timestamp('2010-01-01 10:01:02')
        self.assertEqual(result.year, 2010)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 10)
        self.assertEqual(result.minute, 1)
        self.assertEqual(result.second, 2)
        
    def test_iso2seconds(self):
        txt1, txt2, txt3 = 'P1Y', 'P1M', 'P1D'
        
        self.assertTrue(iso2seconds(txt1), 3600*24*365)
        self.assertTrue(iso2seconds(txt2), 3600*24*30)
        self.assertTrue(iso2seconds(txt3), 3600*24)