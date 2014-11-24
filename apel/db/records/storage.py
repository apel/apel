'''
   Copyright 2012 Will Rogers

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

import logging

# get the relevant logger
log = logging.getLogger(__name__)

class StorageRecord(Record):
    '''
    Class to represent one storage record. 
    
    It knows about the structure of the MySQL table and the message format.
    It stores its information in a dictionary self._record_content.  The keys 
    are in the same format as in the messages, and are case-sensitive.
    '''
    
    MANDATORY_FIELDS = ["RecordId", "CreateTime", "StorageSystem", 
                                  "StartTime", "EndTime", 
                                  "ResourceCapacityUsed"]

    # This list specifies the information that goes in the database.
    DB_FIELDS = ["RecordId", "CreateTime", "StorageSystem", "Site", "StorageShare", 
                       "StorageMedia", "StorageClass", "FileCount", "DirectoryPath",
                       "LocalUser", "LocalGroup", "UserIdentity", 
                       "Group", "StartTime", "EndTime", 
                       "ResourceCapacityUsed", "LogicalCapacityUsed",
                       "ResourceCapacityAllocated"]
    
    ALL_FIELDS = DB_FIELDS
    
    def __init__(self):
        '''Provide the necessary lists containing message information.'''
        
        Record.__init__(self)
        
        # Fields which are required by the message format.
        self._mandatory_fields = StorageRecord.MANDATORY_FIELDS
        
        # This list specifies the information that goes in the database.
        self._db_fields = StorageRecord.DB_FIELDS
        
        # Fields which are accepted but currently ignored.
        self._ignored_fields = []
        
        self._all_fields = self._db_fields
        self._datetime_fields = ["CreateTime", "StartTime", "EndTime"]
        # Fields which will have an integer stored in them
        self._int_fields = ["FileCount", "ResourceCapacityUsed", "LogicalCapacityUsed", "ResourceCapacityAllocated"]
        
    
    def get_apel_db_insert(self, apel_db, source):
        '''
        Returns record content as a tuple, appending the source of the record 
        (i.e. the sender's DN).  Also returns the appropriate stored procedure.
       
        We have to go back to the apel_db object to find the stored procedure.
        This is because only this object knows what type of record it is,
        and only the apel_db knows what the procedure details are. 
        '''
        
        values = self.get_db_tuple(self, source)
        
        
        return values
    
    
    def get_db_tuple(self, source):
        '''
        Last item in list is not usable for us.
        '''
        return Record.get_db_tuple(self, source)[:-1]
