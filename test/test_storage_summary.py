import unittest
from apel.db.records.record import InvalidRecordException
from apel.db.records.storage_summary import StorageSummaryRecord


class StorageSummaryRecordTest(unittest.TestCase):
    """
    Test case for StorageSummaryRecord
    """

    def test_load_from_tuple(self):
        # full example
        data = ('MySite', 'host.example.org', 'pool-003', 'disk',
                '/home/projectA', 'binarydataproject.example.org',
                '2023-10-11T09:41:40Z', 10, 2023, 42, 14728, 13617, 0)

        record = StorageSummaryRecord()
        record.load_from_tuple(data)

        self.assertEqual(record.get_field('Site'), 'MySite')
        self.assertEqual(record.get_field('StorageSystem'), 'host.example.org')
        self.assertEqual(record.get_field('StorageShare'), 'pool-003')
        self.assertEqual(record.get_field('StorageMedia'), 'disk')
        self.assertEqual(record.get_field('DirectoryPath'), '/home/projectA')
        self.assertEqual(record.get_field('Group'),
                          'binarydataproject.example.org')
        self.assertEqual(str(record.get_field('EndTime')),
                          "2023-10-11 09:41:40")
        self.assertEqual(record.get_field('Month'), 10)
        self.assertEqual(record.get_field('Year'), 2023)
        self.assertEqual(record.get_field('FileCount'), 42)
        self.assertEqual(record.get_field('ResourceCapacityUsed'), 14728)
        self.assertEqual(record.get_field('LogicalCapacityUsed'), 13617)
        self.assertEqual(record.get_field('ResourceCapacityAllocated'), 0)

    def test_get_apel_db_insert(self):
        """Check that calling get_apel_db_insert raises no exceptions
        """

        record = StorageSummaryRecord()
        record.set_field('Site', 'MySite')
        record.set_field('EndTime', 1697017300)
        record.set_field('StorageSystem', 'host.example.org')
        record.set_field('ResourceCapacityUsed', 14728)

        try:
            record.set_field('Something', 1212)
        except InvalidRecordException as keyError:
            self.assertEqual(str(keyError), 'Unknown field: Something')

        record.get_apel_db_insert(None)

    def test_get_ur(self):
        """Check YAML output of get_ur

        This checks that all input values are present in the
        YAML output.
        """
        data = ('MySite', 'host.example.org', 'pool-003', 'disk',
                '/home/projectA', 'binarydataproject.example.org',
                '2023-10-11T09:41:40Z', 10, 2023, 42, 14728, 13617, 0)

        expected_data =  {'StorageShare': 'pool-003',
                          'DirectoryPath': '/home/projectA',
                          'Group': 'binarydataproject.example.org', 'Month': '10',
                          'LogicalCapacityUsed': 13617,
                          'StorageSystem': 'host.example.org',
                          'Site': 'MySite', 'ResourceCapacityUsed': 14728,
                          'Year': '2023', 'StorageMedia': 'disk',
                          'EndTime': '2023-10-11T09:41:40Z',
                          'ResourceCapacityAllocated': 0, 'FileCount': 42}

        record = StorageSummaryRecord()
        record.load_from_tuple(data)
        ur = record.get_ur()

        self.assertEqual(ur, expected_data)

if __name__ == '__main__':
    unittest.main()
