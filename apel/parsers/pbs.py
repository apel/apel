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
   
@author: Konrad Jopek, Will Rogers
'''

from apel.db.records.event import EventRecord
from apel.parsers import Parser

import logging

logger = logging.getLogger(__name__)

class PBSParser(Parser):
    '''
    Parser for PBS accounting log files.
    
    Example line from PBS accounting looks like:
    10/02/2011 06:41:44;E;21048463.lcgbatch01.gridpp.rl.ac.uk;user=patls009 group=prodatls jobname=cre09_443343882 queue=grid4000M
    ctime=1317509574 qtime=1317509574 etime=1317509574 start=1317509945 owner=patls009@lcgce09.gridpp.rl.ac.uk
    exec_host=lcg1277.gridpp.rl.ac.uk/5 Resource_List.cput=96:00:00 Resource_List.neednodes=lcg1277.gridpp.rl.ac.uk
    Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.pmem=4000mb Resource_List.walltime=96:00:00 session=20374
    end=1317534104 Exit_status=0 resources_used.cput=18:15:24 resources_used.mem=2031040kb resources_used.vmem=3335528kb resources_used.walltime=19:23:4
    
    Line was split, if you want to rejoin use ' ' as a joiner.
    '''
    def parse(self, line):
        '''
        Parses single line from PBS log file.
        
        Please notice, that we use two different separators: ';' and ' '
        '''
        data = {}
        _, status, jobName, rest = line.split(';')
        
        if self.machineName == '':
            self.machineName = jobName.split('.',1)[1]
        
        # we accept only 'E' status
        # be careful!: this parse can return None, and this is _valid_ situation
        if status != 'E':
            return None
        
        mapping = {'Site'           : lambda x: self.siteName, # ?
                   'JobName'        : lambda x: jobName, 
                   'LocalUserID'    : lambda x: x['user'],
                   'LocalUserGroup' : lambda x: x['group'],
                   'WallDuration'   : lambda x: self._parse_time(x['resources_used.walltime']),
                   'CpuDuration'    : lambda x: self._parse_time(x['resources_used.cput']),
                   'StartTime'      : lambda x: int(x['start']),
                   'StopTime'       : lambda x: int(x['end']),
                   'Infrastructure' : lambda x: "APEL-CREAM-PBS",
                   'MachineName'    : lambda x: self.machineName,
                   # remove 'kb' string from the end
                   'MemoryReal'     : lambda x: int(x['resources_used.mem'][:-2]),
                   'MemoryVirtual'  : lambda x: int(x['resources_used.vmem'][:-2]),
#                   'Processors'     : lambda x: self._parse_mpi(x)[0],
                   'Processors'     : lambda x: 1,
#                   'NodeCount'      : lambda x: self._parse_mpi(x)[1]}
                   'NodeCount'      : lambda x: 1}
    
        for item in rest.split():
            key, value = item.split('=', 1)
            data[key] = value
            
        rc = {}
                
        for key in mapping:
            rc[key] = mapping[key](data)
        
        assert rc['CpuDuration'] >= 0, 'Negative CpuDuration value'
        assert rc['WallDuration'] >= 0, 'Negative WallDuration value'
        
        record = EventRecord()
        record.set_all(rc)
        return record

    def _parse_mpi(self, rec_dict):
        '''
        Return (nodes, total-cores) given a dict from a PBS record.
        
        This checks twice which is for testing purposes.
        '''
        # exec_host is of the form <hostname>/core_no[+<hostname>/core_no]
        # e.g. wn1.rl.ac.uk/0+wn1.rl.ac.uk/1+wn2.rl.ac.uk/0+wn2.rl.ac.uk/1
        core_info = rec_dict['exec_host'].split('+')
        # remove /core_no and get the list of hostnames
        hostnames = [ x.split('/')[0] for x in core_info ]
        # get number of unique hostnames
        nnodes = len(set(hostnames))
        # total number of core details
        ncores = len(core_info)
        
        # Check with the second MPI field
        try:
            # nodes is of the form x:ppn=y; ppn is processors per node
            node_details = rec_dict['Resource_List.nodes']
            nnodes2, ppn = node_details.split(':ppn=')
            ncores2 = nnodes2 * ppn
        except KeyError:  # Not present for non-MPI jobs
            nnodes2 = 1
            ncores2 = 1
        
        assert (nnodes, ncores) == (nnodes2, ncores2), "Inconsistent MPI values from PBS."
                
        return nnodes, ncores

    def _parse_time(self, time):
        '''
        Return seconds from times of the form xx:yy:zz.
        '''
        hours, minutes, seconds = time.split(':')
        return 3600*int(hours) + 60*int(minutes) + int(seconds)