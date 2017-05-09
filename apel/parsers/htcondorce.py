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

A parser for HTCondorCE record file.

    @author: Jordi Casals modified Blahd from Konrad Jopek
'''

from apel.db.records.htcondorce import HTCondorCERecord
from apel.common import valid_from, valid_until, parse_timestamp
from apel.common.parsing_utils import parse_fqan
from apel.parsers import Parser

import re

class HTCondorCEParser(Parser):
    '''
    HTCondorCE parses accounting files from HTCondorCE system.
    '''
    def parse(self, line):
        '''
        Parses single line from accounting log file.

        Example line of accounting log file:
        "timestamp=2017-02-01 00:03:49; clusterid=381620; CE_JobId=396933.0; owner=lhpilot007; VO=lhcb; 
        userDN=/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=romanov/CN=427293/CN=Vladimir Romanovskiy; 
        userFQAN=/lhcb/Role=pilot/Capability=NULL; exec_host=slot1_1@td518.pic.es; request_cpus=1; 
        cputime=3466.000000; syscputime=259.000000; jobduration=4821.575215; walltime+suspensiontime=4823.000000; 
        suspensiontime=0.000000; cputmult=1.1864; pmem=1684532; vmem=944; disk=38543; ExitCode=0; 
        ExitSignal=undefined; LastStatus=4; JobStatus=3; startdate=1485899007; enddate=1485903829"

        Line was split, if you want to rejoin use ' ' as a joiner.
        '''
        data = {}
        rc = {}
        LINE_EXPR = re.compile(r'\"|\"_\"')
        # This is basically for the FQAN
        parts = [x.split('=',1) for x in [y for y in LINE_EXPR.split(line) if len(y) > 1]]

        for item in line.split("; ") :
            key, value = item.split('=', 1)
            data[key] = value

        mapping = {
            'TimeStamp'      : lambda x: 'T'.join(x['timestamp'].split()) + 'Z',
            'GlobalUserName' : lambda x: x['userDN'],
            'FQAN'           : lambda x: x['userFQAN'],
            'VO'             : lambda x: x['VO'],
            'VOGroup'        : lambda x: x['userFQAN'].split("/")[1],
            'VORole'         : lambda x: x['userFQAN'].split("/")[2],
            'CE'             : lambda x: self.machine_name + ":" + "9619" + "/" + self.machine_name + "-" + "condor",
            'GlobalJobId'    : lambda x: x['CE_JobId'] + "_" + self.machine_name,
            'LrmsId'         : lambda x: x['clusterid'] + "_" + self.machine_name,
            'Site'           : lambda x: self.site_name,
            'ValidFrom'      : lambda x: valid_from(parse_timestamp(x['timestamp'])),
            'ValidUntil'     : lambda x: valid_until(parse_timestamp(x['timestamp'])),
            'Processed'      : lambda x: Parser.UNPROCESSED
        }

        for key, value in parts:
            # Store only the first value encountered. This is mainly for the
            # userFQAN field as the first occurence of this is the primary FQAN.
            if key not in data:
                data[key] = value

        for key in mapping:
            rc[key] = mapping[key](data)

        record = HTCondorCERecord()
        record.set_all(rc)
        return record