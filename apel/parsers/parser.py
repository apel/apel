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
import logging

log = logging.getLogger(__name__)

class ParserException(Exception):
    pass

class Parser(object):
    ''' The base class for all parsers '''
    
    UNPROCESSED = '0'
    PROCESSED = '1'
    
    def __init__(self, site, machine_name, mpi=False):
        '''
        Sets machine name and site name, and whether MPI information
        will be retrieved.
        '''
        self.site_name = site
        self.machine_name = machine_name
        log.info('Site: %s; batch system: %s', self.site_name, self.machine_name)
        self._mpi = mpi
        if self._mpi:
            log.info('Parser will retrieve per-processor accounting information.')

    def parse(self, line):
        '''
        Main method for all parsers. It parses a single line from a log file.

        @param line: Line to be parsed
        @return: Filled EventRecord/BlahdRecord
        '''
        raise NotImplementedError('Unimplemented error from base class.')

    def recognize(self, line):
        '''
        Method to recognize if the given line of file can be parsed with this parser
        
        @param line: Line from log file to recognize
        @return bool
        '''
        try:
            if self.parse(line) is not None:
                return True
        except Exception:  # An exception means we can't parse the file!
            pass
        
        return False
    