from datetime import datetime
import unittest

from apel.db.loader import StarParser
from apel.db.loader.xml_parser import XMLParserException

from test_car_parser import datetimes_equal


class StarParserTest(unittest.TestCase):
    """
    Test case for StarParser.
    """

    def test_star_parser(self):

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

        values1 = {'StorageSystem': 'discordia.desy.de',
                   'Site': 'desycerttb',
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

        values2 = {'StorageSystem': 'discordia.desy.de',
                   'Site': 'desycerttb',
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

        values3 = {'StorageSystem': 'host.example.org',
                   'Site': 'ACME-University',
                   'StorageMedia': 'disk',
                   'FileCount': 42,
                   'StartTime': datetime(2010, 10, 11, 9, 31, 40),
                   'EndTime': datetime(2010, 10, 12, 9, 29, 42),
                   'ResourceCapacityUsed': 14728,
                   'LogicalCapacityUsed': 13617
                   }

        cases = {}
        cases[star1] = values1
        cases[star2] = values2
        cases[star3] = values3

        for star in cases:

            parser = StarParser(star)
            record = parser.get_records()[0]
            cont = record._record_content

            #  Mandatory fields
            for field in ("RecordId", "CreateTime", "StorageSystem",
                          "StartTime", "EndTime", "ResourceCapacityUsed"):
                self.assertTrue(field in cont, "Field '%s' not found" % field)

            for key in list(cases[star].keys()):
                if isinstance(cont[key], datetime):
                    if not datetimes_equal(cont[key], cases[star][key]):
                        self.fail("Datetimes don't match for key %s: %s, %s" % (key, cont[key], cases[star][key]))
                else:
                    self.assertEqual(cont[key], cases[star][key], "%s != %s for key %s" % (cont[key], cases[star][key], key))

    def test_group_attribute(self):
        """
        Check that loading a storage record with GroupAttribute fields works.

        The example Storage Usage Record should produce both StorageRecords and
        a GroupAttribute record, depending on what GroupAttributes are present.
        """

        star = '''
<sr:StorageUsageRecords xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">
  <sr:StorageUsageRecord>
    <sr:RecordIdentity sr:createTime="2016-06-09T02:42:15Z" sr:recordId="c698"/>
    <sr:StorageSystem>test-sys.ac.uk</sr:StorageSystem>
    <sr:SubjectIdentity>
      <sr:Group>ops</sr:Group>
      <sr:Site>EXAMPLE</sr:Site>
    </sr:SubjectIdentity>
    <sr:StorageMedia>disk</sr:StorageMedia>
    <sr:StartTime>2016-06-08T02:42:15Z</sr:StartTime>
    <sr:EndTime>2016-06-09T02:42:15Z</sr:EndTime>
    <sr:FileCount>4630</sr:FileCount>
    <sr:ResourceCapacityUsed>0</sr:ResourceCapacityUsed>
    <sr:ResourceCapacityAllocated>0</sr:ResourceCapacityAllocated>
    <sr:LogicalCapacityUsed>30</sr:LogicalCapacityUsed>
  </sr:StorageUsageRecord>
  <sr:StorageUsageRecord>
    <sr:RecordIdentity sr:createTime="2016-06-09T02:42:15Z" sr:recordId="c69b"/>
    <sr:StorageSystem>test-sys.ac.uk</sr:StorageSystem>
    <sr:SubjectIdentity>
      <sr:Group>cms</sr:Group>
      <sr:GroupAttribute sr:attributeType="authority">/O=Grid/OU=eg.org/CN=host/auth.eg.org</sr:GroupAttribute>
      <sr:Site>EXAMPLE</sr:Site>
    </sr:SubjectIdentity>
    <sr:StorageMedia>disk</sr:StorageMedia>
    <sr:StartTime>2016-06-08T02:42:15Z</sr:StartTime>
    <sr:EndTime>2016-06-09T02:42:15Z</sr:EndTime>
    <sr:FileCount>346298</sr:FileCount>
    <sr:ResourceCapacityUsed>0</sr:ResourceCapacityUsed>
    <sr:ResourceCapacityAllocated>0</sr:ResourceCapacityAllocated>
    <sr:LogicalCapacityUsed>26770352879563</sr:LogicalCapacityUsed>
  </sr:StorageUsageRecord>
  <sr:StorageUsageRecord>
    <sr:RecordIdentity sr:createTime="2016-06-09T02:42:15Z" sr:recordId="lc69"/>
    <sr:StorageSystem>test-sys.ac.uk</sr:StorageSystem>
    <sr:SubjectIdentity>
      <sr:GroupAttribute sr:attributeType="role">cmsphedex</sr:GroupAttribute>
      <sr:Group>cms</sr:Group>
      <sr:Site>EXAMPLE</sr:Site>
    </sr:SubjectIdentity>
    <sr:StorageMedia>disk</sr:StorageMedia>
    <sr:StartTime>2016-06-08T02:42:15Z</sr:StartTime>
    <sr:EndTime>2016-06-09T02:42:15Z</sr:EndTime>
    <sr:FileCount>132742</sr:FileCount>
    <sr:ResourceCapacityUsed>0</sr:ResourceCapacityUsed>
    <sr:ResourceCapacityAllocated>0</sr:ResourceCapacityAllocated>
    <sr:LogicalCapacityUsed>194962053020199</sr:LogicalCapacityUsed>
  </sr:StorageUsageRecord>
  <sr:StorageUsageRecord>
    <sr:RecordIdentity sr:createTime="2016-09-08T12:16:10Z" sr:recordId="0715"/>
    <sr:StorageSystem>test-sys.ac.uk</sr:StorageSystem>
    <sr:SubjectIdentity>
      <sr:GroupAttribute sr:attributeType="role">poweruser1</sr:GroupAttribute>
      <sr:Group>atlas</sr:Group>
      <sr:GroupAttribute sr:attributeType="subgroup">uk</sr:GroupAttribute>
      <sr:Site>EXAMPLE</sr:Site>
    </sr:SubjectIdentity>
    <sr:StorageMedia>disk</sr:StorageMedia>
    <sr:StartTime>2016-09-07T12:16:10Z</sr:StartTime>
    <sr:EndTime>2016-09-08T12:16:10Z</sr:EndTime>
    <sr:FileCount>8</sr:FileCount>
    <sr:ResourceCapacityUsed>0</sr:ResourceCapacityUsed>
    <sr:ResourceCapacityAllocated>0</sr:ResourceCapacityAllocated>
    <sr:LogicalCapacityUsed>6000437876</sr:LogicalCapacityUsed>
  </sr:StorageUsageRecord>
</sr:StorageUsageRecords>

'''

        parser = StarParser(star)

        for record in parser.get_records():
            if record.get_field('RecordId') == 'c698':
                # No group attributes.
                self.assertEqual(record.get_field('Group'), 'ops')
            elif record.get_field('RecordId') == 'c69b':
                # GroupAttribute authority defined, which goes in record below.
                self.assertEqual(record.get_field('Group'), 'cms')
            elif record.get_field('StarRecordID') == 'c69b':
                # Only authority defined (so GroupAttribute record created).
                self.assertEqual(record.get_field('AttributeType'), 'authority')
                self.assertEqual(record.get_field('AttributeValue'),
                                 '/O=Grid/OU=eg.org/CN=host/auth.eg.org')
            elif record.get_field('RecordId') == 'lc69':
                # Only role defined.
                self.assertEqual(record.get_field('Group'), 'cms')
                self.assertEqual(record.get_field('SubGroup'), None)
                self.assertEqual(record.get_field('Role'), 'cmsphedex')
            elif record.get_field('RecordId') == '0715':
                # Both subgroup and role defined.
                self.assertEqual(record.get_field('Group'), 'atlas')
                self.assertEqual(record.get_field('SubGroup'), 'uk')
                self.assertEqual(record.get_field('Role'), 'poweruser1')
            else:
                # If it's not in the list, something's gone wrong.
                self.fail("Record with ID %s doesn't match test cases" %
                          record.get_field('RecordId'))

    def test_empty_xml(self):
        """
        Check that correct exception is raised for an XML file with no records.
        """
        parser = StarParser("<something></something>")
        self.assertRaises(XMLParserException, parser.get_records)


if __name__ == '__main__':
    unittest.main()
