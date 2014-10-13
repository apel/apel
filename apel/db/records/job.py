'''
   Copyright (C) 2012 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
    @author Will Rogers, Konrad Jopek
'''

from apel.db.records import Record, InvalidRecordException
from datetime import datetime, timedelta
from xml.dom.minidom import Document
from apel.common import parse_fqan
import time

WITHHELD_DN = 'withheld'


class JobRecord(Record):
    '''
    Class to represent one job record. 
    
    It knows about the structure of the MySQL table and the message format.
    It stores its information in a dictionary self._record_content.  The keys 
    are in the same format as in the messages, and are case-sensitive.
    '''
    
    def __init__(self):
        '''Provide the necessary lists containing message information.'''
        
        Record.__init__(self)
        
        # Fields which are required by the message format.
        self._mandatory_fields = ["Site", "LocalJobId", 
                                  "WallDuration", "CpuDuration", 
                                  "StartTime", "EndTime"]
            
        # This list allows us to specify the order of lines when we construct records.
        self._msg_fields  = ["Site", "SubmitHost", "MachineName", "Queue", "LocalJobId", "LocalUserId", 
                       "GlobalUserName", "FQAN", "VO", "VOGroup", "VORole", "WallDuration", 
                       "CpuDuration", "Processors", "NodeCount", "StartTime", "EndTime", "InfrastructureDescription", "InfrastructureType",
                       "MemoryReal", "MemoryVirtual", "ServiceLevelType", 
                       "ServiceLevel"]
        
        # This list specifies the information that goes in the database.
        self._db_fields = ["Site", "SubmitHost", "MachineName", "Queue", "LocalJobId", "LocalUserId", 
                       "GlobalUserName", "FQAN", "VO", 
                       "VOGroup", "VORole", "WallDuration", "CpuDuration", "Processors", 
                       "NodeCount", "StartTime", "EndTime", "InfrastructureDescription", "InfrastructureType", "MemoryReal",
                       "MemoryVirtual", "ServiceLevelType", "ServiceLevel"]
        
        # Not used in the message format, but required by the database.
        # self._fqan_fields = ["VO", "VOGroup", "VORole"]
        
        # Fields which are accepted but currently ignored.
        self._ignored_fields = ["SubmitHostType", "UpdateTime"]
        
        self._all_fields = self._msg_fields + self._ignored_fields
        
        # Fields which will have an integer stored in them
        self._int_fields = ["WallDuration", "CpuDuration", "Processors", 
                            "NodeCount", "MemoryReal", 
                            "MemoryVirtual"]
        
        self._float_fields = ["ServiceLevel"]
        
        self._datetime_fields = ["StartTime", "EndTime"]
        
        # Acceptable values for the ServiceLevelType field, not case-sensitive
        self._valid_slts = ["si2k", "hepspec"]
    
    
    def _check_fields(self):
        '''
        Add extra checks to those made in every record.
        '''
        # First, call the parent's version.
        Record._check_fields(self)
        
        # Extract the relevant information from the user fqan.
        # Keep the fqan itself as other methods in the class use it.
        if self._record_content['FQAN'] not in ('None', None):
            
            role, group, vo = parse_fqan(self._record_content['FQAN'])
            # We can't / don't put NULL in the database, so we use 'None'
            if role == None:
                role = 'None'
            if group == None:
                group = 'None'
            if vo == None:
                vo = 'None'
            
            self._record_content['VORole'] = role
            self._record_content['VOGroup'] = group
            # Confusing terminology from the CAR
            self._record_content['VO'] = vo
        
        
        # Check the ScalingFactor.
        slt = self._record_content['ServiceLevelType']
        sl = self._record_content['ServiceLevel']
        
        (slt, sl) = self._check_factor(slt, sl)
        self._record_content['ServiceLevelType'] = slt
        self._record_content['ServiceLevel'] = sl
        
        # Check the values of StartTime and EndTime
        self._check_start_end_times()

        
    def _check_start_end_times(self):
        '''Checks the values of StartTime and EndTime in _record_content.
        StartTime should be less than or equal to EndTime.
        Neither StartTime or EndTime should be zero.
        EndTime should not be in the future.
        
        This is merely factored out for simplicity.
        '''
        try:
            start = self._record_content['StartTime']
            end = self._record_content['EndTime']
            if end < start:
                raise InvalidRecordException("EndTime is before StartTime.")
               
            now = datetime.now()
            # add two days to prevent timezone problems
            tomorrow = now + timedelta(2)
            if end > tomorrow:
                raise InvalidRecordException("Epoch time " + str(end) + " is in the future.")
            
        except ValueError:
            raise InvalidRecordException("Cannot parse an integer from StartTime or EndTime.")
        
        
    def _check_factor(self, sfu, sf):
        '''
        Check for the validity of the ScalingFactorUnit and ScalingFactor fields.
        We accept neither field included or both.  If only one of the fields is 
        included, it doesn't really make sense so we reject it.
    
        We expect that all null values have been converted to the string 'None'.
        '''
        if sf == 'None':
            if sfu != 'None':
                raise InvalidRecordException('Unit but not value supplied for ScalingFactor.')
            else:
                sfu = 'custom'
                sf = 1
        else: # sf is present
            if sfu == 'None':
                raise InvalidRecordException('Unit but not value supplied for ScalingFactor.')
            else:
                if sfu.lower() not in self._valid_slts:
                    raise InvalidRecordException('ScalingFactorUnit ' + sfu + 
                                ' not valid.')    
                    
        return (sfu, sf)
    
    def get_ur(self, withhold_dns=False):
        '''
        Returns the JobRecord in CAR format. See
        https://twiki.cern.ch/twiki/bin/view/EMI/ComputeAccounting
        
        Namespace information is written only once per record, by dbunloader.
        '''
        record_id = self.get_field('MachineName') + ' ' + self.get_field('LocalJobId') + ' ' + str(self.get_field('EndTime'))
        
        # Create the document directly
        doc = Document()
        ur = doc.createElement('urf:UsageRecord')
        
        rec_id = doc.createElement('urf:RecordIdentity')
        rec_id.setAttribute('urf:createTime', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        rec_id.setAttribute('urf:recordId', record_id)
        ur.appendChild(rec_id)
        
        job_id = doc.createElement('urf:JobIdentity')
        local_job_id = doc.createElement('urf:LocalJobId')
        text = doc.createTextNode(self.get_field('LocalJobId'))
        local_job_id.appendChild(text)
        job_id.appendChild(local_job_id)
        ur.appendChild(job_id)
        
        user_id = doc.createElement('urf:UserIdentity')

        if self.get_field('GlobalUserName') is not None:
            if withhold_dns:
                dn = WITHHELD_DN
            else:
                dn = self.get_field('GlobalUserName')
            global_user_name = doc.createElement('urf:GlobalUserName')
            global_user_name.appendChild(doc.createTextNode(dn))
            global_user_name.setAttribute('urf:type', 'opensslCompat')
            user_id.appendChild(global_user_name)
            
        if self.get_field('VO') is not None:
            group = doc.createElement('urf:Group')
            group.appendChild(doc.createTextNode(self.get_field('VO')))
            user_id.appendChild(group)
            
        if self.get_field('FQAN') is not None:
            fqan = doc.createElement('urf:GroupAttribute')
            fqan.setAttribute('urf:type', 'FQAN')
            fqan.appendChild(doc.createTextNode(self.get_field('FQAN')))
            user_id.appendChild(fqan)
            
        if self.get_field('VOGroup') is not None:
            vogroup = doc.createElement('urf:GroupAttribute')
            vogroup.setAttribute('urf:type', 'vo-group')
            vogroup.appendChild(doc.createTextNode(self.get_field('VOGroup')))
            user_id.appendChild(vogroup)
            
        if self.get_field('VORole') is not None:
            vorole = doc.createElement('urf:GroupAttribute')
            vorole.setAttribute('urf:type', 'vo-role')
            vorole.appendChild(doc.createTextNode(self.get_field('VORole')))
            user_id.appendChild(vorole)
        
        if self.get_field('LocalUserId') is not None:
            local_user_id = doc.createElement('urf:LocalUserId')
            local_user_id.appendChild(doc.createTextNode(self.get_field('LocalUserId')))
            user_id.appendChild(local_user_id)
            
        ur.appendChild(user_id)
        
        status = doc.createElement('urf:Status')
        status.appendChild(doc.createTextNode('completed'))
        ur.appendChild(status)

        infra = doc.createElement('urf:Infrastructure')
        infra.setAttribute('urf:type', self.get_field('InfrastructureType'))
        ur.appendChild(infra)

        wall = doc.createElement('urf:WallDuration')
        wall.appendChild(doc.createTextNode('PT'+str(self.get_field('WallDuration'))+'S'))
        ur.appendChild(wall)
        
        cpu = doc.createElement('urf:CpuDuration')
        cpu.setAttribute('urf:usageType', 'all')
        cpu.appendChild(doc.createTextNode('PT'+str(self.get_field('CpuDuration'))+'S'))
        ur.appendChild(cpu)
        
        service_level = doc.createElement('urf:ServiceLevel')
        service_level.setAttribute('urf:type', self.get_field('ServiceLevelType'))
        service_level.appendChild(doc.createTextNode(str(self.get_field('ServiceLevel'))))
        ur.appendChild(service_level)

        if self.get_field('MemoryReal') > 0:
            pmem = doc.createElement('urf:Memory')
            pmem.setAttribute('urf:type', 'Physical')
            pmem.setAttribute('urf:storageUnit', 'KB')
            pmem.appendChild(doc.createTextNode(str(self.get_field('MemoryReal'))))
            ur.appendChild(pmem)
        
        if self.get_field('MemoryVirtual') > 0:
            vmem = doc.createElement('urf:Memory')
            vmem.setAttribute('urf:type', 'Shared')
            vmem.setAttribute('urf:storageUnit', 'KB')
            vmem.appendChild(doc.createTextNode(str(self.get_field('MemoryVirtual'))))
            ur.appendChild(vmem)
        
        if self.get_field('NodeCount') > 0:
            ncount = doc.createElement('urf:NodeCount')
            ncount.appendChild(doc.createTextNode(str(self.get_field('NodeCount'))))
            ur.appendChild(ncount)
        
        if self.get_field('Processors') > 0:
            procs = doc.createElement('urf:Processors')
            procs.appendChild(doc.createTextNode(str(self.get_field('Processors'))))
            ur.appendChild(procs)
                           
        end = doc.createElement('urf:EndTime')
        end_text = time.strftime('%Y-%m-%dT%H:%M:%SZ', self.get_field('EndTime').timetuple())
        end.appendChild(doc.createTextNode(end_text))
        ur.appendChild(end)
        
        start = doc.createElement('urf:StartTime')
        start_text = time.strftime('%Y-%m-%dT%H:%M:%SZ', self.get_field('StartTime').timetuple())
        start.appendChild(doc.createTextNode(start_text))
        ur.appendChild(start)
        
        machine = doc.createElement('urf:MachineName')
        machine.appendChild(doc.createTextNode(self.get_field('MachineName')))
        ur.appendChild(machine)
        
        if self.get_field('SubmitHost') is not None:
            subhost = doc.createElement('urf:SubmitHost')
            subhost.appendChild(doc.createTextNode(self.get_field('SubmitHost')))
            ur.appendChild(subhost)
        
        queue = doc.createElement('urf:Queue')
        queue.appendChild(doc.createTextNode(str(self.get_field('Queue'))))
        ur.appendChild(queue)
            
        site = doc.createElement('urf:Site')
        site.appendChild(doc.createTextNode(self.get_field('Site')))
        ur.appendChild(site)
        
        doc.appendChild(ur)
        # We don't want the XML declaration, because the whole XML
        # document will be assembled by another part of the program.
        return doc.documentElement.toxml()

