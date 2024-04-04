"""
   Copyright 2012 STFC

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

import time
from apel.db.records import Record

import logging

# get the relevant logger
log = logging.getLogger(__name__)


class StorageSummaryRecord(Record):
    """
    Class to represent one summarised storage record.

    It knows about the structure of the MySQL table and the message format.
    It stores its information in a dictionary self._record_content.  The keys
    are in the same format as in the messages, and are case-sensitive.
    """

    # This list specifies the information that goes in the database.
    DB_FIELDS = ["Site", "StorageSystem", "StorageShare", "StorageMedia",
                 "DirectoryPath", "Group", "EndTime", "Month", "Year",
                 "FileCount", "ResourceCapacityUsed", "LogicalCapacityUsed",
                 "ResourceCapacityAllocated"]

    ALL_FIELDS = DB_FIELDS

    def __init__(self):
        """Provide the necessary lists containing message information."""

        Record.__init__(self)

        # This list specifies the information that goes in the database.
        self._db_fields = StorageSummaryRecord.DB_FIELDS

        # Fields which are accepted but currently ignored.
        self._ignored_fields = []

        self._all_fields = self._db_fields
        self._datetime_fields = ["EndTime"]
        # Fields which will have an integer stored in them
        self._int_fields = ["FileCount", "ResourceCapacityUsed",
                            "LogicalCapacityUsed", "ResourceCapacityAllocated"]

    def get_apel_db_insert(self, source=None):
        """
        Returns record content as a tuple, appending the source of the record
        (i.e. the sender's DN).  Also returns the appropriate stored procedure.

        We have to go back to the apel_db object to find the stored procedure.
        This is because only this object knows what type of record it is,
        and only the apel_db knows what the procedure details are.
        """

        values = self.get_db_tuple(source)

        return values

    def get_db_tuple(self, source=None):
        """
        Return record contents as tuple ignoring the 'source' keyword argument.

        The source (DN of the sender) isn't used in this record type currently.
        """
        return Record.get_db_tuple(self)

    def verify_and_add_field(self, doc, field_key, value_converter=None):
        """
        Helper method to verify if a field is NOT None.

        The `field_key` parameter is the name of the field in the record.
        The `value_converter` parameter is an optional for specifying type,
        to apply to the field value before adding it to the document.
        """
        value = self.get_field(field_key)

        if value is not None:
            if value_converter is not None:
                value = value_converter(value)
            doc[field_key] = value

    def get_ur(self, withhold_dns=False):
        """
        Returns the summarised storage record in YAML format.

        Namespace information is written only once per record, by dbunloader.
        """
        del withhold_dns  # Unused

        doc = {}

        if self.get_field('EndTime') is not None:
            doc["EndTime"] = time.strftime(
                '%Y-%m-%dT%H:%M:%SZ',
                self.get_field('EndTime').timetuple()
                )

        self.verify_and_add_field(doc, 'StorageSystem')
        self.verify_and_add_field(doc, 'Site')
        self.verify_and_add_field(doc, 'StorageShare')
        self.verify_and_add_field(doc, 'StorageMedia')
        self.verify_and_add_field(doc, 'DirectoryPath')
        self.verify_and_add_field(doc, 'Group')
        self.verify_and_add_field(doc, 'Month', value_converter=str)
        self.verify_and_add_field(doc, 'Year', value_converter=str)
        self.verify_and_add_field(doc, 'FileCount')
        self.verify_and_add_field(doc, 'ResourceCapacityUsed')
        self.verify_and_add_field(doc, 'LogicalCapacityUsed')
        self.verify_and_add_field(doc, 'ResourceCapacityAllocated')

        return doc
