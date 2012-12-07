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
   
A parser for BLAH record file.
I've used a regular expression here. Maybe import csv would be better?

    @author: Konrad Jopek
'''

from apel.db.records.blahd import BlahdRecord
from apel.common import valid_from, valid_until, parse_timestamp
from apel.common.parsing_utils import parse_fqan
from apel.parsers import Parser

import re

class BlahParser(Parser):
    '''
    BlahParser parses accounting files from Blah system.
    '''
    
    # expression below is used to divide 
    # single line from log file into array
    # of values which are later parsed.
    LINE_EXPR = re.compile(r'\"|\"_\"')

    def parse(self, line):
        '''
        Parses single line from accounting log file.
        
        Example line of accounting log file:
        "timestamp=2012-05-20 23:59:47" "userDN=/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg"
        "userFQAN=/atlas/Role=production/Capability=NULL" "ceID=cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL"
        "jobID=CREAM410741480" "lrmsID=9575064.lrms1" "localUser=11999"
        
        Line was split, if you want to rejoin use ' ' as a joiner.
        '''
        data = {}
        rc = {}
        record = BlahdRecord()
        
        #  split file and remove parts which contain only space (like ' ')
        parts = [x.split('=',1) for x in [y for y in self.LINE_EXPR.split(line) if len(y) > 1]]
        
        # Simple mapping between keys in a log file and a table's columns
        mapping = {
            'TimeStamp'      : lambda x: 'T'.join(x['timestamp'].split()) + 'Z',
            'GlobalUserName' : lambda x: x['userDN'],
            'FQAN'           : lambda x: x['userFQAN'],
            'VO'             : lambda x: parse_fqan(x['userFQAN'])[2],
            'VOGroup'        : lambda x: parse_fqan(x['userFQAN'])[1],
            'VORole'         : lambda x: parse_fqan(x['userFQAN'])[0],
            'CE'             : lambda x: x['ceID'],
            'GlobalJobId'    : lambda x: x['jobID'],
            'LrmsId'         : lambda x: x['lrmsID'],
            'Site'           : lambda x: self.siteName,
            'ValidFrom'      : lambda x: valid_from(parse_timestamp(x['timestamp'])),
            'ValidUntil'     : lambda x: valid_until(parse_timestamp(x['timestamp'])),
            'Processed'      : lambda x: Parser.UNPROCESSED}

        for key,value in parts:
            data[key] = value
        
        for key in mapping:
            rc[key] = mapping[key](data)

        record.set_all(rc)
        
        return record
    