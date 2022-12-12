"""
   Copyright (C) 2011 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

@author Will Rogers
"""

from apel.db.records import Record, InvalidRecordException
from apel.common import parse_fqan
from datetime import datetime, timedelta


class CloudRecord(Record):
    """
    Class to represent one cloud record.

    It knows about the structure of the MySQL table and the message format.
    It stores its information in a dictionary self._record_content.  The keys
    are in the same format as in the messages, and are case-sensitive.
    """
    def __init__(self):
        """Provide the necessary lists containing message information."""

        Record.__init__(self)

        # Fields which are required by the message format.
        self._mandatory_fields = ["VMUUID", "SiteName", "StartTime"]

        # This list allows us to specify the order of lines when we construct records.
        self._msg_fields  = ["RecordCreateTime", "VMUUID", "SiteName", "CloudComputeService", "MachineName",
                             "LocalUserId", "LocalGroupId", "GlobalUserName", "FQAN",
                             "Status", "StartTime", "EndTime", "SuspendDuration",
                             "WallDuration", "CpuDuration", "CpuCount",
                             "NetworkType", "NetworkInbound", "NetworkOutbound", "PublicIPCount",
                             "Memory", "Disk", "BenchmarkType", "Benchmark",
                             "StorageRecordId", "ImageId", "CloudType"]

        # This list specifies the information that goes in the database.
        self._db_fields = self._msg_fields[:9] + ['VO', 'VOGroup', 'VORole'] + self._msg_fields[9:]
        self._all_fields = self._db_fields

        self._ignored_fields = ["UpdateTime", "MeasurementTime",
                                "MeasurementMonth", "MeasurementYear"]

        # Fields which will have an integer stored in them
        self._int_fields = [ "SuspendDuration", "WallDuration", "CpuDuration", "CpuCount",
                             "NetworkInbound", "NetworkOutbound", "PublicIPCount", "Memory", "Disk"]

        self._float_fields = ['Benchmark']
        self._datetime_fields = ["RecordCreateTime", "StartTime", "EndTime"]

    def _check_fields(self):
        """
        Add extra checks to those made in every record.
        """
        # First, call the parent's version.
        Record._check_fields(self)

        # Extract the relevant information from the user fqan.
        # Keep the fqan itself as other methods in the class use it.
        role, group, vo = parse_fqan(self._record_content['FQAN'])
        # We can't / don't put NULL in the database, so we use 'None'
        if role is None:
            role = 'None'
        if group is None:
            group = 'None'
        if vo is None:
            vo = 'None'

        if self._record_content['Benchmark'] is None:
            # If Benchmark is not present in the original record the
            # parent Record class level type checking will set it to
            # None. We can't pass None as a Benchmark as the field is
            # NOT NULL in the database, so we set it to something
            # meaningful. In this case the float 0.0.
            self._record_content['Benchmark'] = 0.0


        self._record_content['VORole'] = role
        self._record_content['VOGroup'] = group
        self._record_content['VO'] = vo

        # If the message was missing a CpuCount, assume it used
        # zero Cpus, to prevent a NULL being written into the column
        # in the CloudRecords tables.
        # Doing so would be a problem despite the CloudRecords
        # table allowing it because the CloudSummaries table
        # doesn't allow it, creating a problem at summariser time.
        if self._record_content['CpuCount'] is None:
            self._record_content['CpuCount'] = 0

        # Sanity check the values of StartTime and EndTime
        self._check_start_end_times()


    def _check_start_end_times(self):
        """
        Sanity checks the values of StartTime and EndTime in _record_content.

        - A record has an EndTime if and only if it is in the "completed"
          state.
        - If the record has an EndTime / is in the "completed" state, then
          - the EndTime is equal or grater than StartTime
          - the EndTime is not in the future
        """
        pass
