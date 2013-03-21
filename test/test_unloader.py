from apel.db.unloader import DbUnloader, get_start_of_previous_month
import datetime
from unittest import TestCase

class TestDbUnloader(TestCase):
    '''
    Test case for DbUnloader.
    '''
    
    def setUp(self):
        db = None
        #self.unloader = DbUnloader(db, '/tmp')
    
    def test_get_start_of_previous_month(self):
        
        dt = datetime.datetime(2012,1,1,1,1,1)
        dt2 = datetime.datetime(2011,12,1,0,0,0)
        ndt = get_start_of_previous_month(dt)
        self.assertEqual(dt2, ndt)
        
        dt3 = datetime.datetime(2012,3,1,1,1,1)
        dt4 = datetime.datetime(2012,2,1,0,0,0)
        ndt = get_start_of_previous_month(dt3)
        self.assertEqual(dt4, ndt)