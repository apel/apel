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


from apel.db import ApelDbException, LOGGER_ID
from apel.db.records import BlahdRecord, \
                            CloudRecord, \
                            EventRecord, \
                            GroupAttributeRecord, \
                            JobRecord, \
                            ProcessedRecord, \
                            StorageRecord, \
                            SummaryRecord, \
                            SyncRecord
import MySQLdb.cursors
import datetime
import logging
import decimal

# set up the logger 
log = logging.getLogger(LOGGER_ID)
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
                    ProcessedRecord : 'VProcessedFiles',
                    SummaryRecord : 'VSummaries'}
    
    # These simply need to have the same number of arguments as the stored procedures defined in the database schemas.
    MYSQL_PROCEDURES = {
              EventRecord : 'CALL InsertEventRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
              JobRecord   : "CALL InsertJobRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              BlahdRecord : "CALL InsertBlahdRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              SyncRecord  : "CALL InsertSyncRecord(%s, %s, %s, %s, %s, %s)",
              CloudRecord : "CALL InsertCloudRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              SummaryRecord: "CALL InsertSummary(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              StorageRecord: "CALL InsertStarRecord(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
              GroupAttributeRecord: "CALL InsertGroupAttribute(%s, %s, %s)",
              ProcessedRecord : "CALL InsertProcessedFile(%s, %s, %s, %s, %s)"
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

                
    def load_records(self, record_list, source=None):
        '''
        Loads the records in the list into the DB.  This is transactional - 
        either all or no records will be loaded.  Includes the DN of the 
        sender.
        '''

        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
            
            for record in record_list:
                proc = self.MYSQL_PROCEDURES[type(record)]
                values = record.get_db_tuple(source)
                c.execute(proc, values)
            self.db.commit()
        except (MySQLdb.Warning, MySQLdb.Error), err:
            log.error("Error loading records: %s" % str(err))
            log.error("Transaction will be rolled back.")
            self.db.rollback()
            raise ApelDbException(err)
        
    #def get_records(self, record_type, table_name=None, VOs=None, since=None, local=False, rec_number=1000):
    def get_records(self, record_type, table_name=None, query=None, rec_number=1000):
        '''
        Yields lists of records fetched from database.
        '''
        
        if table_name is None:
            table_name = self.MYSQL_TABLES[record_type]
      
        select_query = 'SELECT * FROM %s' % (table_name)
#        
#        clauses = []
#        
#        if VOs is not None and len(VOs) > 0:
#            vos = '("%s"' + ', "%s"' * (len(VOs) - 1) + ')'
#            vos = vos % VOs
#            clauses.append('VO in %s' % vos)
#        
#        if since is not None:
#            clauses.append('UpdateTime > "%s"' % since)
#        
#        if not local:
#            clauses.append('InfrastructureType = \"grid\"')
#            
#        if clauses:
#            select_query += " WHERE %s" % clauses.pop()
#            
#        for clause in clauses:
#            select_query += " AND %s" % clause

        if query is not None:
            
            select_query += query.get_where() 
            
        log.debug(select_query)

        record_list = []

        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor(cursorclass=MySQLdb.cursors.SSDictCursor)
            c.execute(select_query)
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
        query = 'select UpdateTime from LastUpdated where Type = "sent"'
        c = self.db.cursor()
        c.execute(query)
        result = c.fetchone()
        
        if result is None:
            return None
        else:
            return result[0]
        
    def set_updated(self):
        log.info('Updating timestamp.')
        query = 'call UpdateTimestamp("sent")'
        c = self.db.cursor()
        c.execute(query)
        c.fetchone()
        self.db.commit()
        return True
    
    def summarise(self):
        '''
        The summarising process has two parts: copying summaries from
        the Summaries table to the SuperSummaries table; and aggregating 
        the JobRecords table and putting the results in the 
        SuperSummaries table.  This method does this by calling the 
        two stored procedures which have these effects.
        
        Any failure will result in the entire transaction being rolled 
        back.
        '''
                
        try:
            # prevent MySQLdb from raising
            # 'MySQL server has gone' exception
            self._mysql_reconnect()
            
            c = self.db.cursor()
            
            # Preliminary check that we don't have data from the same site
            # in both job and summary tables
#            c.execute("select count(*) from JobRecords j inner join Summaries s using (SiteID)")
#            conflict = c.fetchone()[0] > 0
#            
#            if conflict:
#                raise ApelDbException("Records exist in both job and summary tables for the same site.")

            log.info("Summarising job records...")
            c.callproc(self._summarise_jobs_proc, ())
            log.info("Done.")
         
#            log.info("Copying summaries...")
#            c.callproc(self._copy_summaries_proc)
#            log.info("Done.")

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
