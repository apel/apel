import datetime
import unittest

from apel.db.loader import CarParser
from apel.db.loader.xml_parser import XMLParserException


def datetimes_equal(dt1, dt2):
    """Compare if datetimes are equal to the nearest second."""
    diff = dt1 - dt2
    return abs(diff) < datetime.timedelta(seconds=1)


class CarParserTest(unittest.TestCase):
    """Test case for Car Parser"""

    def setUp(self):
        pass
        #self.parser = CarParser(self.example_data)

    def test_car_parser(self):
        # Careful! I added a Z to the end of the dates here but they weren't there in the CAR spec...
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

        values1 = {'Site': 'urf:Site',
                   'MachineName': 'MachineName',
                   'LocalJobId': 'urf:LocalJobId',
                   'LocalUserId': 'urf:LocalUserId',
                   'WallDuration': 86400,
                   'CpuDuration': 86400,
                   'StartTime': datetime.datetime(2001, 12, 31, 12, 0, 0),
                   'EndTime': datetime.datetime(2001, 12, 31, 12, 0, 0),
                   }

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

        values2 = {"Site": "PGS03-GRID-UPJS-SK",
                   "MachineName": "pgs03.grid.upjs.sk",
                   "LocalJobId": "jobid10",
                   "LocalUserId": "gridtest",
                   "WallDuration": 4,
                   "CpuDuration": 3,
                   "ServiceLevelType": "Si2K",
                   "ServiceLevel": 1,
                   "NodeCount": 2,
                   "StartTime": datetime.datetime(2013, 2, 9, 15, 9, 16),
                   "EndTime": datetime.datetime(2013, 2, 9, 15, 11, 41),
                   "SubmitHost": "gsiftp://pgs03.grid.upjs.sk:2811/jobs",
                   "Queue": "gridlong"
                   }

        car3 = '''<com:UsageRecord xmlns:com="http://eu-emi.eu/namespaces/2012/11/computerecord">
        <com:RecordIdentity com:recordId="62991a08-909b-4516-aa30-3732ab3d8998" com:createTime="2013-02-22T15:58:44.567+01:00"/>
        <com:JobIdentity>
          <com:GlobalJobId>ac2b1157-7aff-42d9-945e-389aa9bbb19a</com:GlobalJobId>
          <com:LocalJobId>7005</com:LocalJobId>
        </com:JobIdentity>
        <com:UserIdentity>
          <com:GlobalUserName com:type="rfc2253">CN=Bjoern Hagemeier,OU=Forschungszentrum Juelich GmbH,O=GridGermany,C=DE</com:GlobalUserName>
          <com:LocalUserId>bjoernh</com:LocalUserId>
          <com:LocalGroup>users</com:LocalGroup>
        </com:UserIdentity>
        <com:JobName>HiLA</com:JobName>
        <com:Status>completed</com:Status>
        <com:ExitStatus>0</com:ExitStatus>
        <com:Infrastructure com:type="grid"/>
        <com:Middleware com:name="unicore">unicore</com:Middleware>
        <com:WallDuration>PT0S</com:WallDuration>
        <com:CpuDuration>PT0S</com:CpuDuration>
        <com:ServiceLevel com:type="HEPSPEC">1.0</com:ServiceLevel>
        <com:Memory com:metric="total" com:storageUnit="KB" com:type="physical">0</com:Memory>
        <com:Memory com:metric="total" com:storageUnit="KB" com:type="shared">0</com:Memory>
        <com:TimeInstant com:type="uxToBssSubmitTime">2013-02-22T15:58:44.568+01:00</com:TimeInstant>
        <com:TimeInstant com:type="uxStartTime">2013-02-22T15:58:46.563+01:00</com:TimeInstant>
        <com:TimeInstant com:type="uxEndTime">2013-02-22T15:58:49.978+01:00</com:TimeInstant>
        <com:TimeInstant com:type="etime">2013-02-22T15:58:44+01:00</com:TimeInstant>
        <com:TimeInstant com:type="ctime">2013-02-22T15:58:44+01:00</com:TimeInstant>
        <com:TimeInstant com:type="qtime">2013-02-22T15:58:44+01:00</com:TimeInstant>
        <com:TimeInstant com:type="maxWalltime">2013-02-22T16:58:45+01:00</com:TimeInstant>
        <com:NodeCount>1</com:NodeCount>
        <com:Processors>2</com:Processors>
        <com:EndTime>2013-02-22T15:58:45+01:00</com:EndTime>
        <com:StartTime>2013-02-22T15:58:45+01:00</com:StartTime>
        <com:MachineName>zam052v15.zam.kfa-juelich.de</com:MachineName>
        <com:SubmitHost>zam052v02</com:SubmitHost>
        <com:Queue com:description="execution">batch</com:Queue>
        <com:Site>zam052v15.zam.kfa-juelich.de</com:Site>
        <com:Host com:primary="false" com:description="CPUS=2;SLOTS=1,0">zam052v15</com:Host>
        </com:UsageRecord>'''

        values3 = {"LocalJobId": "7005",
                   "GlobalUserName": "CN=Bjoern Hagemeier,OU=Forschungszentrum Juelich GmbH,O=GridGermany,C=DE",
                   "LocalUserId": "bjoernh",
                   "InfrastructureType": "grid",
                   'WallDuration': 0,
                   'CpuDuration': 0,
                   'ServiceLevelType': 'HEPSPEC',
                   'ServiceLevel': 1,
                   'NodeCount': 1,
                   'Processors': 2,
                   'StartTime': datetime.datetime(2013, 2, 22, 14, 58, 45),
                   'EndTime': datetime.datetime(2013, 2, 22, 14, 58, 45),
                   'MachineName': 'zam052v15.zam.kfa-juelich.de',
                   'SubmitHost': 'zam052v02',
                   'Queue': 'batch',
                   'Site': 'zam052v15.zam.kfa-juelich.de'
                   }

        cases = {}
        cases[car1] = values1
        cases[car2] = values2
        cases[car3] = values3

        for car in cases:

            parser = CarParser(car)
            record = parser.get_records()[0]
            cont = record._record_content

            #  Mandatory fields - need checking.
            self.assertIn('Site', cont)
            self.assertIn('Queue', cont)
            self.assertIn('LocalJobId', cont)
            self.assertIn('WallDuration', cont)
            self.assertIn('CpuDuration', cont)
            self.assertIn('StartTime', cont)
            self.assertIn('EndTime', cont)

            for key in list(cases[car].keys()):
                if isinstance(cont[key], datetime.datetime):
                    if not datetimes_equal(cont[key], cases[car][key]):
                        self.fail("Datetimes don't match for key %s: %s, %s" % (key, cont[key], cases[car][key]))
                else:
                    self.assertEqual(cont[key], cases[car][key], '%s != %s for key %s' % (cont[key], cases[car][key], key))

    def test_empty_xml(self):
        """
        Check that exception is raised for XML not in computerecord namepsace.
        """
        parser = CarParser("<something></something>")
        self.assertRaises(XMLParserException, parser.get_records)

    #def test_empty_record(self):
    #    # Not sure what should be returned with an empty record like this.
    #    parser = CarParser('<urf:UsageRecord xmlns:urf="http://eu-emi.eu/namesp'
    #                       'aces/2012/11/computerecord"></urf:UsageRecord>')
    #    print parser.get_records()[0]._record_content

if __name__ == '__main__':
    unittest.main()
