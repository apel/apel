from datetime import datetime
import unittest

from apel.db.loader import AurParser
from apel.db.loader.xml_parser import XMLParserException
from test_car_parser import datetimes_equal


class AurParserTest(unittest.TestCase):
    """Test case for AUR Parser"""

    def test_aur_parser(self):
        # Careful!  I added a Z to the end of the dates here but they weren't there in the CAR spec...
        example1 = '''<?xml version="1.0" encoding="UTF-8"?>
<aur:SummaryRecord xmlns:aur="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord" xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord ../org.glite.dgas_B_4_0_0/config-consumers/car_aggregated_v1.2.xsd ">
  <aur:Site>aur:Site</aur:Site>
  <aur:Month>1</aur:Month>
  <aur:Year>2012</aur:Year>
  <aur:UserIdentity/>
  <aur:Infrastructure urf:type="grid"/>
  <aur:EarliestEndTime>2012-01-01T12:00:00Z</aur:EarliestEndTime>
  <aur:LatestEndTime>2012-01-31T12:00:00Z</aur:LatestEndTime>
  <aur:WallDuration>P1D</aur:WallDuration>
  <aur:CpuDuration>P1D</aur:CpuDuration>
  <aur:ServiceLevel urf:type="token">0.0</aur:ServiceLevel>
  <aur:NumberOfJobs>1</aur:NumberOfJobs>
</aur:SummaryRecord>'''

        values1 = {"Site": "aur:Site",
                   "Month": 1,
                   "Year": 2012,
                   "Infrastructure": "grid",
                   "WallDuration": 86400,
                   "CpuDuration": 86400,
                   "EarliestEndTime": datetime(2012, 1, 1, 12, 0, 0),
                   "LatestEndTime": datetime(2012, 1, 31, 12, 0, 0),
                   #"ServiceLevel": Decimal('0.0'),
                   "NumberOfJobs": 1
                   }

        example2 = '''<?xml version="1.0" encoding="UTF-8"?>
<aur:SummaryRecord xmlns:aur="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord" xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord ../org.glite.dgas_B_4_0_0/config-consumers/car_aggregated_v1.2.xsd ">
  <aur:Site urf:type="gocdb">aur:Site</aur:Site>
  <aur:Month>1</aur:Month>
  <aur:Year>2012</aur:Year>
  <aur:UserIdentity>
    <urf:GlobalUserName urf:type="opensslCompat">urf:GlobalUserName</urf:GlobalUserName>
    <urf:Group>TestGroup</urf:Group>
    <urf:GroupAttribute urf:type="vo-group">vogroup</urf:GroupAttribute>
  </aur:UserIdentity>
  <aur:MachineName urf:description="">aur:MachineName</aur:MachineName>
  <aur:SubmitHost>aur:SubmitHost</aur:SubmitHost>
  <aur:Host primary="true" urf:description="">aur:Host</aur:Host>
  <aur:Queue urf:description="execution">aur:Queue</aur:Queue>
  <aur:Infrastructure urf:description="" urf:type="grid"/>
  <aur:Middleware urf:description="" urf:name="" urf:version="">aur:Middleware</aur:Middleware>
  <aur:EarliestEndTime>2012-01-01T12:00:00Z</aur:EarliestEndTime>
  <aur:LatestEndTime>2012-01-31T12:00:00Z</aur:LatestEndTime>
  <aur:WallDuration>P1D</aur:WallDuration>
  <aur:CpuDuration>P1D</aur:CpuDuration>
  <aur:ServiceLevel urf:description="" urf:type="token">0.0</aur:ServiceLevel>
  <aur:NumberOfJobs>1</aur:NumberOfJobs>
  <aur:Memory urf:description="" urf:metric="total" urf:phaseUnit="P1D" urf:storageUnit="b" urf:type="token">1</aur:Memory>
  <aur:Swap urf:description="" urf:metric="total" urf:phaseUnit="P1D" urf:storageUnit="b" urf:type="token">1</aur:Swap>
  <aur:NodeCount urf:description="" urf:metric="total">1</aur:NodeCount>
  <aur:Processors urf:consumptionRate="0.0" urf:description="" urf:metric="token">1</aur:Processors>
</aur:SummaryRecord>'''

        values2 = {"Site": "aur:Site",
                   "Month": 1,
                   "Year": 2012,
                   "SubmitHost": "aur:SubmitHost",
                   "VO": "TestGroup",
                   "VOGroup": "vogroup",
                   "Infrastructure": "grid",
                   "WallDuration": 86400,
                   "CpuDuration": 86400,
                   "EarliestEndTime": datetime(2012, 1, 1, 12, 0, 0),
                   "LatestEndTime": datetime(2012, 1, 31, 12, 0, 0),
                   # "ServiceLevel": Decimal(0.0),
                   "NumberOfJobs": 1,
                   "NodeCount": 1,
                   "Processors": 1
                   }

        # test CarRecord fields
        cases = {}
        cases[example1] = values1
        cases[example2] = values2

        for aur in cases:
            parser = AurParser(aur)
            record = parser.get_records()[0]
            cont = record._record_content

            # Mandatory fields - need checking.
            for field in ('Site', 'Month', 'Year',
                          'WallDuration', 'CpuDuration', 'NumberOfJobs'):
                # Also need: 'NormalisedWallDuration', 'NormalisedCpuDuration'
                self.assertIn(field, cont, "Field '%s' not found" % field)

            for key in cases[aur]:
                if isinstance(cont[key], datetime):
                    if not datetimes_equal(cont[key], cases[aur][key]):
                        self.fail("Datetimes don't match for key %s: %s, %s" % (key, cont[key], cases[aur][key]))
                else:
                    self.assertEqual(cont[key], cases[aur][key], "%s != %s for key %s" % (cont[key], cases[aur][key], key))

            # This should pass
            # record.get_db_tuple()

    def test_empty_xml(self):
        """
        Check that correct exception is raised for an XML file with no records.
        """
        parser = AurParser("<something></something>")
        self.assertRaises(XMLParserException, parser.get_records)


if __name__ == '__main__':
    unittest.main()
