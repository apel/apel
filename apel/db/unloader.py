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
from apel.db import Query, ApelDbException, LOGGER_ID,\
    JOB_MSG_HEADER, SUMMARY_MSG_HEADER, SYNC_MSG_HEADER, CLOUD_MSG_HEADER, \
    CLOUD_SUMMARY_MSG_HEADER
from apel.db.records import JobRecord, SummaryRecord, SyncRecord, CloudRecord, CloudSummaryRecord
from dirq.QueueSimple import QueueSimple
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import datetime
import os
import logging

log = logging.getLogger(LOGGER_ID)

class DbUnloader(object):
    
    APEL_HEADERS = {JobRecord: JOB_MSG_HEADER, 
                    SummaryRecord: SUMMARY_MSG_HEADER,
                    SyncRecord: SYNC_MSG_HEADER,
                    CloudRecord: CLOUD_MSG_HEADER,
                    CloudSummaryRecord: CLOUD_SUMMARY_MSG_HEADER}
    
    RECORD_TYPES = {'VJobRecords': JobRecord,
                    'VSummaries': SummaryRecord,
                    'VSuperSummaries': SummaryRecord,
                    'VSyncRecords': SyncRecord,
                    'VCloudRecords': CloudRecord,
                    'VCloudSummaries': CloudSummaryRecord}
    
    def __init__(self, db, qpath, inc_vos=None, exc_vos=None, local=False):
        self._db = db
        outpath = os.path.join(qpath, "outgoing")
        self._msgq = QueueSimple(outpath)
        self._inc_vos = inc_vos
        self._exc_vos = exc_vos
        self._local = local
        
    def _get_base_query(self, record_type):
        '''
        Set up a query object containing the logic which is common for 
        all users of this DbUnloader.
        ''' 
        query = Query()
        
        if record_type in (JobRecord, SummaryRecord, SyncRecord):
            if self._inc_vos is not None:
                query.VO_in = self._inc_vos
                log.info('Sending only these VOs: ')
                log.info(self._inc_vos)
            elif self._exc_vos is not None:
                log.info('Excluding these VOs: ')
                log.info(self._exc_vos)
                query.VO_notin = self._exc_vos
            if not self._local:
                query.InfrastructureType = 'grid'
            
        return query
        
    def unload_all(self, table_name, car=False):
        '''
        Unload all records from the specified table.
        '''
        log.info('Unloading all records from %s.' % table_name)
        
        record_type = self.RECORD_TYPES[table_name]
        
        query = self._get_base_query(record_type)
        msgs, records = self._write_messages(record_type, table_name, query, car)
        return msgs, records
        
    def unload_sync(self):
        '''
        Unload all records from the SyncRecords table or view.
        '''
        log.info('Writing sync messages.')
        query = self._get_base_query(SyncRecord)
        msgs = 0
        records = 0
        for batch in self._db.get_sync_records(query=query):
            records += len(batch)
            self._write_apel(batch)
            msgs += 1
        return msgs, records
        
        
    def unload_gap(self, table_name, start, end, ur=False):
        '''
        Unload all records from the JobRecords table whose EndTime falls
        within the provided dates (inclusive).
        '''
        record_type = self.RECORD_TYPES[table_name]
        
        if record_type != JobRecord:
            raise ApelDbException("Can only gap publish for JobRecords.")
        
        start_tuple = [ int(x) for x in start.split('-') ]
        end_tuple = [ int(x) for x in end.split('-') ]
        # get the start of the start date
        start_date = datetime.date(*start_tuple)
        start_datetime = datetime.datetime.combine(start_date, datetime.time())
        # get the end of the end date
        end_date = datetime.date(*end_tuple)
        end_datetime = datetime.datetime.combine(end_date, datetime.time())
        end_datetime += datetime.timedelta(days=1)
        
        log.info('Finding records with end times between:')
        log.info(start_datetime)
        log.info(end_datetime)
        query = self._get_base_query(record_type)
        query.EndTime_gt = start_datetime
        query.EndTime_le = end_datetime
            
        msgs, records = self._write_messages(record_type, table_name, query, ur)
        return msgs, records
    
    def unload_latest(self, table_name, ur=False):
        '''
        Unloads records from database to file.
        
        Returns the number of created files.
        '''
        record_type = self.RECORD_TYPES[table_name]
        
        query = self._get_base_query(record_type)
        since = self._db.get_last_updated()
        
        log.info('Getting records updated since: %s' % since)
        if since is not None:
            query.UpdateTime_gt = str(since)
            
        msgs, records = self._write_messages(record_type, table_name, query, ur)
        
        self._db.set_updated()
        
        return msgs, records
            
    def _write_messages(self, record_type, table_name, query, ur):
        '''
        Write messsages for all the records found in the specified table,
        according to the logic contained in the query object.
        '''
        log.info('writing messages')
        msgs = 0
        records = 0
        for batch in self._db.get_records(record_type, table_name, query=query):
            records += len(batch)
            if ur:
                self._write_xml(batch)
            else:
                self._write_apel(batch)
            msgs += 1
        
        return msgs, records
    
    def _write_xml(self, records):
        '''
        Write one message in the appropriate XML format to the outgoing 
        message queue.
        
        This currently works only for CAR.
        '''
        buf = StringIO.StringIO()
        if type(records[0]) == JobRecord:
            XML_HEADER = '<?xml version="1.0" ?>'
            UR_OPEN = '<urf:UsageRecords xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/computerecord car_v1.2.xsd">'
            UR_CLOSE = '</urf:UsageRecords>'
#        elif type(records[0]) == SummaryRecord:
#            XML_HEADER = '<?xml version="1.0" ?>'
#            UR_OPEN = '<aur:SummaryRecords xmlns:aur="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord" xmlns:urf="http://eu-emi.eu/namespaces/2012/11/computerecord" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord ">'
#            UR_CLOSE = '</aur:SummaryRecords>'
        else:
            raise ApelDbException('Can only send URs for JobRecords.')
            
        buf.write(XML_HEADER + '\n')
        buf.write(UR_OPEN + '\n')
        buf.write('\n'.join( [ record.get_ur() for record in records ] ))
        buf.write('\n' + UR_CLOSE + '\n')
        
        self._msgq.add(buf.getvalue())
        buf.close()
        del buf
    
    def _write_apel(self, records):
        '''
        Write one message in the APEL format to the outgoing 
        message queue.
        '''
        record_type = type(records[0])
    
        buf = StringIO.StringIO()
        buf.write(self.APEL_HEADERS[record_type] + ' \n')
        buf.write('%%\n'.join( [ record.get_msg() for record in records ] ))
        buf.write('%%\n')
        
        self._msgq.add(buf.getvalue())
        buf.close()
        del buf
            
