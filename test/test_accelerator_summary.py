#!/bin/env python2.7

import unittest

from apel.db.records import AcceleratorSummary


class AcceleratorSummaryRecordTest(unittest.TestCase):
    """
    Test case for AcceleratorSummary
    """

    def setUp(self):
        self._msg1 = '''
                Month: 12
                Year: 2021
                AssociatedRecordType: cloud
                GlobalUserName: /C=UK/O=eScience/OU=CLRC/L=RAL/CN=apel-consumer2.esc.rl.ac.uk/emailAddress=sct-certificates@stfc.ac.uk
                SiteName: Site Navigation
                Count: 604800.000
                Cores: 857
                AvailableDuration: 326057
                ActiveDuration: 30739
                BenchmarkType: Site FAQs
                Benchmark: 326.000
                Model: HS About
                Type: Accelerator
                NumberOfRecords: 1000
                '''

        self._values1 = {
                'Month': 12,
                'Year': 2021,
                'AssociatedRecordType': 'cloud',
                'GlobalUserName': '/C=UK/O=eScience/OU=CLRC/L=RAL/CN=apel-consumer2.esc.rl.ac.uk/emailAddress=sct-certificates@stfc.ac.uk',
                'SiteName': 'Site Navigation',
                'Count': 604800.000,
                'Cores': 857,
                'AvailableDuration': 326057,
                'ActiveDuration': 30739,
                'BenchmarkType': 'Site FAQs',
                'Benchmark': 326.000,
                'Model': 'HS About',
                'Type': 'Accelerator',
                'NumberOfRecords': 1000,
        }

        self.cases = {}
        self.cases[self._msg1] = self._values1

    def test_load_from_msg(self):
        for msg in self.cases.keys():

            acceleratorr = AcceleratorSummary()
            acceleratorr.load_from_msg(msg)

            cont = acceleratorr._record_content

            for key in self.cases[msg].keys():
                self.assertEqual(cont[key], self.cases[msg][key], "%s != %s for key %s" % (cont[key], self.cases[msg][key], key))

    def test_mandatory_fields(self):
        record = AcceleratorSummary()
        record.set_field("Month", '01')
        record.set_field("Year", '2021')
        record.set_field("AssociatedRecordType", 'cloud')
        record.set_field('SiteName', 'MySite')
        record.set_field("Count", 100.01)
        record.set_field("AvailableDuration", 1000)
        record.set_field("Type", 'Accelerator')
        record.set_field("NumberOfRecords", 10)

        try:
            record._check_fields()
        except Exception as e:
            self.fail('_check_fields method failed: %s [%s]' % (e, type(e)))

if __name__ == '__main__':
    unittest.main()
