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

import logging
import os
from xml.parsers.expat import ExpatError

from dirq.queue import Queue

import apel.db
from apel.db.loader.xml_parser import XMLParserException
from apel.db.records import InvalidRecordException
from record_factory import RecordFactory, RecordFactoryException


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
    def __init__(self, qpath, save_msgs, backend, host, port, db, user, pwd, pidfile):
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

        self._save_msgs = save_msgs
        if self._save_msgs:
            acceptqpath = os.path.join(qpath, "accept")
            self._acceptq = Queue(acceptqpath, schema=QSCHEMA)

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
            log.warning("A pidfile %s already exists.", self._pidfile)
            log.warning("Check that the dbloader is not running, then remove the file.")
            raise LoaderException("The dbloader cannot start while pidfile exists.")
        try:
            f = open(self._pidfile, "w")
            f.write(str(os.getpid()))
            f.write("\n")
            f.close()
        except IOError, e:
            log.warning("Failed to create pidfile %s: %s", self._pidfile, e)

    def shutdown(self):
        """
        Unlock current messsage queue element and remove pidfile.
        """
        # Check if self.current_msg is assigned as it may not have been before
        # shutdown is called.
        if hasattr(self, 'current_msg') and self.current_msg:
            try:
                self._inq.unlock(self.current_msg)
            except OSError, e:
                log.error('Unable to remove lock: %s', e)

        pidfile = self._pidfile
        try:
            if os.path.exists(pidfile):
                os.remove(pidfile)
            else:
                log.warning("pidfile %s not found.", pidfile)
        except IOError, e:
            log.warning("Failed to remove pidfile %s: %s", pidfile, e)
            log.warning("The loader may not start again until it is removed.")

        log.info("The loader has shut down.")

    def load_all_msgs(self):
        """
        Get all the messages from the incoming queue and attempt to put them
        into the database, then purge the accept, incoming, and reject queues.
        """
        log.debug("======================")
        log.debug("Starting loader run.")

        num_msgs = self._inq.count()
        log.info("Found %s messages", num_msgs)

        self.current_msg = self._inq.first()
        # loop until there are no messages left
        while self.current_msg:
            if not self._inq.lock(self.current_msg):
                log.warning("Skipping locked message %s", self.current_msg)
                self.current_msg = self._inq.next()
                continue
            log.debug("Reading message %s", self.current_msg)
            data = self._inq.get(self.current_msg)
            msg_id = data['empaid']
            signer = data['signer']
            msg_text = data['body']

            try:
                log.info("Loading message %s. ID = %s", self.current_msg, msg_id)

                if (not data or
                        not data['body'].strip() or
                        not data['signer'].strip() or
                        not data['empaid'].strip()):
                    raise LoaderException(
                        "Cannot load incomplete message from an incoming queue"
                    )

                self.load_msg(msg_text, signer)

                if self._save_msgs:
                    name = self._acceptq.add({"body": msg_text,
                                              "signer": signer,
                                              "empaid": msg_id})
                    log.info("Message saved to accept queue as %s", name)

            except (RecordFactoryException, LoaderException,
                    InvalidRecordException, apel.db.ApelDbException,
                    XMLParserException, ExpatError), err:
                errmsg = "Parsing unsuccessful: %s" % str(err)
                log.warning('Message rejected. %s', errmsg)
                name = self._rejectq.add({"body": msg_text,
                                          "signer": signer,
                                          "empaid": msg_id,
                                          "error": errmsg})
                log.info("Message saved to reject queue as %s", name)

            log.info("Removing message %s. ID = %s", self.current_msg, msg_id)
            self._inq.remove(self.current_msg)
            self.current_msg = self._inq.next()

        if num_msgs:  # Only tidy up if messages found
            log.info('Tidying message directories')
            try:
                # Remove empty dirs and unlock msgs older than 5 min (default)
                self._inq.purge()
                self._rejectq.purge()
                # The accept queue is only created if _save_msgs is true.
                if self._save_msgs:
                    self._acceptq.purge()
            except OSError, e:
                log.warning('OSError raised while purging message queues: %s', e)

        log.debug("Loader run finished.")
        log.debug("======================")

    def load_msg(self, msg_text, signer):
        '''
        Load one message (i.e. one file; many records)
        from its text content into the database.
        '''
        record_types = {
                    apel.db.records.summary.SummaryRecord: 'Summary',
                    apel.db.records.job.JobRecord: 'Job',
                    apel.db.records.normalised_summary.NormalisedSummaryRecord:
                    'Normalised Summary',
                    apel.db.records.sync.SyncRecord: 'Sync',
                    apel.db.records.cloud.CloudRecord: 'Cloud',
                    apel.db.records.cloud_summary.CloudSummaryRecord:
                    'Cloud Summary'}

        log.info('Loading message from %s', signer)

        # Create the record objects, using the RecordFactory
        records = self._rf.create_records(msg_text)

        try:
            if len(records) == 1:
                # Get record type to display in logs
                record_type = record_types[type(records[0])]
                log.info('Message contains 1 %s record', record_type)
            elif len(records) > 1:
                record_type = record_types[type(records[0])]
                log.info('Message contains %i %s records',
                         len(records), record_type)
            else:
                log.info('Message contains 0 records')
        except KeyError:  # if record type is not in record_types
            log.info('Message contains %i records', len(records))

        # Use the DB to load the records
        log.debug('Loading records...')
        self._apeldb.load_records(records, source=signer)

        log.debug('Records successfully loaded')
