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
   
   @author: Lisa Zangrando
'''
from apel.common import parse_timestamp, parse_time
from apel.db.records.event import EventRecord
from apel.parsers import Parser

import logging

log = logging.getLogger(__name__)

class SlurmParser(Parser):
    '''
    First implementation of the APEL parser for SLURM
    '''
    def __init__(self, site, machine_name, mpi):
        Parser.__init__(self, site, machine_name, mpi)
        if self._mpi:
            log.warn('SLURM MPI accounting may be incomplete.')
        log.info('Site: %s; batch system: %s' % (self.site_name, self.machine_name))
    
    def parse(self, line):
        '''
        Parses single line from accounting log file.
        '''
        # /usr/local/bin/sacct -P -n --format=JobID,JobName,User,Group,Start,End,Elapsed,CPUTimeRAW,Partition,NCPUS,NNodes,NodeList,MaxRSS,MaxVMSize -j $JOBID >> /var/log/apel/slurm_acc.20130311
        # 667|sleep|root|root|2013-03-11T12:47:37|2013-03-11T12:47:40|00:00:03|12|debug|4|2|cloud-vm-[03-04]|560K|100904K

        # log.info('line: %s' % (line));
        values = line.strip().split('|')

        rmem = 0
        if values[12]:
            # remove 'K' string from the end
            rmem = float(values[12][:-1])

        vmem = 0
        if values[13]:
            # remove 'K' string from the end
            vmem = float(values[13][:-1])

        mapping = {
                   'Site'            : lambda x: self.site_name,
                   'MachineName'     : lambda x: self.machine_name,
                   'Infrastructure'  : lambda x: "APEL-CREAM-SLURM",
                   'JobName'         : lambda x: x[0],
                   'LocalUserID'     : lambda x: x[2],
                   'LocalUserGroup'  : lambda x: x[3],
                   'WallDuration'    : lambda x: parse_time(x[6]),
                   'CpuDuration'     : lambda x: int(float(x[7])), 
                   # need to check timezones
                   'StartTime'       : lambda x: parse_timestamp(x[4]),
                   'StopTime'        : lambda x: parse_timestamp(x[5]),
                   'Queue'           : lambda x: x[9],
                   'MemoryReal'      : lambda x: int(rmem), # KB
                   'MemoryVirtual'   : lambda x: int(vmem), # KB
                   'Processors'      : lambda x: int(x[9]),
                   'NodeCount'       : lambda x: int(x[10])
        }

        rc = {}

        for key in mapping:
            rc[key] = mapping[key](values)

        assert rc['CpuDuration'] >= 0, 'Negative CpuDuration value'
        assert rc['WallDuration'] >= 0, 'Negative WallDuration value'

        record = EventRecord()
        record.set_all(rc)
        return record      



    