'''
   Copyright 2012 Konrad Jopek

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

import md5
import gzip

def calculate_hash(fname, gz=False):
    '''
    Calculates MD5 hash from content of file with name='fname'.  Opens gzip
    file if gz=True.
    
    Used in parsers to avoid double parsing of files.
    For sample usage please go to: apel2/bin/client.py
    '''
    
    data = 'initial'
    
    if gz:
        fp = gzip.open(fname, 'r')
    else:
        fp = open(fname, 'r')
    
    md = md5.new()
    
    while data != '':
        # 128kiB buffer
        data = fp.read(131072)
        md.update(data)
    
    fp.close()
    return md.hexdigest()