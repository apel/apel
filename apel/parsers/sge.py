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
import subprocess
import xml.dom.minidom

log = logging.getLogger(__name__)

class MultiplierError(Exception):
    pass

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
            log.warning('SGE MPI accounting may be incomplete.')
        self.multipliers = self._load_multipliers()

        # This should be set to True in parser.py for versions of Grid Engine
        # using millisecond timestamps (i.e. Univa Grid Engine 8.2.0+).
        self._ms_timestamps = False

    def set_ms_timestamps(self, use_ms):
        """
        Set _ms_timestamps to True or False.

        This decides if timestamps will be treated as being in milliseconds (in
        which case they'll need to be converted back to seconds).
        """
        if use_ms:
            log.info('Will treat GE timestamps as being in milliseconds.')
        self._ms_timestamps = use_ms

    def _load_multipliers(self):
        '''
        Returns a dictionary {hostname: {cputmult: <value>, wallmult: <value>}}.

        Hosts with no cputmult/wallmult definitions are ignored.
        '''
        d = {}
        try:
            p = subprocess.Popen(["qhost", "-F", "-xml"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                raise MultiplierError(err)
        except (OSError, MultiplierError):
            log.warning("Unable to retrieve multipliers from qhost. Will default "
                        "to '1.0'.")
            return {}

        xml_str = xml.dom.minidom.parseString(out)
        hosts = xml_str.getElementsByTagName("host")

        for host in hosts:
            host_name = host.getAttribute("name")
            for resource in host.getElementsByTagName("resourcevalue"):
                resource_name = resource.getAttribute("name")
                if resource_name in ["cputmult", "wallmult"]:
                    try:
                        resource_value = float(resource.childNodes[0].data)
                        d[host_name][resource_name] = resource_value
                    except ValueError:
                        pass # float conversion
                    except KeyError:
                        d[host_name] = {resource_name: resource_value}
        return d

    def _get_cpu_multiplier(self, node):
        '''
        Returns a given node's cputmult complex. Defaults to 1.
        '''
        return self.multipliers.get(node, self.multipliers).get("cputmult", 1.0)

    def _get_wall_multiplier(self, node):
        '''
        Returns a given node's wallmult complex. Defaults to 1.
        '''
        return self.multipliers.get(node, self.multipliers).get("wallmult", 1.0)

    def parse(self, line):
        '''
        Parses single line from accounting log file.
        '''
        values = line.split(':')

        if self._mpi:
            procs = int(values[34])
        else:
            procs = 0

        # If a version of GE that uses millisecond timestamps is being used then
        # set the divisor to convert back to seconds.
        if self._ms_timestamps:
            divisor = 1000
        else:
            divisor = 1

        mapping = {'Site'           : lambda x: self.site_name,
                  'JobName'         : lambda x: x[5],
                  'LocalUserID'     : lambda x: x[3],
                  'LocalUserGroup'  : lambda x: x[2],
                  # int() can't parse strings like '1.000'
                  'WallDuration'    : lambda x: int(round(float(x[13]))*self._get_wall_multiplier(x[1])),
                  'CpuDuration'     : lambda x: int(round(float(x[36]))*self._get_cpu_multiplier(x[1])),
                  'StartTime'       : lambda x: int(round(float(x[9])/divisor)),
                  'StopTime'        : lambda x: int(round(float(x[10])/divisor)),
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
