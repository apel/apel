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
   
   @author Will Rogers, Konrad Jopek

Module containing the Loader class.
'''

import apel.db 
import logging
import os

from apel.db.records import InvalidRecordException
from apel.db.loader.xml_parser import XMLParserException
from record_factory import RecordFactory, RecordFactoryException

from dirq.queue import Queue

# set up the logger 
log = logging.getLogger('loader')

QSCHEMA = {"body": "string", "signer":"string", "empaid":"string?", "error": "string?"}
REJECT_SCHEMA = {"body": "string", "signer":"string?", "empaid":"string?", "error": "string"}

class LoaderException(Exception):
    ''' Exception for use by loader class.'''
    pass

class Loader(object):
    '''
    Designed to read apel messages containing summary records or individual
    job records and load them into the appropriate database.
    '''
    def __init__(self, qpath, backend, host, port, db, user, pwd, pidfile):
        '''
        Set up the database details.
        '''
        self._db_host = host
        self._db_port = port
        self._db_name = db
        self._db_username = user
        self._db_pwd = pwd
        # Only here (and in the imports) would we change if we needed 
        # to change the DB class used.
        self._apeldb = apel.db.ApelDb(backend, self._db_host, self._db_port, 
                                    self._db_username, self._db_pwd,
                                    self._db_name)
        # Check the connection while we're setting up.
        self._apeldb.test_connection()
        
        inqpath = os.path.join(qpath, "incoming")
        rejectqpath = os.path.join(qpath, "reject")
        self._inq = Queue(inqpath, schema=QSCHEMA)
        self._rejectq = Queue(rejectqpath, schema=REJECT_SCHEMA)
        
        # Create a message factory
        self._rf = RecordFactory()
        self._pidfile = pidfile
        log.info("Loader created.")
        
    def startup(self):
        """
        Create a pidfile.
        """ 
        # If the pidfile exists, don't start up.
        if os.path.exists(self._pidfile):
            log.warn("A pidfile %s already exists." % self._pidfile)
            log.warn("Check that the dbloader is not running, then remove the file.")
            raise LoaderException("The dbloader cannot start while pidfile exists.")
        try:
            f = open(self._pidfile, "w")
            f.write(str(os.getpid()))
            f.write("\n")
            f.close()
        except IOError, e:
            log.warn("Failed to create pidfile %s: %s" % (self._pidfile, e))
                
    def shutdown(self):
        """
        Remove the pidfile.
        """
        pidfile = self._pidfile
        try:
            if os.path.exists(pidfile):
                os.remove(pidfile)
            else:
                log.warn("pidfile %s not found." % pidfile)
        except IOError, e:
            log.warn("Failed to remove pidfile %s: %e" % (pidfile, e))
            log.warn("The loader may not start again until it is removed.")
            
        log.info("The loader has shut down.")
        
    def load_all_msgs(self):
        '''
        Get all the messages from the MessageDB and attempt to put them 
        into the database.
        '''
        log.debug("======================")
        log.debug("Starting loader run.")
        log.info("Found %s messages" % self._inq.count())

        name = self._inq.first()
        # loop until there are no messages left
        while name:
            if not self._inq.lock(name):
                log.warn("Skipping locked message: ID = %s" % name)
                name = self._inq.next()
                continue
            log.debug("# reading element %s" % name)
            data = self._inq.get(name)
            msg_id = data['empaid']
            signer = data['signer']
            msg_text = data['body']
            
            try:
                log.info("Loading message: ID = " + msg_id)
                self.load_msg(msg_text, signer)
            except (RecordFactoryException, LoaderException,
                    InvalidRecordException, apel.db.ApelDbException,
                    XMLParserException), err:
                errmsg = "Message parsing unsuccessful: %s." % str(err)
                log.warn('Message rejected: %s' % errmsg)
                self._rejectq.add({"body": msg_text, 
                                   "signer": signer, 
                                   "empaid": msg_id,
                                   "error": errmsg})
                
            log.info("Removing message: ID = " + msg_id)
            self._inq.remove(name)
            name = self._inq.next()
            
        log.debug("Loader run finished.")
        log.debug("======================")
        
    def load_msg(self, msg_text, signer):
        '''
        Load one message (i.e. one file; many records)
        from its text content into the database.
        '''
        log.info('Loading message from ' + signer + '.')

        # Create the record objects, using the RecordFactory
        records = self._rf.create_records(msg_text)
        log.info('Message contains '+ str(len(records)) + ' records.')
        # Use the DB to load the records
        self._apeldb.load_records(records, signer)
        
        log.debug('Message successfully loaded.')
 