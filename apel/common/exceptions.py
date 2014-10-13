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
import sys
import logging

log = logging.getLogger(__name__)

def install_exc_handler(handler):
    '''
    Installs the global exception handler.
    '''
    sys.excepthook = handler


def default_handler(exc_type, value, traceback):
    '''
    Default handler for unhandled exception.
    Current version stores information about exception
    and saves traceback for debugging process.
    
    In future this handler can be able to log problems
    with applications to Nagios or other monitoring system.
    '''
    
    log.critical('Unhandled exception raised!')
    log.critical('Please send a bug report with following information:')
    log.critical('%s: %s', exc_type.__name__, value)

    tbstack = []
    
    while traceback:
        tbstack.append(
            (traceback.tb_frame.f_code.co_filename, 
             traceback.tb_frame.f_code.co_name, 
             traceback.tb_lineno))
        traceback = traceback.tb_next
    
    tbstack.reverse()

    log.critical('%s [%s %s]', tbstack[0][1], tbstack[0][0], tbstack[0][2])

    for tb in tbstack[1:]:
        log.critical('  %s in %s [%s]', tb[1], tb[0], tb[2])
