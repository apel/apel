import unittest

from apel.db.records import Record, InvalidRecordException


class RecordTest(unittest.TestCase):
    '''
    Test case for Record
    '''
    # test for public interface
    def test_set_field(self):
        record = Record()
        self.assertRaises(InvalidRecordException,
                          record.set_field, 'Test', 'value')
        
        record._db_fields = ['Test']
        record.set_field('Test', 'value')
        
        self.assertEqual(record._record_content['Test'], 'value')
    
    
    def test_set_all(self):
        record = Record()
        
        self.assertRaises(InvalidRecordException,
                          record.set_all, {'Test':'value'})
        
        record._db_fields = ['Test']
        record.set_all({'Test':'value'})
        self.assertEqual(record._record_content['Test'], 'value')
        
    
    def test_get_field(self):
        record = Record()
        record._db_fields = ['Test']
        record._record_content['Test'] = 'value'
        
        self.assertEqual(record.get_field('Test'), 'value')

if __name__ == '__main__':
    unittest.main()
