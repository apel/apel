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

from datetime import datetime
import time
from apel.db.records import Record
from xml.dom.minidom import Document

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
                       "Group", "SubGroup", "Role", "StartTime", "EndTime",
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

    def get_apel_db_insert(self, source=None):
        '''
        Returns record content as a tuple, appending the source of the record 
        (i.e. the sender's DN).  Also returns the appropriate stored procedure.
       
        We have to go back to the apel_db object to find the stored procedure.
        This is because only this object knows what type of record it is,
        and only the apel_db knows what the procedure details are. 
        '''

        values = self.get_db_tuple(source)

        return values

    def get_db_tuple(self, source=None):
        """
        Return record contents as tuple ignoring the 'source' keyword argument.

        The source (DN of the sender) isn't used in this record type currently.
        """
        return Record.get_db_tuple(self)

    def get_ur(self, withhold_dns=False):
        '''
        Returns the StorageRecord in StAR format. See
        http://cds.cern.ch/record/1452920/

        Namespace information is written only once per record, by dbunloader.
        '''
        del withhold_dns  # Unused

        doc = Document()
        ur = doc.createElement('sr:StorageUsageRecord')

        record_id = self.get_field('RecordId')
        rec_id = doc.createElement('sr:RecordIdentity')
        rec_id.setAttribute('sr:createTime', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        rec_id.setAttribute('sr:recordId', record_id)
        ur.appendChild(rec_id)

        storage_system = self.get_field('StorageSystem')
        s_system = doc.createElement('sr:StorageSystem')
        s_system.appendChild(doc.createTextNode(storage_system))
        ur.appendChild(s_system)

        if self.get_field('Site') is not None:
            site = self.get_field('Site')
            s_site = doc.createElement('sr:Site')
            s_site.appendChild(doc.createTextNode(site))
            ur.appendChild(s_site)

        if self.get_field('StorageShare') is not None:
            storage_share = self.get_field('StorageShare')
            s_share = doc.createElement('sr:StorageShare')
            s_share.appendChild(doc.createTextNode(storage_share))
            ur.appendChild(s_share)

        if self.get_field('StorageMedia') is not None:
            storage_media = self.get_field('StorageMedia')
            s_media = doc.createElement('sr:StorageMedia')
            s_media.appendChild(doc.createTextNode(storage_media))
            ur.appendChild(s_media)

        if self.get_field('StorageClass') is not None:
            storage_class = self.get_field('StorageClass')
            s_class = doc.createElement('sr:StorageClass')
            s_class.appendChild(doc.createTextNode(storage_class))
            ur.appendChild(s_class)

        if self.get_field('FileCount') is not None:
            file_count = self.get_field('FileCount')
            f_count = doc.createElement('sr:FileCount')
            f_count.appendChild(doc.createTextNode(str(file_count)))
            ur.appendChild(f_count)

        if self.get_field('DirectoryPath') is not None:
            directory_path = self.get_field('DirectoryPath')
            d_path = doc.createElement('sr:DirectoryPath')
            d_path.appendChild(doc.createTextNode(directory_path))
            ur.appendChild(d_path)

        # Create Subject Identity Block
        s_identity = doc.createElement('sr:SubjectIdentity')

        if self.get_field('LocalUser') is not None:
            local_user = self.get_field('LocalUser')
            l_user = doc.createElement('sr:LocalUser')
            l_user.appendChild(doc.createTextNode(local_user))
            s_identity.appendChild(l_user)

        if self.get_field('LocalGroup') is not None:
            local_group = self.get_field('LocalGroup')
            l_group = doc.createElement('sr:LocalGroup')
            l_group.appendChild(doc.createTextNode(local_group))
            s_identity.appendChild(l_group)

        if self.get_field('UserIdentity') is not None:
            user_identity = self.get_field('UserIdentity')
            u_identity = doc.createElement('sr:UserIdentity')
            u_identity.appendChild(doc.createTextNode(user_identity))
            s_identity.appendChild(u_identity)

        if self.get_field('Group') is not None:
            group_field = self.get_field('Group')
            group_node = doc.createElement('sr:Group')
            group_node.appendChild(doc.createTextNode(group_field))
            s_identity.appendChild(group_node)

        if self.get_field('SubGroup') is not None:
            sub_attr = doc.createElement('sr:GroupAttribute')
            sub_attr.setAttribute('sr:attributeType', 'subgroup')
            sub_attr.appendChild(doc.createTextNode(self.get_field('SubGroup')))
            s_identity.appendChild(sub_attr)

        if self.get_field('Role') is not None:
            role_attr = doc.createElement('sr:GroupAttribute')
            role_attr.setAttribute('sr:attributeType', 'role')
            role_attr.appendChild(doc.createTextNode(self.get_field('Role')))
            s_identity.appendChild(role_attr)

        # Append Subject Identity Block
        ur.appendChild(s_identity)

        start_text = time.strftime('%Y-%m-%dT%H:%M:%SZ', self.get_field('StartTime').timetuple())
        s_time = doc.createElement('sr:StartTime')
        s_time.appendChild(doc.createTextNode(start_text))
        ur.appendChild(s_time)

        end_text = time.strftime('%Y-%m-%dT%H:%M:%SZ', self.get_field('EndTime').timetuple())
        e_time = doc.createElement('sr:EndTime')
        e_time.appendChild(doc.createTextNode(end_text))
        ur.appendChild(e_time)

        resource_capacity_used = self.get_field('ResourceCapacityUsed')
        r_capacity_used = doc.createElement('sr:ResourceCapacityUsed')
        r_capacity_used.appendChild(doc.createTextNode(str(resource_capacity_used)))
        ur.appendChild(r_capacity_used)

        if self.get_field('LogicalCapacityUsed') is not None:
            logical_capacity_used = self.get_field('LogicalCapacityUsed')
            l_capacity_used = doc.createElement('sr:LogicalCapacityUsed')
            l_capacity_used.appendChild(doc.createTextNode(str(logical_capacity_used)))
            ur.appendChild(l_capacity_used)

        if self.get_field('ResourceCapacityAllocated') is not None:
            resource_capacity_allocated = self.get_field('ResourceCapacityAllocated')
            r_capacity_allocated = doc.createElement('sr:ResourceCapacityAllocated')
            r_capacity_allocated.appendChild(doc.createTextNode(str(resource_capacity_allocated)))
            ur.appendChild(r_capacity_allocated)

        doc.appendChild(ur)
        return doc.documentElement.toxml()
