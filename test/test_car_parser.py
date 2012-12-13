from unittest import TestCase
import datetime
from apel.db.loader import CarParser

class CarParserTest(TestCase):
    '''
    Test case for Car Parser
    '''
    
    

    
    def setUp(self):
        pass
        #self.parser = CarParser(self.example_data)
    
    def test_car_parser(self):
        
        # Careful!  I added a Z to the end of the dates here but they weren't there in the CAR spec...
        example_data = '''<?xml version="1.0" encoding="UTF-8"?>
<urf:UsageRecord xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/computerecord ../../../org.glite.dgas_B_4_0_0/config-consumers/car_v1.2.xsd ">
  <urf:RecordIdentity urf:createTime="2001-12-31T12:00:00Z" urf:recordId="token"/>
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
  <urf:EndTime>2001-12-31T12:00:00Z</urf:EndTime>
  <urf:StartTime>2001-12-31T12:00:00Z</urf:StartTime>
  <urf:MachineName>MachineName</urf:MachineName>
  <urf:Queue>urf:Queue</urf:Queue>
  <urf:Site>urf:Site</urf:Site>
</urf:UsageRecord>
'''
    
        example_values = {"Site": "urf:Site", 
                        "MachineName":"MachineName", 
                        "LocalJobId":"urf:LocalJobId", 
                        "LocalUserId": "urf:LocalUserId", 
                        "WallDuration":86400,
                        "CpuDuration": 86400,
                        "StartTime": datetime.datetime(2001, 12, 31, 12, 00, 00),
                        "EndTime": datetime.datetime(2001, 12, 31, 12, 00, 00),
                        }
        
        
        # test CarRecord fields
        cases = {}
        cases[example_data] = example_values
        
        for car in cases.keys():
            
            parser  = CarParser(car)
            record = parser.get_records()[0]
            cont = record._record_content
            
            # Mandatory fields - need checking.
            self.assertTrue(cont.has_key("Site"))
            self.assertTrue(cont.has_key("Queue"))
            self.assertTrue(cont.has_key("LocalJobId"))
            self.assertTrue(cont.has_key("WallDuration"))
            self.assertTrue(cont.has_key("CpuDuration"))
            self.assertTrue(cont.has_key("StartTime"))
            self.assertTrue(cont.has_key("EndTime"))
        
        
            for key in cases[car].keys():
                self.assertEqual(cont[key], cases[car][key], "%s != %s for key %s" % (cont[key], cases[car][key], key))