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
   
   @author: Will Rogers
'''

from apel.parsers import Parser

class SlurmParser(Parser):
    '''
    SlurmParser parses files from SGE batch system.
    
    This is not yet implemented.
    '''
    
    def __init__(self, site, machine_name, mpi):
        '''
        Not yet implemented.
        '''
        raise NotImplementedError('SLURM parser not yet implemented.')
    
    def parse(self, line):
        '''
        Parses single line from accounting log file.
        '''
        pass