'''
   Copyright 2012 Konrad Jopek

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

from apel.db.records import Record

class ProcessedRecord(Record):
    '''
    A simple class for inserting data into
    ProcessedFiles table.

    This class is used for avoiding reparsing files
    that have been already parsed.
    '''
    def __init__(self):
        '''
        Initializes ProcessedRecord
        '''
        Record.__init__(self)

        self._db_fields = ["HostName", "FileName", "Hash", "StopLine", "Parsed"]
        self._int_fields = ["StopLine", "Parsed"]

        self._all_fields = self._db_fields
