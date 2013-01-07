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

from apel.parsers import Parser
from apel.db.records.event import EventRecord

import re

class LSFParser(Parser):
    '''
    LSFParser parses LSF accounting logs from versions:
     - 5.x
     - 6.x
     - 7.x
     - 8.x
    '''

    '''
    The expression below describes elements which we are looking for.
    Here is some explanation:
    
    In accounting log file we have only two types of data: strings and numbers.
    Strings may contain quoted strings inside - marked by: ""this is quoted string"".
    The incorrect parsing of that lines can destroy the layout of fields (we can get
    several fields more or less than the documentation assumes). 
    
        (\"([^"]|(""))*\") - we are looking for everything between " and " except for double quotation
                             mark ("). ("") are treated as a part of field.
        ([-]?\d+(\.\d*)?)  - expression for integer and float numbers.
        
    Example line from LSF accounting log:
    "JOB_FINISH" "5.1" 1089407406 699195 283 33554482 1 1089290023 0 0 1089406862 
    "raortega" "8nm" "" "" "" "lxplus015" "prog/step3c" "" "/afs/cern.ch/user/r/raortega/log/bstep3c-362.txt"
    "/afs/cern.ch/user/r/raortega/log/berr-step3c-362.txt" "1089290023.699195" 0 1 "tbed0079" 64 3.3 ""
    "/afs/cern.ch/user/r/raortega/prog/step3c/startEachset.pl 362 7 8" 277.210000 17.280000 0 0 -1 0 0 927804
    87722 0 0 0 -1 0 0 0 0 0 -1 "" "default" 0 1 "" "" 0 310424 339112 "" "" ""
    
    Line was split, if you want to rejoin use ' ' as a joiner.
    '''

    EXPR = re.compile(r'''(
        (\"([^"]|(""))*\")
        |
        ([-]?\d+(\.\d*)?)
        )''', re.VERBOSE)

    def parse(self, line):

        # correct handling of double quotes
        # expression <condition and expr1 or expr2> in Python
        # means the same as <condition ? expr1 : expr2> in C
        # the later implementations of Python introduced syntax:
        # <expr1 if condition else expr2>
        items = [x[0].startswith('"') and x[0][1:-1].replace('""', '"') or x[0] 
                for x in self.EXPR.findall(line)]

        if items[0] != 'JOB_FINISH':
            return None
        
        num_asked = int(items[22])
        num_exec = int(items[23 + num_asked])
        offset = num_asked + num_exec
        
        # get unique values for the different hosts listed after num_exec
        nnodes = len(set(items[24 + num_asked:24 + offset]))
        
        mapping_lsf_5678 = {
                   'Site'           : lambda x: self.siteName,
                   'JobName'        : lambda x: x[3],
                   'LocalUserID'    : lambda x: x[11],
                   'LocalUserGroup' : lambda x: "",
                   'WallDuration'   : lambda x: int(x[2]) - int(x[10]),
                   'CpuDuration'    : lambda x: int(round(float(x[28+offset]) + float(x[29+offset]))),
                   'StartTime'      : lambda x: int(x[10]),
                   'StopTime'       : lambda x: int(x[2]),
                   'Infrastructure' : lambda x: "APEL-CREAM-LSF",
                   'Queue'          : lambda x: x[12],
                   'MachineName'    : lambda x: self.machineName,
                   'MemoryReal'     : lambda x: int(x[54+offset]) > 0 and int(x[54+offset]) or 0,
                   'MemoryVirtual'  : lambda x: int(x[55+offset]) > 0 and int(x[55+offset]) or 0,
                   'Processors'     : lambda x: num_exec,
                   'NodeCount'      : lambda x: nnodes
                   }
        
        mapping = {
                   '5' : mapping_lsf_5678,
                   '6' : mapping_lsf_5678,
                   '7' : mapping_lsf_5678,
                   '8' : mapping_lsf_5678
                  }
        
        version = items[1][0]
        data = {}
    
        for key in mapping[version]:
            data[key] = mapping[version][key](items)
        
        assert data['CpuDuration'] >= 0, 'Negative CpuDuration value'
        assert data['WallDuration'] >= 0, 'Negative WallDuration value'
        
        record = EventRecord()
        record.set_all(data)
        return record
