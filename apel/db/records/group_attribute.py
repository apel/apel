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

class GroupAttributeRecord(Record):
    '''
    GroupAttributeRecord represents single attribute record
    associated with StarRecord.
    
    Single StarRecord can have multiple GroupAttributeRecords.
    '''
    
    DB_FIELDS = ["StarRecordID", "AttributeType", "AttributeValue"]
    MANDATORY_FIELDS = ["StarRecordID"]
    
    ALL_FIELDS = DB_FIELDS
    
    def __init__(self):
        '''
        Initializer for GroupAttributeRecord
        '''
        Record.__init__(self)
        
        self._db_fields = self.DB_FIELDS
        self._mandatory_fields = self.MANDATORY_FIELDS
        self._all_fields = self._db_fields

    def get_db_tuple(self, source=None):
        """
        Return record contents as tuple ignoring the 'source' keyword argument.

        The source (DN of the sender) isn't used in this record type currently.
        """
        return Record.get_db_tuple(self)
