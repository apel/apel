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

'''

from future.builtins import zip

from apel.db.records.event import EventRecord
from apel.parsers import Parser
from apel.common import parse_time

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
        unused_date, status, jobName, rest = line.split(';')

        # we accept only 'E' status
        # be careful!: this parse can return None, and this is _valid_ situation
        if status != 'E':
            return None

        for item in rest.split():
            key, value = item.split('=', 1)
            data[key] = value

        if self._mpi:
            nodes, cores = _parse_mpi(data['exec_host'])
        else:
            nodes, cores = 0, 0

        wall_function = parse_time
        cput_function = parse_time

        # Different versions Torque use different time formats for for cput and
        # walltime (either seconds or hh:mm:ss) so check for that here.
        if ':' not in data['resources_used.walltime']:
            # Although the duration doesn't need converting if it's already in
            # seconds, this needs to be a function to work with later code.
            wall_function = lambda y: y
        if ':' not in data['resources_used.cput']:
            cput_function = lambda y: y

        # map each field to functions which will extract them
        mapping = {'Site'          : lambda x: self.site_name,
                   'JobName'       : lambda x: jobName,
                   'LocalUserID'   : lambda x: x['user'],
                   'LocalUserGroup': lambda x: x['group'],
                   'WallDuration'  : lambda x: wall_function(x['resources_used.walltime']),
                   'CpuDuration'   : lambda x: cput_function(x['resources_used.cput']),
                   'StartTime'     : lambda x: int(x['start']),
                   'StopTime'      : lambda x: int(x['end']),
                   'Infrastructure': lambda x: "APEL-CREAM-PBS",
                   'MachineName'   : lambda x: self.machine_name,
                   # remove 'kb' string from the end
                   'MemoryReal'    : lambda x: int(x['resources_used.mem'][:-2]),
                   'MemoryVirtual' : lambda x: int(x['resources_used.vmem'][:-2]),
                   'NodeCount'     : lambda x: nodes,
                   'Processors'    : lambda x: cores
                   }

        rc = {}

        for key in mapping:
            rc[key] = mapping[key](data)

        # Input checking
        if int(rc['CpuDuration']) < 0:
            raise ValueError("Negative 'cput' value")
        if int(rc['WallDuration']) < 0:
            raise ValueError("Negative 'walltime' value")
        if rc['StopTime'] < rc['StartTime']:
            raise ValueError("'end' time less than 'start' time")

        record = EventRecord()
        record.set_all(rc)
        return record


def _parse_mpi(exec_host):
    """
    Return (nodes, total-cores) given a dict from a PBS record.
    """
    # exec_host is of the form <hostname>/core_no[+<hostname>/core_no]
    # e.g. wn1.rl.ac.uk/0+wn1.rl.ac.uk/1+wn2.rl.ac.uk/0+wn2.rl.ac.uk/1
    # The 'exec_host' in Torque >= 5.1.0 reads like 'b391/0-1,5,11'

    core_info = exec_host.split('+')
    # Split hostname and core_no into seperate lists.
    hostnames, core_no = zip(*[x.split('/') for x in core_info])

    # Split any comma separated fields into a flat list.
    core_no = [core for cores in core_no for core in cores.split(',')]
    ncores = 0
    for no in core_no:
        if '-' in no:
            # Calculate the number of cores in the closed set.
            ncores += int(no.split('-')[1]) - int(no.split('-')[0]) + 1
        else:
            ncores += 1

    # get number of unique hostnames
    nnodes = len(set(hostnames))

    return nnodes, ncores
