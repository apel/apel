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

Created on 26 Jul 2012

@author: Alan Kyffin, STFC

'''

from apel.db import ApelDbException, LOGGER_ID
from apel.db.records.job import JobRecord
import cx_Oracle
import logging
# import warnings

# Set up the logger
log = logging.getLogger(LOGGER_ID)

# Treat cx_Oracle warnings as exceptions
# warnings.simplefilter("error", category=cx_Oracle.Warning)


class ApelOracleDb(object):
    ''' Oracle implementation of the general ApelDb interface. '''

    def __init__(self, host, port, username, pwd, db):
        ''' Initialise variables. '''

        self._db_connect_string = username + '/' + pwd + '@' + host + ':' + str(port) + '/' + db
        self._db_log_string = username + '@' + host + ':' + str(port) + '/' + db

        self.INSERT_PROCEDURES = {
            JobRecord     : 'pkg_apel_dbloader.insert_temp_job_record'
        }

        self.MERGE_PROCEDURES = {
            JobRecord     : 'pkg_apel_dbloader.merge_temp_job_records'
        }


    def test_connection(self):
        ''' Tests the DB connection. '''

        try:
            con = cx_Oracle.connect(self._db_connect_string)

            log.info('Connected to: ' + self._db_log_string)
            log.info('Oracle Version: ' + con.version)

            con.close()

        except Exception, e:
            raise ApelDbException('Failed to connect to database: ' + str(e))


    def load_records(self, record_list, source):
        '''
        Loads the records in the list into the DB.  This is transactional -
        either all or no records will be loaded.  Includes the DN of the
        sender.
        '''

        con = cx_Oracle.connect(self._db_connect_string)

        try:
            cur = con.cursor()

            # Insert the records into temporary tables.
            for record in record_list:
                proc = self.INSERT_PROCEDURES[type(record)]
                values = record.get_db_tuple(source)

                cur.callproc(proc, values)

            # Now merge the temporary tables into the actual tables.
            for k, v in self.MERGE_PROCEDURES.iteritems():
                cur.callproc(v)

            con.commit()
            con.close()

        except (cx_Oracle.Warning, cx_Oracle.Error), err:
            log.error("Error loading records: %s", err)
            log.error("Transaction will be rolled back.")

            con.rollback()
            con.close()

            raise ApelDbException(err)

