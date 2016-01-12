from datetime import datetime
import unittest

from apel.db.loader import StarParser
from apel.db.loader.xml_parser import XMLParserException

from test_car_parser import datetimes_equal


class StarParserTest(unittest.TestCase):
    '''
    Test case for StarParser
    '''
    
    def setUp(self):
        star1 = '''<?xml version="1.0" encoding="UTF-8" ?>
    <sr:StorageUsageRecords xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">
      <sr:StorageUsageRecord>
        <sr:RecordIdentity sr:createTime="2012-10-30T17:20:04Z" sr:recordId="desycerttb_cms_disk_20121030T172004Z"/>
        <sr:StorageSystem>discordia.desy.de</sr:StorageSystem>
        <sr:Site>desycerttb</sr:Site>
        <sr:StorageMedia>disk</sr:StorageMedia>
        <sr:FileCount>5</sr:FileCount>
        <sr:SubjectIdentity>
          <sr:Group>cms</sr:Group>
        </sr:SubjectIdentity>
        <sr:StartTime>2012-10-30T17:10:04Z</sr:StartTime>
        <sr:EndTime>2012-10-30T17:20:04Z</sr:EndTime>
        <sr:ResourceCapacityUsed>693064064</sr:ResourceCapacityUsed>
      </sr:StorageUsageRecord>
    </sr:StorageUsageRecords>'''
        
        values1 = {
                   'StorageSystem': 'discordia.desy.de',
                   'Site':'desycerttb',
                   'StorageMedia': 'disk',
                   'FileCount': 5,
                   'StartTime': datetime(2012, 10, 30, 17, 10, 4),
                   'EndTime': datetime(2012, 10, 30, 17, 20, 4),
                   'ResourceCapacityUsed': 693064064
                   }
        
        star2 = '''<?xml version="1.0" encoding="UTF-8" ?>
    <sr:StorageUsageRecords xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">
      <sr:StorageUsageRecord>
        <sr:RecordIdentity sr:createTime="2012-10-30T17:20:04Z" sr:recordId="desycerttb_atlas_disk_20121030T172004Z"/>
        <sr:StorageSystem>discordia.desy.de</sr:StorageSystem>
        <sr:Site>desycerttb</sr:Site>
        <sr:StorageMedia>disk</sr:StorageMedia>
        <sr:FileCount>163</sr:FileCount>
        <sr:SubjectIdentity>
          <sr:Group>atlas</sr:Group>
        </sr:SubjectIdentity>
        <sr:StartTime>2012-10-30T17:10:04Z</sr:StartTime>
        <sr:EndTime>2012-10-30T17:20:04Z</sr:EndTime>
        <sr:ResourceCapacityUsed>2843234682</sr:ResourceCapacityUsed>
      </sr:StorageUsageRecord>
    </sr:StorageUsageRecords>'''
    
        values2 = {
                   'StorageSystem': 'discordia.desy.de',
                   'Site':'desycerttb',
                   'StorageMedia': 'disk',
                   'FileCount': 163,
                   'StartTime': datetime(2012, 10, 30, 17, 10, 4),
                   'EndTime': datetime(2012, 10, 30, 17, 20, 4),
                   'ResourceCapacityUsed': 2843234682
                   }
    
    # From the StAR document.
        star3 = '''<sr:StorageUsageRecord
    xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">
    <sr:RecordIdentity    sr:createTime="2010-11-09T09:06:52Z"
            sr:recordId="host.example.org/sr/87912469269276"/>
    <sr:StorageSystem>host.example.org</sr:StorageSystem>
    <sr:Site>ACME-University</sr:Site>
    <sr:StorageShare>pool-003</sr:StorageShare>
    <sr:SubjectIdentity>
        <sr:Group>binarydataproject.example.org</sr:Group>
        <sr:GroupAttribute sr:attributeType="subgroup">ukusers</sr:GroupAttribute>
    </sr:SubjectIdentity>
    <sr:StorageMedia>disk</sr:StorageMedia>
    <sr:FileCount>42</sr:FileCount>
    <sr:StartTime>2010-10-11T09:31:40Z</sr:StartTime>
    <sr:EndTime>2010-10-12T09:29:42Z</sr:EndTime>
    <sr:ResourceCapacityUsed>14728</sr:ResourceCapacityUsed>
    <sr:LogicalCapacityUsed>13617</sr:LogicalCapacityUsed>
</sr:StorageUsageRecord>'''
    
        values3 = {
                   'StorageSystem': 'host.example.org',
                   'Site':'ACME-University',
                   'StorageMedia': 'disk',
                   'FileCount': 42,
                   'StartTime': datetime(2010, 10, 11, 9, 31, 40),
                   'EndTime': datetime(2010, 10, 12, 9, 29, 42),
                   'ResourceCapacityUsed': 14728,
                   'LogicalCapacityUsed': 13617
                   }
        
        self.cases = {}
        self.cases[star1] = values1
        self.cases[star2] = values2
        self.cases[star3] = values3
        
    def test_star_parser(self):
        for star in self.cases:
            
            parser  = StarParser(star)
            record = parser.get_records()[0]
            cont = record._record_content
            
            #  Mandatory fields
            self.assertTrue(cont.has_key("StorageSystem"))
            self.assertTrue(cont.has_key("StartTime"))
            self.assertTrue(cont.has_key("EndTime"))
            self.assertTrue(cont.has_key("ResourceCapacityUsed"))
        
            for key in self.cases[star].keys():
                if isinstance(cont[key], datetime):
                    if not datetimes_equal(cont[key], self.cases[star][key]):
                        self.fail("Datetimes don't match for key %s: %s, %s" % (key, cont[key], self.cases[star][key]))
                else:
                    self.assertEqual(cont[key], self.cases[star][key], "%s != %s for key %s" % (cont[key], self.cases[star][key], key))

    def test_empty_xml(self):
        """
        Check that correct exception is raised for an XML file with no records.
        """
        parser = StarParser("<something></something>")
        self.assertRaises(XMLParserException, parser.get_records)


if __name__ == '__main__':
    unittest.main()
