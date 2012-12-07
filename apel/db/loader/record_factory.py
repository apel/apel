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
   
@author Will Rogers

Module containing the RecordFactory class.
'''

from apel.db.records.job import JobRecord
from apel.db.records.summary import SummaryRecord
from apel.db.records.sync import SyncRecord
from apel.db.records.cloud import CloudRecord

from apel.db.loader.car_parser import CarParser
from apel.db.loader.aur_parser import AurParser
from apel.db.loader.star_parser import StarParser

import logging



# Set up logging
log = logging.getLogger(__name__)

class RecordFactoryException(Exception):
    '''Exception for use by the RecordFactory.'''
    pass


class RecordFactory(object):
    '''
    Class to create message objects for the appropriate message.  We only 
    expect to make JobRecord and SummaryRecord objects, but this shouldn't
    restrict the capability to make more.
    '''
    # Message headers
    JR_HEADER = 'APEL-individual-job-message'
    SR_HEADER = 'APEL-summary-job-message'
    SYNC_HEADER = 'APEL-sync-message'
    CLOUD_HEADER = 'APEL-cloud-message'
    # XML Tags
    JR_TAG = 'urf:UsageRecord'
    SR_TAG = 'aur:SummaryRecord'

    def create_records(self, msg_text):
        '''
        Given the text from a message, create a list of record objects and 
        return that list.
        '''    
        try:
        
        # XML format
            if msg_text.startswith('<?xml'):
                if RecordFactory.JR_TAG in msg_text:
                    created_records = self._create_cars(msg_text)
#                    # Not available yet.
                elif RecordFactory.SR_TAG in msg_text:
                    created_records = self._create_aurs(msg_text)
                elif StarParser.NAMESPACE in msg_text:
                    created_records = self._create_stars(msg_text)
                else:
                    raise RecordFactoryException('XML format not recognised.')
            # APEL format
            else:
                lines = msg_text.splitlines()
                
                header = lines.pop(0)
                # recreate message as string having removed header
                msg_text = '\n'.join(lines)        
                
                created_records = []
            
                # crop the string to before the first ':'
                index = header.index(':')
                header = header[0:index].strip()
                if (header == RecordFactory.JR_HEADER):
                    created_records = self._create_jrs(msg_text)
                elif (header == RecordFactory.SR_HEADER):
                    created_records = self._create_srs(msg_text)
                elif (header == RecordFactory.SYNC_HEADER):
                    created_records = self._create_syncs(msg_text)
                elif (header == RecordFactory.CLOUD_HEADER):
                    created_records = self._create_clouds(msg_text)
                else:
                    raise RecordFactoryException('Message type %s not recognised.' % header)
                
            return created_records
        
        except ValueError, e:
            raise RecordFactoryException('Message header is incorrect: %s' % e)

    ######################################################################
    # Private methods below
    ######################################################################

    def _create_jrs(self, msg_text):
        '''
        Given the text from a job record message, create a list of 
        JobRecord objects and return it.
        '''
        
        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                j = JobRecord()
                j.load_from_msg(record)
                msgs.append(j)
                
        return msgs
                

    def _create_srs(self, msg_text):
        '''
        Given the text from a summary record message, create a list of 
        JobRecord objects and return it.
        '''
        
        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                s = SummaryRecord()
                s.load_from_msg(record)
                msgs.append(s)
        
        return msgs
                

    def _create_syncs(self, msg_text):
        '''
        Given the text from a sync message, create a list of 
        SyncRecord objects and return it.
        '''
        
        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                s = SyncRecord()
                s.load_from_msg(record)
                msgs.append(s)
        
        return msgs
              
                
    def _create_clouds(self, msg_text):
        '''
        Given the text from a sync message, create a list of 
        SyncRecord objects and return it.
        '''
        
        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                c = CloudRecord()
                c.load_from_msg(record)
                msgs.append(c)
        
        return msgs
    
    
    def _create_cars(self, msg_text):
        '''
        Given a CAR message in XML format, create a list of JobRecord
        objects and return it.
        '''
        parser = CarParser(msg_text)
        records = parser.get_records()
        return records 
    
    def _create_aurs(self, msg_text):
        '''
        Given a CAR message in XML format, create a list of JobRecord
        objects and return it.
        '''
        parser = AurParser(msg_text)
        records = parser.get_records()
        return records 
    
    def _create_stars(self, msg_text):
        '''
        Given a StAR message in XML format, create a list of StorageRecord
        and GroupAttributes objects and return it.
        '''

        parser = StarParser(msg_text)
        records = parser.get_records()
        return records 
    