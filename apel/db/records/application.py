'''
   Copyright 2013 Henning Perl

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

from apel.db.records.record import Record


class ApplicationRecord(Record):
    """
    Class to represent an Application Accounting Record
    """

    def __init__(self, **kwargs):
        '''
        Initializer for ApplicationRecord
        '''

        Record.__init__(self)
        self._db_fields = ["Site", "MachineName", "BinaryPath", "ExitInfo",
                           "User", "StartTime", "EndTime"]
        self._datetime_fields = ["StartTime", "EndTime"]
        self._all_fields = self._db_fields
        self.set_all(kwargs)
