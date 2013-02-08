from unittest import TestCase
import datetime
from decimal import Decimal
from apel.db.loader import AurParser

class AurParserTest(TestCase):
    '''
    Test case for AUR Parser
    '''

    def setUp(self):
        pass
        #self.parser = CarParser(self.example_data)
    

# This currently fails because the AUR parser isn't working.    

#    def test_aur_parser(self):
#        
#        # Careful!  I added a Z to the end of the dates here but they weren't there in the CAR spec...
#        example1 = '''<?xml version="1.0" encoding="UTF-8"?>
#<aur:SummaryRecord xmlns:aur="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord" xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord ../org.glite.dgas_B_4_0_0/config-consumers/car_aggregated_v1.2.xsd ">
#  <aur:Site>aur:Site</aur:Site>
#  <aur:Month>1</aur:Month>
#  <aur:Year>2012</aur:Year>
#  <aur:UserIdentity/>
#  <aur:Infrastructure urf:type="grid"/>
#  <aur:EarliestEndTime>2012-01-01T12:00:00Z</aur:EarliestEndTime>
#  <aur:LatestEndTime>2012-01-31T12:00:00Z</aur:LatestEndTime>
#  <aur:WallDuration>P1D</aur:WallDuration>
#  <aur:CpuDuration>P1D</aur:CpuDuration>
#  <aur:ServiceLevel urf:type="token">0.0</aur:ServiceLevel>
#  <aur:NumberOfJobs>1</aur:NumberOfJobs>
#</aur:SummaryRecord>'''
#    
#        values1 = {"Site": "aur:Site", 
#                        "Month": 1, 
#                        "Year": 2012, 
#                        "InfrastructureType": "grid",
#                        "WallDuration":86400,
#                        "CpuDuration": 86400,
#   #                     "EarliestEndTime": datetime.datetime(2012, 1, 1, 12, 00, 00),
#   #                     "LatestEndTime": datetime.datetime(2012, 1, 31, 12, 00, 00),
#   #                     "ServiceLevel": Decimal(0.0),
#                        "NumberOfJobs": 1
#                        }
#        
#        example2 = '''<?xml version="1.0" encoding="UTF-8"?>
#<aur:SummaryRecord xmlns:aur="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord" xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord ../org.glite.dgas_B_4_0_0/config-consumers/car_aggregated_v1.2.xsd ">
#  <aur:Site urf:type="gocdb">aur:Site</aur:Site>
#  <aur:Month>1</aur:Month>
#  <aur:Year>2012</aur:Year>
#  <aur:UserIdentity>
#    <urf:GlobalUserName urf:type="opensslCompat">urf:GlobalUserName</urf:GlobalUserName>
#    <urf:Group>urf:Group</urf:Group>
#    <urf:GroupAttribute urf:type="vo-group">vogroup</urf:GroupAttribute>
#  </aur:UserIdentity>
#  <aur:MachineName urf:description="">aur:MachineName</aur:MachineName>
#  <aur:SubmitHost>aur:SubmitHost</aur:SubmitHost>
#  <aur:Host primary="true" urf:description="">aur:Host</aur:Host>
#  <aur:Queue urf:description="execution">aur:Queue</aur:Queue>
#  <aur:Infrastructure urf:description="" urf:type="grid"/>
#  <aur:Middleware urf:description="" urf:name="" urf:version="">aur:Middleware</aur:Middleware>
#  <aur:EarliestEndTime>2012-01-01T12:00:00Z</aur:EarliestEndTime>
#  <aur:LatestEndTime>2012-01-31T12:00:00Z</aur:LatestEndTime>
#  <aur:WallDuration>P1D</aur:WallDuration>
#  <aur:CpuDuration>P1D</aur:CpuDuration>
#  <aur:ServiceLevel urf:description="" urf:type="token">0.0</aur:ServiceLevel>
#  <aur:NumberOfJobs>1</aur:NumberOfJobs>
#  <aur:Memory urf:description="" urf:metric="total" urf:phaseUnit="P1D" urf:storageUnit="b" urf:type="token">1</aur:Memory>
#  <aur:Swap urf:description="" urf:metric="total" urf:phaseUnit="P1D" urf:storageUnit="b" urf:type="token">1</aur:Swap>
#  <aur:NodeCount urf:description="" urf:metric="total">1</aur:NodeCount>
#  <aur:Processors urf:consumptionRate="0.0" urf:description="" urf:metric="token">1</aur:Processors>
#</aur:SummaryRecord>'''
#
#        values2 = {"Site": "aur:Site", 
#                        "Month": 1, 
#                        "Year": 2012, 
#                        "SubmitHost": "aur:SubmitHost",
#                        "VO": "urf:Group",
#                        "VOGroup": "vogroup",
#                        "InfrastructureType": "grid",
#                        "WallDuration":86400,
#                        "CpuDuration": 86400,
# #                       "EarliestEndTime": datetime.datetime(2012, 1, 1, 12, 00, 00),
# #                       "LatestEndTime": datetime.datetime(2012, 1, 31, 12, 00, 00),
# #                       "ServiceLevel": Decimal(0.0),
#                        "NumberOfJobs": 1,
#                        "NodeCount": 1,
#                        "Processors": 1
#                        }
#        
#        
#        # test CarRecord fields
#        cases = {}
#        cases[example1] = values1
#        cases[example2] = values2
#        
#        for aur in cases.keys():
#            
#            parser  = AurParser(aur)
#            record = parser.get_records()[0]
#            cont = record._record_content
#            
#            # Mandatory fields - need checking.
#            self.assertTrue(cont.has_key("Site"))
#            self.assertTrue(cont.has_key("Month"))
#            self.assertTrue(cont.has_key("Year"))
#            self.assertTrue(cont.has_key("WallDuration"))
#            self.assertTrue(cont.has_key("CpuDuration"))
#            self.assertTrue(cont.has_key("NumberOfJobs"))
#        
#        
#            for key in cases[aur].keys():
#                print key
#                self.assertEqual(cont[key], cases[aur][key], "%s != %s for key %s" % (cont[key], cases[aur][key], key))