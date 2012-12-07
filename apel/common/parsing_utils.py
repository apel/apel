'''
   Copyright 2012 Will Rogers

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

import logging

log = logging.getLogger(__name__)

def parse_fqan(fqan):
    '''
    We can get three pieces of information from a FQAN: role, group and VO.
    We return this as a 3-tuple.
    If it's not of the expected format, we put the whole string in the VO
    and leave the other two as None.
    '''
    # Take only the first FQAN
    fqan = fqan.split(';')[0]
    # Check for the expected format, accepting any case for 'role'
    fqan_check = fqan.lower()
    if (fqan_check.find('/') != 0) or (fqan_check.find('role=') == -1) \
            or (fqan_check.find('role=') == 1):
        # if not, just return FQAN as VO
        return (None, None, fqan)
           
    pieces = fqan.split('/')
    
    try:
        # pieces[0] is empty if the string begins with /
        vo = pieces[1]
        # group is everything before 'role='
        group = ""
        for piece in pieces:
            if len(piece) == 0:
                continue
            if piece.lower().startswith('role='):
                role = piece
                break
            else:
                group += '/' + piece
       
        return (role, group, vo)       
    
    except Exception:
        log.info("FQAN in non-standard format: " + fqan)
        return (None, None, fqan)