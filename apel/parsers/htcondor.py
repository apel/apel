'''
   Copyright 2014 The Science and Technology Facilities Council

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   @author: Pavel Demin
'''

import logging

from apel.db.records.event import EventRecord
from apel.parsers import Parser

log = logging.getLogger(__name__)

class HTCondorParser(Parser):
    '''
    First implementation of the APEL parser for HTCondor
    '''
    def __init__(self, site, machine_name, mpi):
        Parser.__init__(self, site, machine_name, mpi)
        log.info('Site: %s; batch system: %s' % (self.site_name, self.machine_name))

    def parse(self, line):
        '''
        Parses single line from accounting log file.
        '''
        # Put here command that extracts log line

        data = {}

        for item in line.split("; ") :
            key, value = item.split('=', 1)
            data[key] = value

        mapping = {'Site' : lambda x: self.site_name,
            'JobName'       : lambda x: x['clusterid'] + "_" + self.machine_name,
            'LocalUserID'   : lambda x: x['owner'],
            'LocalUserGroup': lambda x: x['VO'],
            'WallDuration'  : lambda x: float(x['cputmult'])*
              (float(x['walltime+suspensiontime'])-float(x['suspensiontime'])),
            'CpuDuration'   : lambda x: float(x['cputmult'])*(float(x['cputime'])+float(x['syscputime'])),
            'StartTime'     : lambda x: int(x['startdate']),
            'StopTime'      : lambda x: int(x['enddate']),
            'Infrastructure': lambda x: "APEL-HTCONDOR",
            'MachineName'   : lambda x: self.machine_name,
            # remove 'kb' string from the end
            'MemoryReal'    : lambda x: int(x['pmem']),
            'MemoryVirtual' : lambda x: int(x['vmem']),
            'NodeCount'     : lambda x: 1,
            'Processors'    : lambda x: int(x['request_cpus'])
        }

        rc = {}

        for key in mapping:
            rc[key] = mapping[key](data)

        record = EventRecord()
        record.set_all(rc)
        return record
