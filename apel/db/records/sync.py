'''
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
'''

from apel.db.records import Record

class SyncRecord(Record):
    '''
    Class to represent one sync record.

    It knows about the structure of the MySQL table and the message format.
    It stores its information in a dictionary self._record_content.  The keys
    are in the same format as in the messages, and are case-sensitive.
    '''

    def __init__(self):
        '''Populate fields required to load the message.'''

        Record.__init__(self)

        # Fields which are required by the message format.
        self._mandatory_fields = ["Site", "NumberOfJobs", "Month", "Year"]

        # This list allows us to specify the order of lines when we construct
        # records.
        self._msg_fields = ['Site', 'SubmitHost', 'NumberOfJobs', 'Month', 'Year']

        # Fields which will have an integer stored in them
        self._int_fields = ["NumberOfJobs", "Month", "Year"]

        # This list specifies the information that goes in the database.
        self._db_fields = self._msg_fields
        # All allowed fields.
        self._all_fields = self._msg_fields
