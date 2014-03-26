'''
   Copyright (C) 2013 Henning Perl

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

from datetime import datetime
from apel.db.records.application import ApplicationRecord
from apel.parsers import Parser

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError('Python 2.7, 2.6, 2.5 with simplejson, or 2.4 with simplejson 2.0.9 required')


class ApplicationParser(Parser):
    '''
    Application Accounting parser.
    '''

    def parse(self, line):
        '''
        Parses single line from accounting log file.

        Example line of accounting log file (JSON format):
        {"binary path": "/usr/bin/uptime", "exit_info": {"exited_normally": "true", "signal": "0"}, "user": {"uid": "501", "gid": "20"}, "start_time": "Tue Nov  5 15:05:01 2013", "end_time": "Tue Nov  5 15:05:01 2013"}
        '''
        # clean up newline etc.
        line = line.strip()
        # json parse the stuff
        data = json.loads(line)

        # Simple mapping between keys in a log file and a table's columns
        mapping = { 'BinaryPath'     : lambda x: x['binary path']
                  , 'ExitInfo'       : lambda x: x['exit_info']
                  , 'User'           : lambda x: x['user']
                  , 'StartTime'      : lambda x: datetime.strptime(x['start_time'], '%c')
                  , 'EndTime'        : lambda x: datetime.strptime(x['end_time'], '%c')
                  }
        rc = {}
        for key in mapping:
            rc[key] = mapping[key](data)

        return ApplicationRecord(**rc)

