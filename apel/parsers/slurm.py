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

   @author: Lisa Zangrando, Will Rogers
'''
from apel.common import parse_time
from apel.db.records.event import EventRecord
from apel.parsers import Parser

import time
import datetime
import logging

log = logging.getLogger(__name__)


def parse_local_timestamp(datetime_string):
    '''
    Parse a timestamp without TZ information, assuming that it is
    referring to system time.  Return a datetime converted to UTC.

    SLURM timestamps are in the form '2013-06-01T10:00:00'.
    '''
    unix_time = time.mktime(time.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S"))
    return datetime.datetime.utcfromtimestamp(unix_time)


class SlurmParser(Parser):
    '''
    First implementation of the APEL parser for SLURM
    '''
    def __init__(self, site, machine_name, mpi):
        Parser.__init__(self, site, machine_name, mpi)
        log.info('Site: %s; batch system: %s' % (self.site_name, self.machine_name))

    def parse(self, line):
        '''
        Parses single line from accounting log file.
        '''
        # /usr/local/bin/sacct -P -n --format=JobID,JobName,User,Group,Start,End,Elapsed,CPUTimeRAW,Partition,NCPUS,NNodes,NodeList,MaxRSS,MaxVMSize,State -j $JOBID >> /var/log/apel/slurm_acc.20130311
        # 1007|cream_612883006|dteam005|dteam|2013-03-27T17:13:41|2013-03-27T17:13:44|00:00:03|3|prod|1|1|cert-40|||COMPLETED

        # log.info('line: %s' % (line));
        values = line.strip().split('|')

        if values[14] != 'COMPLETED':
            return None

        rmem = self._normalise_memory(values[12])

        vmem = self._normalise_memory(values[13])

        mapping = {'Site'            : lambda x: self.site_name,
                   'MachineName'     : lambda x: self.machine_name,
                   'Infrastructure'  : lambda x: "APEL-CREAM-SLURM",
                   'JobName'         : lambda x: x[0],
                   'LocalUserID'     : lambda x: x[2],
                   'LocalUserGroup'  : lambda x: x[3],
                   'WallDuration'    : lambda x: parse_time(x[6]),
                   'CpuDuration'     : lambda x: int(x[7]), 
                   # SLURM gives timestamps which are in system time.
                   'StartTime'       : lambda x: parse_local_timestamp(x[4]),
                   'StopTime'        : lambda x: parse_local_timestamp(x[5]),
                   'Queue'           : lambda x: x[9],
                   'MemoryReal'      : lambda x: rmem,  # KB
                   'MemoryVirtual'   : lambda x: vmem,  # KB
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

    def _normalise_memory(self, mem):
        """Strip unit prefix and return memory size as int in KB."""
        if mem:
            if mem[-1:] == 'K':
                mem = int(mem[:-1])
            elif mem[-1:] == 'M':
                mem = int(float(mem[:-1])*1024)
            elif mem[-1:] == 'G':
                mem = int(float(mem[:-1])*1024**2)
            elif mem[-1:] == 'T':
                mem = int(float(mem[:-1])*1024**3)
            elif mem[-1:] == 'P':
                mem = int(float(mem[:-1])*1024**4)
            else:
                raise ValueError("Unsupported unit prefix '%s'. Expected one of [KMGTP]." % mem[-1:])
        else:
            mem = None
        return mem
