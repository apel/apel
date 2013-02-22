from unittest import TestCase
import datetime
from iso8601.iso8601 import UTC
from apel.db.loader import CarParser


def datetimes_equal(dt1, dt2):
    '''
    Compare if datetimes are equal to the nearest second.
    '''
    diff = dt1 - dt2
    return abs(diff) < datetime.timedelta(seconds = 1)

class CarParserTest(TestCase):
    '''
    Test case for Car Parser
    '''
    
    def setUp(self):
        pass
        #self.parser = CarParser(self.example_data)
    
    def test_car_parser(self):
        
        # Careful!  I added a Z to the end of the dates here but they weren't there in the CAR spec...
        car1 = '''<?xml version="1.0" encoding="UTF-8"?>
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
        car2 = '''<?xml version="1.0"?>
<UsageRecords xmlns="http://eu-emi.eu/namespaces/2012/11/computerecord">
  <UsageRecord xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <RecordIdentity urf:createTime="2013-02-09T15:39:16Z" urf:recordId="ur-pgs03-T1eKDmSEROhnyOkhppswXjgoABFKDmABFKDmzQNKDmABFKDm4BxvIn"/>
  <JobIdentity>
    <GlobalJobId>gsiftp://pgs03.grid.upjs.sk:2811/jobs/T1eKDmSEROhnyOkhppswXjgoABFKDmABFKDmzQNKDmABFKDm4BxvIn</GlobalJobId>
    <LocalJobId>jobid10</LocalJobId>
    </JobIdentity>
    <UserIdentity>
      <GlobalUserName urf:type="opensslCompat">/DC=eu/DC=KnowARC/O=nagios/CN=demo1</GlobalUserName>
      <LocalUserId>gridtest</LocalUserId>
    </UserIdentity>
    <Status>completed</Status>
    <ExitStatus>0</ExitStatus>
    <Infrastructure urf:description="pbs" urf:type="grid"/>
    <Middleware urf:name="arc" urf:version="3.0.0rc5" urf:description="nordugrid-arc 3.0.0rc5"></Middleware>
    <WallDuration>PT4S</WallDuration>
    <CpuDuration urf:usageType="user">PT1S</CpuDuration>
    <CpuDuration urf:usageType="system">PT2S</CpuDuration>
    <CpuDuration urf:usageType="all">PT3S</CpuDuration>
    <Memory urf:type="Shared" urf:metric="average" urf:storageUnit="KB">9404</Memory>
    <Memory urf:type="Physical" urf:metric="max" urf:storageUnit="KB">2368</Memory>
    <ServiceLevel urf:type="Si2K" urf:description="">1.0</ServiceLevel>
    <NodeCount>2</NodeCount>
    <EndTime>2013-02-09T15:11:41Z</EndTime>
    <StartTime>2013-02-09T15:09:16Z</StartTime>
    <MachineName>pgs03.grid.upjs.sk</MachineName>
    <SubmitHost>gsiftp://pgs03.grid.upjs.sk:2811/jobs</SubmitHost>
    <Queue urf:description="execution">gridlong</Queue>
    <Site urf:type="arc">PGS03-GRID-UPJS-SK</Site>
    <Host urf:primary="true">pgs03</Host>
    <Host>pgs03.grid.upjs.sk</Host></UsageRecord>
</UsageRecords>'''
    #<UsageRecord xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><RecordIdentity urf:createTime="2013-02-09T15:39:16Z" urf:recordId="ur-pgs03-5XHKDmQlQOhnyOkhppswXjgoABFKDmABFKDmPSIKDmABFKDmANxl3m"/><JobIdentity><GlobalJobId>gsiftp://pgs03.grid.upjs.sk:2811/jobs/5XHKDmQlQOhnyOkhppswXjgoABFKDmABFKDmPSIKDmABFKDmANxl3m</GlobalJobId><LocalJobId></LocalJobId></JobIdentity><UserIdentity><GlobalUserName urf:type="opensslCompat">/DC=eu/DC=KnowARC/O=nagios/CN=demo1</GlobalUserName><LocalUserId>gridtest</LocalUserId></UserIdentity><Status>completed</Status><ExitStatus>0</ExitStatus><Infrastructure urf:description="pbs" urf:type="grid"/><Middleware urf:name="arc" urf:version="3.0.0rc5" urf:description="nordugrid-arc 3.0.0rc5"></Middleware><WallDuration>PT0S</WallDuration><CpuDuration urf:usageType="user">PT0S</CpuDuration><CpuDuration urf:usageType="system">PT0S</CpuDuration><CpuDuration urf:usageType="all">PT0S</CpuDuration><ServiceLevel urf:type="Si2K" urf:description="">1.0</ServiceLevel><NodeCount>2</NodeCount><EndTime>2013-02-09T14:43:17Z</EndTime><StartTime>2013-02-09T14:39:16Z</StartTime><MachineName>pgs03.grid.upjs.sk</MachineName><SubmitHost>gsiftp://pgs03.grid.upjs.sk:2811/jobs</SubmitHost><Queue urf:description="execution">gridlong</Queue><Site urf:type="arc">PGS03-GRID-UPJS-SK</Site><Host urf:primary="true">pgs03</Host><Host>pgs03.grid.upjs.sk</Host></UsageRecord></UsageRecords>'''

    

        
        values1 = {"Site": "urf:Site", 
                        "MachineName":"MachineName",
                        "LocalJobId":"urf:LocalJobId", 
                        "LocalUserId": "urf:LocalUserId", 
                        "WallDuration":86400,
                        "CpuDuration": 86400,
                        "StartTime": datetime.datetime(2001, 12, 31, 12, 00, 00),
                        "EndTime": datetime.datetime(2001, 12, 31, 12, 00, 00),
                        }
        
        values2 = {"Site": "PGS03-GRID-UPJS-SK", 
                        "MachineName":"pgs03.grid.upjs.sk", 
                        "LocalJobId":"jobid10", 
                        "LocalUserId": "gridtest", 
                        "WallDuration":4,
                        "CpuDuration": 3,
                        "ServiceLevelType": "Si2K",
                        "ServiceLevel": 1,
                        "NodeCount": 2,
                        "StartTime": datetime.datetime(2013, 2, 9, 15, 9, 16),
                        "EndTime": datetime.datetime(2013, 2, 9, 15, 11, 41),
                        "SubmitHost": "gsiftp://pgs03.grid.upjs.sk:2811/jobs",
                        "Queue": "gridlong"
                        }
        
        
        # test CarRecord fields
        cases = {}
        cases[car1] = values1
        cases[car2] = values2
        
        for car in cases:
            
            parser  = CarParser(car)
            record = parser.get_records()[0]
            cont = record._record_content
            
            #  Mandatory fields - need checking.
            self.assertTrue(cont.has_key("Site"))
            self.assertTrue(cont.has_key("Queue"))
            self.assertTrue(cont.has_key("LocalJobId"))
            self.assertTrue(cont.has_key("WallDuration"))
            self.assertTrue(cont.has_key("CpuDuration"))
            self.assertTrue(cont.has_key("StartTime"))
            self.assertTrue(cont.has_key("EndTime"))
        
        
            for key in cases[car].keys():
                if isinstance(cont[key], datetime.datetime):
                    if not datetimes_equal(cont[key], cases[car][key]):
                        self.fail("Datetimes don't match for key %s: %s, %s" % (key, cont[key], cases[car][key]))
                else:
                    self.assertEqual(cont[key], cases[car][key], "%s != %s for key %s" % (cont[key], cases[car][key], key))