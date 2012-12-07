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
from apel.parsers import LOGGER_ID

logger = logging.getLogger(LOGGER_ID)

class Parser(object):
    ''' The base class for all parsers '''
    
    UNPROCESSED = '0'
    PROCESSED = '1'
    
    def __init__(self, siteName='', machineName=''):
        '''
        Sets machine name and site name.
        '''
        self.siteName = siteName
        self.machineName = machineName
        logger.info('Created parser for: %s / %s' % (self.siteName, self.machineName))

    def parse(self, line):
        '''
        Main method for all parsers. It parses single line of log.

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
        except: # An exception means we can't parse the file!
            pass
        
        return False