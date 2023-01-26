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

    def test_dict_field_parsing(self):
        good_inputs = {"{D: 3.0, E:4}": {'D': 3.0, 'E': 4.0}, "{A:1,B:2}": {'A': 1.0, 'B': 2.0}}
        bad_inputs =  ["{A:1,A:2}", "{1: 2}", "{A: 1, A: 2}"]

        for key in good_inputs:
            self.assertEqual(Record()._clean_up_dict(key), good_inputs[key])

        for value in bad_inputs:
            self.assertRaises(ValueError, Record()._clean_up_dict, value)

if __name__ == '__main__':
    unittest.main()
