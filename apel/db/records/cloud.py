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

from apel.db.records import Record, InvalidRecordException
from datetime import datetime, timedelta


class CloudRecord(Record):
    '''
    Class to represent one cloud record. 
    
    It knows about the structure of the MySQL table and the message format.
    It stores its information in a dictionary self._record_content.  The keys 
    are in the same format as in the messages, and are case-sensitive.
    '''
    
    def __init__(self):
        '''Provide the necessary lists containing message information.'''
        
        Record.__init__(self)
        
        # Fields which are required by the message format.
        self._mandatory_fields = ["VMUUID", "SiteName"]
            
        # This list allows us to specify the order of lines when we construct records.
        self._msg_fields  = ["VMUUID", "SiteName", "MachineName", 
                             "LocalUserId", "LocalGroupId", "GlobalUserName", "FQAN",
                             "Status", "StartTime", "EndTime", "SuspendDuration", 
                              "WallDuration",
                             "CpuDuration", "CpuCount", "NetworkType", "NetworkInbound", 
                             "NetworkOutbound",
                             "Memory", "Disk", "StorageRecordId", "ImageId", "CloudType"]
        
        # This list specifies the information that goes in the database.
        self._db_fields = self._msg_fields
        self._all_fields = self._msg_fields
        
        self._ignored_fields = ["UpdateTime"]
        
        # Fields which will have an integer stored in them
        self._int_fields = [ "SuspendDuration", "WallDuration", "CpuDuration", "CpuCount", 
                            "NetworkInbound", 
                            "NetworkOutbound", "Memory", "Disk"]
        
        self._datetime_fields = ["StartTime", "EndTime"]
    
    
    def _check_fields(self):
        '''
        Add extra checks to those made in every record.
        '''
        # First, call the parent's version.
        Record._check_fields(self)
        
#        # Extract the relevant information from the user fqan.
#        # Keep the fqan itself as other methods in the class use it.
#        role, group, vo = self._parse_fqan(self._record_content['FQAN'])
#        # We can't / don't put NULL in the database, so we use 'None'
#        if role == None:
#            role = 'None'
#        if group == None:
#            group = 'None'
#        if vo == None:
#            vo = 'None'
#            
#        self._record_content['VORole'] = role
#        self._record_content['VOGroup'] = group
#        self._record_content['Group'] = vo
#        
#        
#        # Check the ScalingFactor.
#        slt = self._record_content['ServiceLevelType']
#        sl = self._record_content['ServiceLevel']
#        
#        (slt, sl) = self._check_factor(slt, sl)
#        self._record_content['ServiceLevelType'] = slt
#        self._record_content['ServiceLevel'] = sl
        
        # Check the values of StartTime and EndTime
#        self._check_start_end_times()

        
    def _check_start_end_times(self):
        '''Checks the values of StartTime and EndTime in _record_content.
        StartTime should be less than or equal to EndTime.
        Neither StartTime or EndTime should be zero.
        EndTime should not be in the future.
        
        This is merely factored out for simplicity.
        '''
        
        try:
            start = int(self._record_content['StartTime'])
            end = int(self._record_content['EndTime'])
            if end < start:
                raise InvalidRecordException("EndTime is before StartTime.")
            
            if start == 0 or end == 0:
                raise InvalidRecordException("Epoch times StartTime and EndTime mustn't be 0.")
            
            now = datetime.now()
            # add two days to prevent timezone problems
            tomorrow = now + timedelta(2)
            if datetime.fromtimestamp(end) > tomorrow:
                raise InvalidRecordException("Epoch time " + str(end) + " is in the future.")
            
        except ValueError:
            raise InvalidRecordException("Cannot parse an integer from StartTime or EndTime.")
        
        