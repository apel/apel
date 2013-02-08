from unittest import TestCase
from apel.db.loader import StarParser
from datetime import datetime, timedelta

class StarParserTest(TestCase):
    '''
    Test case for StarParser
    '''
    example_data = '''<?xml version="1.0" encoding="UTF-8"?>
    <sr:StorageUsageRecords xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">
        <sr:StorageUsageRecord>
            <sr:RecordIdentity sr:createTime="2010-11-09T09:06:52Z" sr:recordId="host.example.org/sr/87912469269276"/>
            <sr:StorageSystem>host.example.org</sr:StorageSystem>
            <sr:StorageShare>pool-003</sr:StorageShare>
            <sr:StorageMedia>disk</sr:StorageMedia>
            <sr:StorageClass>replicated</sr:StorageClass>
            <sr:FileCount>42</sr:FileCount>
            <sr:DirectoryPath>/home/projectA</sr:DirectoryPath>
            <sr:SubjectIdentity>
                <sr:LocalUser>johndoe</sr:LocalUser>
                <sr:LocalGroup>projectA</sr:LocalGroup>
                <sr:UserIdentity>/O=Grid/OU=example.org/CN=John Doe</sr:UserIdentity>
                <sr:Group>binarydataproject.example.org</sr:Group>
                <sr:GroupAttribute sr:attributeType="subgroup">ukusers</sr:GroupAttribute>
            </sr:SubjectIdentity>
            <sr:MeasureTime>2010-10-11T09:31:40Z</sr:MeasureTime>
            <sr:ValidDuration>PT3600S</sr:ValidDuration>
            <sr:ResourceCapacityUsed>14728</sr:ResourceCapacityUsed>
            <sr:LogicalCapacityUsed>13617</sr:LogicalCapacityUsed>
        </sr:StorageUsageRecord>
    </sr:StorageUsageRecords>
    '''
    
    example_data2 = '''<?xml version="1.0" encoding="UTF-8" ?>
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
    
    def setUp(self):
        self.parser = StarParser(self.example_data2)
        
#    def test_star_parser(self):
#        records = self.parser.get_records()
#        self.assertEqual(len(records), 2, 'Invalid number of records')
#        
#        star_record, group_attribute = records
#        
#        # check the correctness of star_record
##        self.assertEqual(star_record.get_field('RecordId'), "host.example.org/sr/87912469269276")
##        self.assertEqual(star_record.get_field('StorageSystem'), 'host.example.org')
##        self.assertEqual(star_record.get_field('StorageShare'), 'pool-003')
##        self.assertEqual(star_record.get_field('StorageClass'), 'replicated')
##        self.assertEqual(star_record.get_field('FileCount'), 42)
##        self.assertEqual(star_record.get_field('DirectoryPath'), '/home/projectA')
##        self.assertEqual(star_record.get_field('LocalUser'), 'johndoe')
##        self.assertEqual(star_record.get_field('LocalGroup'), 'projectA')
##        self.assertEqual(star_record.get_field('UserIdentity'), '/O=Grid/OU=example.org/CN=John Doe')
##        self.assertEqual(star_record.get_field('GroupName'), 'binarydataproject.example.org')
##        self.assertEqual(str(star_record.get_field('MeasureTime')), "2010-10-11 09:31:40")
##        self.assertEqual(star_record.get_field('ValidDuration'), 3600)
##        self.assertEqual(star_record.get_field('ResourceCapacityUsed'), 14728)
##        self.assertEqual(star_record.get_field('LogicalCapacityUsed'), 13617)
##        
##        # check the correctess of group_attribute
##        self.assertEqual(group_attribute.get_field('StarRecordID'), 'host.example.org/sr/87912469269276')
##        self.assertEqual(group_attribute.get_field('AttributeType'), 'subgroup')
##        self.assertEqual(group_attribute.get_field('AttributeValue'), 'ukusers')
#
#        self.assertEqual(star_record.get_field('Site'), 'desycerttb')
#        self.assertEqual(star_record.get_field('RecordId'), "desycerttb_cms_disk_20121030T172004Z")
#        self.assertEqual(star_record.get_field('StorageSystem'), 'discordia.desy.de')
#        self.assertEqual(star_record.get_field('FileCount'), 5)
#        self.assertEqual(star_record.get_field('Group'), 'cms')
#        dt = datetime(2012,10,30,17,10,4)
#        st = star_record.get_field('StartTime')
#        st.microsecond = 0
#        if st != dt:
#            self.fail("StartTime isn't correctly parsed.")
#        if abs(star_record.get_field('EndTime') - dt) > timedelta(seconds = 1):
#            self.fail("StartTime isn't correctly parsed.")
#        #self.assertEqual(star_record.get_field('StartTime'), dt)
#        #self.assertEqual(str(star_record.get_field('EndTime')), "2012-10-30 17:10:04")
#        self.assertEqual(star_record.get_field('ResourceCapacityUsed'), 693064064)
#        
#        # check the correctess of group_attribute
##        self.assertEqual(group_attribute.get_field('StarRecordID'), 'desycerttb_cms_disk_20121030T172004Z')
##        self.assertEqual(group_attribute.get_field('AttributeType'), 'subgroup')
##        self.assertEqual(group_attribute.get_field('AttributeValue'), 'ukusers')
        