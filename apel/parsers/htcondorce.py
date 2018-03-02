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

    @author: Jordi Casals, Geonmo Ryu
'''

from apel.db.records.blahd import BlahdRecord
from apel.common import valid_from, valid_until
from apel.common.parsing_utils import parse_fqan
from apel.parsers import HTCondorParser

import datetime, logging

log = logging.getLogger(__name__)

class HTCondorCEParser(HTCondorParser):
    '''
    HTCondorCE parses accounting files from HTCondorCE system.
    '''
    mapping = None
    isParsed = False
    def __init__(self, site, machine_name, mpi):
        HTCondorParser.__init__(self, site, machine_name, mpi)
    def getMapping(self):
        '''
        Return the parsed mapping.
        '''
        if isParsed:
            return self.mapping
        else:
            print "The log files are not yet parsed by HTCondorCEParser."
            return None
    def parse(self, line):
        '''
        Parses single line from accounting log file.
        Example line of accounting log file:
        "cms-t2-ce01.sdfarm.kr#2.0#1492418148|3.0|geonmo|/C=KR/O=KISTI/O=GRID/O=KISTI/CN=58079576
Geonmo Ryu|/cms/Role=NULL/Capability=NULL|cms|1|0|0|1492418156|1492418167|0|100|1|"
        ['cms-t2-ce01.sdfarm.kr#2.0#1492418148', '3.0', 'geonmo',
        '/C=KR/O=KISTI/O=GRID/O=KISTI/CN=58079576 Geonmo Ryu', '/cms/Role=NULL/Capability=NULL',
        'cms', '1', '0', '0', '1492418156', '1492418167', '0', '100', '1', '']

        '''
        values = line.strip().split('|')
        dateinfo = datetime.datetime.fromtimestamp(float(line.strip().split('|')[9]))
        self.mapping = {
            'TimeStamp'      : lambda x: dateinfo.isoformat()+'Z',
            'GlobalUserName' : lambda x: x[3],
            'FQAN'           : lambda x: x[4],
            'VO'             : lambda x: parse_fqan(x[4])[2],
            'VOGroup'        : lambda x: parse_fqan(x[4])[1],
            'VORole'         : lambda x: parse_fqan(x[4])[0],
            'CE'             : lambda x: self.machine_name + ":" + "9619" + "/" + self.machine_name + "-" + "condor",
            'GlobalJobId'    : lambda x: x[0],
            'LrmsId'         : lambda x: x[1]+'.'+self.machine_name,
            'Site'           : lambda x: self.site_name,
            'ValidFrom'      : lambda x: valid_from(dateinfo),
            'ValidUntil'     : lambda x: valid_until(dateinfo),
            'Processed'      : lambda x: Parser.UNPROCESSED
        }
        rc = {}
        for key in self.mapping:
            rc[key] = self.mapping[key](values)
        record = BlahdRecord()
        record.set_all(rc)
        self.isParsed = True
        return record
