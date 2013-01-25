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
   
   @author: Konrad Jopek
'''

from apel.db.records.event import EventRecord
from apel.parsers import Parser

import logging

log = logging.getLogger(__name__)

class SGEParser(Parser):
    '''
    SGEParser parses files from SGE batch system.
    
    Please, refer to:
    http://jra1mw.cvs.cern.ch/cgi-bin/jra1mw.cgi/org.glite.apel.sge/src/org/glite/apel/sge/EventLogParser.java?revision=1.8&view=markup
    if you are interested how the old parser worked.
    
    Parser is based on this specification: http://manpages.ubuntu.com/manpages/lucid/man5/sge_accounting.5.html
    
    Example line from SGE:
    dteam:testce.test:dteam:dteam041:STDIN:43:sge:
    19:1200093286:1200093294:1200093295:0:0:1:0:0:0.000000:0:0:0:0:
    46206:0:0:0.000000:0:0:0:0:337:257:NONE:defaultdepartment:NONE:1
    :0:0.090000:0.000213:0.000000:-U dteam -q dteam:0.000000:NONE:30171136.000000
    
    Line was splitted, if you want to rejoin use empty string as a joiner.
    '''
    
    def __init__(self, site, machine_name, mpi):
        Parser.__init__(self, site, machine_name, mpi)
        if self._mpi:
            log.warn('SGE MPI accounting may be incomplete.')
        
    
    def parse(self, line):
        '''
        Parses single line from accounting log file.
        '''
        values = line.split(':')
        
        if self._mpi:
            procs = int(values[34])
        else:
            procs = 0
            
        mapping = {'Site'           : lambda x: self.site_name,
                  'JobName'         : lambda x: x[5],
                  'LocalUserID'     : lambda x: x[3],
                  'LocalUserGroup'  : lambda x: x[2],
                  'WallDuration'    : lambda x: int(x[13]),
                  # some kind of hack - int() can't parse strings like '1.000'
                  'CpuDuration'     : lambda x: int(float(x[36])), 
                  'StartTime'       : lambda x: int(x[9]),
                  'StopTime'        : lambda x: int(x[10]),
                  'Infrastructure'  : lambda x: "APEL-CREAM-SGE",
                  'MachineName'     : lambda x: self.machine_name,
                  'MemoryReal'      : lambda x: int(float(x[37])*1024*1024),  # is this correct?
                  'MemoryVirtual'   : lambda x: int(float(x[42])),
                  'Processors'      : lambda x: procs,
                  # Apparently can't get the number of WNs.
                  'NodeCount'       : lambda x: 0}
    
        record = EventRecord()
        data = {}
        
        for key in mapping:
            data[key] = mapping[key](values)
        
        assert data['CpuDuration'] >= 0, 'Negative CpuDuration value'
        assert data['WallDuration'] >= 0, 'Negative WallDuration value'
        assert data['StopTime'] > 0, 'Zero epoch time for field StopTime'
        
        
        record.set_all(data)
        
        return record