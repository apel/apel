from builtins import str
import unittest

from apel.db.loader import StarParser
from apel.db.records import StorageRecord


class StorageRecordTest(unittest.TestCase):
    """
    Test case for StorageRecord
    """

    def test_load_from_tuple(self):
        # full example
        data = ('host.example.org/sr/87912469269276', 1289293612,
                'host.example.org', 'MySite', 'pool-003', 'disk', 'replicated',
                42, '/home/projectA', 'johndoe', 'projectA',
                '/O=Grid/OU=example.org/CN=John Doe',
                'binarydataproject.example.org', 'uk', 'poweruser',
                '2010-10-11T09:31:40Z', '2010-10-11T09:41:40Z', 14728, 13617, 0)

        record = StorageRecord()
        record.load_from_tuple(data)

        self.assertEqual(record.get_field('RecordId'),
                          'host.example.org/sr/87912469269276')
        self.assertEqual(str(record.get_field('CreateTime')),
                          "2010-11-09 09:06:52")
        self.assertEqual(record.get_field('StorageSystem'), 'host.example.org')
        self.assertEqual(record.get_field('Site'), 'MySite')
        self.assertEqual(record.get_field('StorageShare'), 'pool-003')
        self.assertEqual(record.get_field('StorageMedia'), 'disk')
        self.assertEqual(record.get_field('StorageClass'), 'replicated')
        self.assertEqual(record.get_field('FileCount'), 42)
        self.assertEqual(record.get_field('DirectoryPath'), '/home/projectA')
        self.assertEqual(record.get_field('LocalUser'), 'johndoe')
        self.assertEqual(record.get_field('LocalGroup'), 'projectA')
        self.assertEqual(record.get_field('UserIdentity'),
                          '/O=Grid/OU=example.org/CN=John Doe')
        self.assertEqual(record.get_field('Group'),
                          'binarydataproject.example.org')
        self.assertEqual(record.get_field('SubGroup'), 'uk')
        self.assertEqual(record.get_field('Role'), 'poweruser')
        self.assertEqual(str(record.get_field('StartTime')),
                          "2010-10-11 09:31:40")
        self.assertEqual(str(record.get_field('EndTime')),
                          "2010-10-11 09:41:40")
        self.assertEqual(record.get_field('ResourceCapacityUsed'), 14728)
        self.assertEqual(record.get_field('LogicalCapacityUsed'), 13617)
        self.assertEqual(record.get_field('ResourceCapacityAllocated'), 0)

    def test_mandatory_fields(self):
        record = StorageRecord()
        record.set_field('RecordId', 'host.example.org/sr/87912469269276')
        record.set_field('CreateTime', 1289293612)
        record.set_field('StorageSystem', 'host.example.org')
        record.set_field('StartTime', 1286785900)
        record.set_field('EndTime', 1286786500)
        record.set_field('ResourceCapacityUsed', 14728)

        try:
            record._check_fields()
        except Exception as e:
            self.fail('_check_fields method failed: %s [%s]' % (str(e), str(type(e))))

    def test_get_apel_db_insert(self):
        """Check that calling get_apel_db_insert raises no exceptions

        Previously there was a mismatch between the number of arguments of this
        and the parent Record class which led to a TypeError being raised.
        """

        record = StorageRecord()
        record.set_field('RecordId', 'host.example.org/sr/87912469269276')
        record.set_field('CreateTime', 1289293612)
        record.set_field('StorageSystem', 'host.example.org')
        record.set_field('StartTime', 1286785900)
        record.set_field('EndTime', 1286786500)
        record.set_field('ResourceCapacityUsed', 14728)

        record.get_apel_db_insert()
        record.get_apel_db_insert(None)

    def test_get_ur(self):
        """Check XML output of get_ur

        This checks that all input values save for createTime are present in the
        XML output, then it parses the XML back into a storage record and checks
        that the only mismatching field is CreateTime.
        """
        data = ('host.example.org/sr/87912469269276', 1289293612,
                'host.example.org', 'MySite', 'pool-003', 'disk', 'replicated',
                42, '/home/projectA', 'johndoe', 'projectA',
                '/O=Grid/OU=example.org/CN=John Doe',
                'binarydataproject.example.org', 'uk', 'poweruser',
                '2010-10-11T09:31:40Z', '2010-10-11T09:41:40Z', 14728, 13617, 0)

        record = StorageRecord()
        record.load_from_tuple(data)
        ur = record.get_ur()

        for value in data:
            # Skip the createTime value as it's regenerated when calling get_ur
            if value != 1289293612 and str(value) not in ur:
                self.fail("Input value '%s' not found in XML output." % value)

        XML_HEADER = '<?xml version="1.0" ?>'
        UR_OPEN = ('<sr:StorageUsageRecords xmlns:sr="http://eu-emi.eu/namespac'
                   'es/2011/02/storagerecord">')
        UR_CLOSE = '</sr:StorageUsageRecords>'

        parser = StarParser(XML_HEADER + UR_OPEN + ur + UR_CLOSE)

        # This works as all dictionary values are hashable/immutable
        missmatched = (set(parser.get_records()[0]._record_content.items()) ^
                       set(record._record_content.items()))
        for item in list(missmatched):
            # Only mismatched item should be CreateTime as it's regenerated
            self.assertEqual(item[0], 'CreateTime')


if __name__ == '__main__':
    unittest.main()
