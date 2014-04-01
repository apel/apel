'''
   Copyright (C) 2011,2012 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
Created on 27 Oct 2011

    @author: Will Rogers, Konrad Jopek
'''


from apel.db import ApelDbException
from apel.db.records import BlahdRecord, \
                            CloudRecord, \
                            CloudSummaryRecord, \
                            EventRecord, \
                            GroupAttributeRecord, \
                            JobRecord, \
                            NormalisedSummaryRecord, \
                            ProcessedRecord, \
                            StorageRecord, \
                            SummaryRecord, \
                            SyncRecord
import MySQLdb.cursors
import datetime
import logging
import decimal

# set up the logger 
log = logging.getLogger(__name__)
# treat MySQL warnings as exceptions
#warnings.simplefilter("error", category=MySQLdb.Warning)

class ApelMysqlDb(object):
    '''
    MySQL implementation of the general ApelDb interface.
    '''
    MYSQL_TABLES = {EventRecord : 'EventRecords',
                    JobRecord   : 'VJobRecords',
                    BlahdRecord : 'BlahdRecords',
                    SyncRecord  : 'SyncRecords',
                    CloudRecord : 'CloudRecords',
                    CloudSummaryRecord : 'VCloudSummaries',
                    NormalisedSummaryRecord : 'NormalisedSummaries',
                    ProcessedRecord : 'VProcessedFiles',
                    SummaryRecord : 'VSummaries'}
    
    # These simply need to have the same number of arguments as the stored procedures defined in the database schemas.
    INSERT_PROCEDURES = {
              EventRecord : 'CALL InsertEventRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
              BlahdRecord : "CALL InsertBlahdRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              }
    
    REPLACE_PROCEDURES = {
              EventRecord : 'CALL ReplaceEventRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
              JobRecord   : "CALL ReplaceJobRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              SummaryRecord: "CALL ReplaceSummary(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              NormalisedSummaryRecord: "CALL ReplaceNormalisedSummary(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              SyncRecord  : "CALL ReplaceSyncRecord(%s, %s, %s, %s, %s, %s)",
              ProcessedRecord : "CALL ReplaceProcessedFile(%s, %s, %s, %s, %s)",
              CloudRecord : "CALL ReplaceCloudRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              CloudSummaryRecord : "CALL ReplaceCloudSummaryRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              StorageRecord: "CALL ReplaceStarRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              GroupAttributeRecord: "CALL ReplaceGroupAttribute(%s, %s, %s)"
              }
    
    def __init__(self, host, port, username, pwd, db):
        '''
        Initialise variables, and define stored procedures.
        '''
        self._db_host = host
        self._db_port = port
        self._db_username = username
        self._db_pwd = pwd
        self._db_name = db
        
        self._summarise_jobs_proc = "SummariseJobs"
        self._normalise_summaries_proc = "NormaliseSummaries"
        self._summarise_vms_proc = "SummariseVMs"
        self._copy_summaries_proc = "CopySummaries"
        self._hep_spec_hist_proc = "CreateHepSpecHistory"
        self._join_records_proc = "JoinJobRecords"
        self._local_jobs_proc = "LocalJobs"
        self._spec_lookup_proc = "SpecLookup (%s, %s, %s, %s)"
        self._spec_update_proc = "CALL SpecUpdate (%s, %s, %s, %s, %s)"
        
        self._processed_clean = "CALL CleanProcessedFiles(%s)"
        
        try:
            self.db = MySQLdb.connect(host=self._db_host, port=self._db_port, 
                                      user=self._db_username, passwd=self._db_pwd, 
                                      db=self._db_name)
        except MySQLdb.Error, e:
            log.error('Error connecting to database: %s' % str(e))
            raise ApelDbException(e)
        
    def test_connection(self):
        '''
        Tests the DB connection - if it fails a MySQLdb.OperationalError will be
        thrown.
        '''
        try:
            db =  MySQLdb.connect(host=self._db_host, port=self._db_port, 
                                  user=self._db_username, passwd=self._db_pwd, 
                                  db=self._db_name)
        
            log.info('Connected to ' + self._db_host + ':' + str(self._db_port))
            log.info('Database: ' + self._db_name + '; username: ' + self._db_username)
            db.close()
        except MySQLdb.OperationalError, e:
            raise ApelDbException("Failed to connect to database: " + str(e))

    def load_records(self, record_list, replace=True, source=None):
        '''
        Loads the records in the list into the DB.  This is transactional - 
        either all or no records will be loaded.  Includes the DN of the 
        sender.
        '''
        # all records in the list are the same type
        try:
            record_type = type(record_list[0])
            if replace:
                proc = self.REPLACE_PROCEDURES[record_type]
            else:
                proc = self.INSERT_PROCEDURES[record_type]
        except KeyError:
            raise ApelDbException('No procedure found for %s; replace = %s' % (record_type, replace))
        except IndexError:
            # no records to load
            return
            
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
            
            for record in record_list:
                values = record.get_db_tuple(source)
                log.debug('Values: %s' % str(values))
                c.execute(proc, values)
            self.db.commit()
        except (MySQLdb.Warning, MySQLdb.Error, KeyError), err:
            log.error("Error loading records: %s" % str(err))
            log.error("Transaction will be rolled back.")
            self.db.rollback()
            raise ApelDbException(err)
        
    def get_records(self, record_type, table_name=None, query=None, rec_number=1000):
        '''
        Yields lists of records fetched from database of the given type.  This is used
        if the records are coming directly from a table or view.
        '''
        if table_name is None:
            table_name = self.MYSQL_TABLES[record_type]
      
        select_query = 'SELECT * FROM %s' % (table_name)

        if query is not None:
            select_query += query.get_where() 
            
        log.debug(select_query)
        
        for batch in self._get_records(record_type, select_query, rec_number):
            yield batch

    def get_sync_records(self, query=None, rec_number=1000):
        '''
        Get sync records from the SuperSummaries table.  Filter by the 
        provided query.
        '''
        if query is not None:
            where = query.get_where()
        else:
            where = ''
        
        select_query = '''SELECT Site, SubmitHost, sum(NumberOfJobs) as NumberOfJobs, 
        Month, Year FROM VSuperSummaries %s GROUP BY Site, SubmitHost, Month, Year''' % where
        
        log.debug(select_query)
    
        for batch in self._get_records(SyncRecord, select_query, rec_number):
            yield batch
        
    def _get_records(self, record_type, query_string, rec_number=1000):

        record_list = []
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor(cursorclass=MySQLdb.cursors.SSDictCursor)
            c.execute(query_string)
            while True:
                for row in c.fetchmany(size=rec_number):
                    record = record_type()
                    # row is a dictionary {Field: Value}
                    record.set_all(row)
                    record_list.append(record)
                
                if len(record_list) > 0:
                    yield record_list
                    record_list = []
                
                else:
                    break
                
        except MySQLdb.Error, err:
            log.error('Error during getting records: %s' % (str(err)))
            log.error('Transaction will be rolled back.')
            self.db.rollback()
            raise ApelDbException(err)
        except MySQLdb.Warning, warning:
            log.warn('Warning from MySQL: %s' % str(warning))
        
        
    def get_last_updated(self):
        '''
        Find the last time that messages were sent.
        '''
        query = 'select UpdateTime from LastUpdated where Type = "sent"'
        c = self.db.cursor()
        c.execute(query)
        result = c.fetchone()
        
        if result is None:
            return None
        else:
            return result[0]
        
    def set_updated(self):
        '''
        Set the current time as the last time messages were sent.
        '''
        log.info('Updating timestamp.')
        query = 'call UpdateTimestamp("sent")'
        c = self.db.cursor()
        c.execute(query)
        c.fetchone()
        self.db.commit()
        return True
    
    def check_duplicate_sites(self):
        '''
        Check that records from the same site are not in both the 
        JobRecords table and the Summaries table.
        '''
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            
            c.execute("select count(*) from JobRecords j inner join Summaries s using (SiteID)")
            conflict = c.fetchone()[0] > 0
            
            if conflict:
                raise ApelDbException("Records exist in both job and summary tables for the same site.")
            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            
            if not self.db is None:
                self.db.rollback()
            raise
            
    def summarise_jobs(self):
        '''
        Aggregate the data from the JobRecords table and put the results in the 
        NormalisedSuperSummaries table.  This method does this by calling the 
        SummariseJobs stored procedure.
        
        Any failure will result in the entire transaction being rolled 
        back.
        '''
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()

            log.info("Summarising job records...")
            c.callproc(self._summarise_jobs_proc, ())
            log.info("Done.")
            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            
            if not self.db is None:
                self.db.rollback()
            raise
    
    def normalise_summaries(self):
        """
        Normalise data from Summaries and insert into NormalisedSuperSummaries.

        Normalise the data from the Summaries table (calculate the normalised
        wall clock and cpu duration values from the ServiceLevel fields) and put
        the results in the NormalisedSuperSummaries table. This is done by
        calling the NormaliseSummaries stored procedure.

        Any failure will result in the entire transaction being rolled 
        back.
        """
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()

            c = self.db.cursor()

            log.info("Normalising the Summary records...")
            c.callproc(self._normalise_summaries_proc, ())
            log.info("Done.")
            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")

            if not self.db is None:
                self.db.rollback()
            raise
    
    def copy_summaries(self):
        '''
        Copy summaries from the NormalisedSummaries table to the NormalisedSuperSummaries table.
        ''' 
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            log.info("Copying summaries...")
            c.callproc(self._copy_summaries_proc)
            log.info("Done.")

            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            
            if not self.db is None:
                self.db.rollback()
            raise
        
    def summarise_cloud(self):
        '''
        Aggregate the CloudRecords table and put the results in the 
        CloudSummaries table.  This method does this by calling the 
        SummariseVMs() stored procedure.
        
        Any failure will result in the entire transaction being rolled 
        back.
        '''
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            
            log.info("Summarising cloud records...")
            c.callproc(self._summarise_vms_proc, ())
            log.info("Done.")
            
            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            
            if not self.db is None:
                self.db.rollback()
            raise
        
    def join_records(self):
        '''
        This method executes JoinJobRecords procedure in database which joins data 
        from BlahdRecords table and EventRecords table into JobRecord.
        
        For exact implementantion please read the code of JoinJobRecords procedure
        from client.sql in apeldb/schema folder.
        '''
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            log.info("Creating JobRecords")
            c.callproc(self._join_records_proc)
            log.info("Done.")
            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            
            if not self.db is None:
                self.db.rollback()
            raise e
        
    def create_local_jobs(self):
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            
            log.info("Creating local jobs")
            c.callproc(self._local_jobs_proc)
            log.info("Done.")
            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            
            if not self.db is None:
                self.db.rollback()
                
            raise e
    
    def update_spec(self, site, ce, spec_level_type, spec_level):
        '''
        This method compares the existing data from database to given values
        and updates the SpecRecords table if it is neccessary.
        '''
        
        try:
            # prevent MySQLdb from raising 
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            
            c.execute("SELECT %s" % self._spec_lookup_proc, 
                      [site, ce, spec_level_type, 
                       datetime.datetime.now()])
            
            # MySQL 5.1.xx (or MySQL-python 1.2.1) returns None
            # directly from c.fetchone(), so we must handle it in another way
            try:
                old_level = c.fetchone()[0]
            except TypeError:
                old_level = None
                
            # Precision limited to third decimal place is enough for our purposes.
            
            if old_level is None:
                c.execute(self._spec_update_proc,
                           [site, ce, spec_level_type,
                            datetime.datetime.fromtimestamp(0),
                            spec_level])
            elif abs((old_level-decimal.Decimal(str(spec_level)))) > decimal.Decimal('0.001'):
                c.execute(self._spec_update_proc, 
                           [site, ce, spec_level_type, 
                            datetime.datetime.now(), spec_level])

            self.db.commit()
            
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            
            if not self.db is None:
                self.db.rollback()
        
    def clean_processed_files(self, hostname):
        '''
        Cleans ProcessedFiles table from records for given host.
        '''
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            c.execute(self._processed_clean, [hostname])
            self.db.commit()
        except MySQLdb.Error, e:
            log.error("A mysql error occurred: %s" % e)
            log.error("Any transaction will be rolled back.")
            if not self.db is None:
                self.db.rollback()
    
    def _mysql_reconnect(self):
        '''
        Checks if current connection is active and
        reconnects if necessary
        '''
        try:
            self.db.ping()
        except MySQLdb.Error:
            try:
                self.db = MySQLdb.connect(host=self._db_host, port=self._db_port, 
                                          user=self._db_username, passwd=self._db_pwd, 
                                          db=self._db_name)
            except MySQLdb.Error, e:
                log.error('Error connecting to database: %s' % str(e))
                raise ApelDbException(e)
