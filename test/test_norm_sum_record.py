# Copyright 2016 The Science and Technology Facilities Council
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test cases for the NormalisedSummaryRecord based on SummaryRecord tests."""


from builtins import zip
from builtins import str

from datetime import datetime, timedelta
import unittest

from apel.db.records import NormalisedSummaryRecord, InvalidRecordException


class TestNormalisedSummaryRecord(unittest.TestCase):
    """
    Tests the NormalisedSummaryRecord class.
    """

    def setUp(self):
        """Run before each test."""
        self._records = self._get_record_text()
        self._tuples = self._get_record_tuples()
        self._wrong_records = self._get_wrong_records()

    def test_load_from_msg(self):
        """This currently checks that an exception is not thrown."""
        for record in self._records:
            nsr = NormalisedSummaryRecord()
            nsr.load_from_msg(record)

    def test_get_msg(self):
        """This currently checks that an exception is not thrown."""
        for record in self._records:
            nsr = NormalisedSummaryRecord()
            nsr.load_from_msg(record)

            # not a proper test yet
            nsr.get_msg()

    def test_load_from_msg_wrong(self):
        """Check that invalid records don't get loaded."""

        nsr = NormalisedSummaryRecord()

        # N.B. When values are being loaded from messages, they are all strings.
        # Not a dictionary because I want to use more than one value per key.
        invalid_values = [('Month', 0), ('Month', 13), ('Year', 2030),
                          ('CpuDuration', -123), ('WallDuration', 'hello'),
                          ('Site', 'Null')]

        for key, value in invalid_values:
            nsr.load_from_msg(self._records[1])

            nsr._record_content[key] = value
            self.assertRaises(InvalidRecordException, nsr.get_msg)

    def test_load_from_msg_wrong_2(self):
        """This checks that an exception is thrown when invalid
        records are loaded."""
        for record in self._wrong_records:
            nsr = NormalisedSummaryRecord()

            self.assertRaises(InvalidRecordException, nsr.load_from_msg, record)

    def test_get_apel_db_insert(self):
        """Test that the method getting the data to put into the DB
        actually does retrieve the correct values."""

        for rec_txt, rec_tuple in zip(self._records, self._tuples):

            nsr = NormalisedSummaryRecord()
            nsr.load_from_msg(rec_txt)

            test_dn = "This is a test DN."

            # Mock object so we don't have to use an actual DB.
            values = nsr.get_db_tuple(test_dn)
            for item1, item2 in zip(values, rec_tuple):
                if isinstance(item1, datetime):
                    if abs(item1 - item2) > timedelta(seconds=1):
                        self.fail('Datetimes %s and %s do not match.' % (item1,
                                                                         item2))

                if item1 != item2 and str(item1) != str(item2):
                    self.fail("Summary record values don't match: %s != %s" %
                              (item1, item2))

    def test_get_ur(self):
        """Check that get_ur outputs correct XML."""
        nsr = NormalisedSummaryRecord()
        nsr.load_from_msg(self._records[0])
        xml = ('<aur:SummaryRecord><aur:Site>RAL-LCG2</aur:Site><aur:Month>3</a'
               'ur:Month><aur:Year>2010</aur:Year><aur:UserIdentity><urf:GroupA'
               'ttribute urf:type="vo-group">/atlas</urf:GroupAttribute><urf:Gr'
               'oupAttribute urf:type="vo-role">Role=production</urf:GroupAttri'
               'bute></aur:UserIdentity><aur:SubmitHost>some.host.org</aur:Subm'
               'itHost><aur:Infrastructure urf:type="grid"/><aur:EarliestEndTim'
               'e>2010-03-01T01:00:00Z</aur:EarliestEndTime><aur:LatestEndTime>'
               '2010-03-20T01:00:00Z</aur:LatestEndTime><aur:WallDuration>PT234'
               '256S</aur:WallDuration><aur:CpuDuration>PT244435S</aur:CpuDurat'
               'ion><aur:NormalisedWallDuration>PT234256S</aur:NormalisedWallDu'
               'ration><aur:NormalisedCpuDuration>PT244435S</aur:NormalisedCpuD'
               'uration><aur:NumberOfJobs>100</aur:NumberOfJobs></aur:SummaryRe'
               'cord>')
        self.assertEqual(nsr.get_ur(), xml)

    def _get_record_text(self):
        """Gets some sample valid records, as a tuple of strings.  The contents
        must match the values in _get_record_tuples."""

        records = []
        record_text = """Site: RAL-LCG2
            Month: 3
            Year: 2010
            GlobalUserName: /C=whatever/D=someDN
            VO: atlas
            VOGroup: /atlas
            VORole: Role=production
            SubmitHost: some.host.org
            Infrastructure: grid
            EarliestEndTime: 1267405200
            LatestEndTime: 1269046800
            WallDuration: 234256
            CpuDuration: 244435
            NormalisedWallDuration: 234256
            NormalisedCpuDuration: 244435
            NumberOfJobs: 100"""

        record_text2 = """Site: RAL-LCG2
            Month: 4
            Year: 2010
            GlobalUserName: /C=whatever/D=someDN
            VO: atlas
            VOGroup: /atlas
            VORole: Role=production
            SubmitHost: some.host.org
            Infrastructure: local
            EarliestEndTime: 1270083600
            LatestEndTime: 1271725200
            WallDuration: 234256
            CpuDuration: 244435
            NormalisedWallDuration: 234256
            NormalisedCpuDuration: 244435
            NumberOfJobs: 100"""

        record_text3 = """Site: RAL-LCG2
            Month: 12
            Year: 2010
            GlobalUserName: /C=whatever/D=someDN
            VO: atlas
            VOGroup: /atlas
            VORole: Role=production
            SubmitHost: some.host.org
            Infrastructure: local
            EarliestEndTime: 1291161600
            LatestEndTime: 1291162100
            Processors: 1
            NodeCount: 1
            WallDuration: 234256
            CpuDuration: 244435
            NormalisedWallDuration: 234256
            NormalisedCpuDuration: 244435
            NumberOfJobs: 100"""

        records.append(record_text)
        records.append(record_text2)
        records.append(record_text3)
        return records

    def _get_record_tuples(self):
        """
        Get tuples with contents in the correct order to go into the
        stored procedure with the same values as in the messages in
        _get_record_txt().
        """
        tuples = []

        tuple1 = ('RAL-LCG2', 3, 2010, '/C=whatever/D=someDN', 'atlas',
                  '/atlas',   'Role=production', 'some.host.org', 'grid', None,
                  None, datetime.utcfromtimestamp(1267405200),
                  datetime.utcfromtimestamp(1269046800), 234256, 244435, 234256,
                  244435, 100)

        tuple2 = ('RAL-LCG2', 4, 2010, '/C=whatever/D=someDN', 'atlas',
                  '/atlas', 'Role=production', 'some.host.org', 'local', None,
                  None, datetime.utcfromtimestamp(1270083600),
                  datetime.utcfromtimestamp(1271725200), 234256, 244435, 234256,
                  244435, 100)

        tuple3 = ('RAL-LCG2', 12, 2010, '/C=whatever/D=someDN', 'atlas',
                  '/atlas', 'Role=production', 'some.host.org', 'local', 1, 1,
                  datetime.utcfromtimestamp(1291161600),
                  datetime.utcfromtimestamp(1291162100), 234256, 244435, 234256,
                  244435, 100)

        tuples.append(tuple1)
        tuples.append(tuple2)
        tuples.append(tuple3)

        return tuples

    def _get_wrong_records(self):

        records = []

        # wrong month
        record_text = """Site: RAL-LCG2
            Month: 13
            Year: 2010
            GlobalUserName: /C=whatever/D=someDN
            VO: atlas
            VOGroup: /atlas
            VORole: Role=production
            WallDuration: 234256
            CpuDuration: 2345
            NormalisedWallDuration: 234256
            NormalisedCpuDuration: 244435
            NumberOfJobs: 100"""

        # negative number
        record_text2 = """Site: RAL-LCG2
            Month: 4
            Year: 2010
            GlobalUserName: /C=whatever/D=someDN
            VO: atlas
            VOGroup: /atlas
            VORole: Role=production
            WallDuration: -234256
            CpuDuration: 2345
            NormalisedWallDuration: 234256
            NormalisedCpuDuration: 244435
            NumberOfJobs: 100"""

        # times outside of month
        record_text3 = """Site: RAL-LCG2
            Month: 5
            Year: 2010
            GlobalUserName: /C=whatever/D=someDN
            VO: atlas
            VOGroup: /atlas
            VORole: Role=production
            EarliestEndTime: 1234567890
            LatestEndTime: 1310641063
            WallDuration: 234256
            CpuDuration: 2345
            NormalisedWallDuration: 234256
            NormalisedCpuDuration: 244435
            NumberOfJobs: 100"""

        records.append(record_text)
        records.append(record_text2)
        records.append(record_text3)
        return records


if __name__ == '__main__':
    unittest.main()
