"""
   Copyright (C) 2023 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

from apel.db.records import Record


class AcceleratorRecord(Record):
    """Class to represent one Accelerator record."""
    def __init__(self):
        """Provide the necessary lists containing message information."""
        Record.__init__(self)

        # This specifies the order of entries to match the database schema
        self._db_fields = [
            "MeasurementMonth",
            "MeasurementYear",
            "AssociatedRecordType",
            "AssociatedRecord",
            "GlobalUserName",
            "FQAN",
            "SiteName",
            "Count",
            "Cores",
            "ActiveDuration",
            "AvailableDuration",
            "BenchmarkType",
            "Benchmark",
            "Type",
            "Model",
        ]

        # Fields which are required by the message format.
        self._mandatory_fields = [
            "MeasurementMonth",
            "MeasurementYear",
            "AssociatedRecordType",
            "AssociatedRecord",
            "FQAN",
            "SiteName",
            "Count",
            "AvailableDuration",
            "Type",
        ]

        self._int_fields = [
            "MeasurementMonth",
            "MeasurementYear",
            "Cores",
            "ActiveDuration",
            "AvailableDuration",
        ]

        self._float_fields = [
            "Count",
            "Benchmark",
        ]

        # This list specifies the output ordering for printed records
        self._msg_fields = self._db_fields

        # All allowed fields.
        self._all_fields = self._db_fields

    def _check_fields(self):
        """
        Add extra checks to those made in every record.
        Also populates fields that are extracted from other fields.
        """
        # First, call the parent's version.
        Record._check_fields(self)
