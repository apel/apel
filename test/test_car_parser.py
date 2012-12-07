from unittest import TestCase
from apel.db.loader import CarParser

class CarParserTest(TestCase):
    '''
    Test case for Car Parser
    '''
    
    example_data = '''<?xml version="1.0" encoding="UTF-8"?>
<urf:UsageRecord xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/computerecord ../../../org.glite.dgas_B_4_0_0/config-consumers/car_v1.2.xsd ">
  <urf:RecordIdentity urf:createTime="2001-12-31T12:00:00" urf:recordId="token"/>
  <urf:JobIdentity>
    <urf:LocalJobId>urf:LocalJobId</urf:LocalJobId>
  </urf:JobIdentity>
  <urf:UserIdentity>
    <urf:LocalUserId>urf:LocalUserId</urf:LocalUserId>
  </urf:UserIdentity>
  <urf:Status>aborted</urf:Status>
  <urf:Infrastructure/>
  <urf:WallDuration>P1D</urf:WallDuration>
  <urf:CpuDuration>P1D</urf:CpuDuration>
  <urf:ServiceLevel urf:type="token">0.0</urf:ServiceLevel>
  <urf:EndTime>2001-12-31T12:00:00</urf:EndTime>
  <urf:StartTime>2001-12-31T12:00:00</urf:StartTime>
  <urf:MachineName>MachineName</urf:MachineName>
  <urf:Queue>urf:Queue</urf:Queue>
  <urf:Site>urf:Site</urf:Site>
</urf:UsageRecord>
'''
    
    def setUp(self):
        self.parser = CarParser(self.example_data)
    
    def test_car_parser(self):
        records = self.parser.get_records()
        self.assertEqual(len(records), 1, 'Invalid number of records')
        
        car_record, = records
        self.assertEqual(car_record.get_field('Site'), 'urf:Site')
        self.assertEqual(car_record.get_field('MachineName'), 'MachineName')
        self.assertEqual(car_record.get_field('LocalJobId'), 'urf:LocalJobId')
        self.assertEqual(car_record.get_field('LocalUserId'), 'urf:LocalUserId')
        self.assertEqual(car_record.get_field('WallDuration'), 1)
        self.assertEqual(car_record.get_field('CpuDuration'), 1)
        self.assertEqual(str(car_record.get_field('StartTime')), "2001-12-31 12:00:00")
        self.assertEqual(str(car_record.get_field('EndTime')), "2001-12-31 12:00:00")
        
        # test CarRecord fields
        