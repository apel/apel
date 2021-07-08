#!/usr/bin/env python

#   Copyright (C) 2012 STFC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# Module used to start and run the APEL loader.
'''
@author: Will Rogers
'''

from optparse import OptionParser
import ConfigParser
import logging.config
import os
import sys
import time

from apel.db import ApelDb, ApelDbException
from apel.common import set_up_logging, LOG_BREAK
from apel import __version__


def runprocess(db_config_file, config_file, log_config_file):
    '''Parse the configuration file, connect to the database and run the
       summarising process.'''

    # Store start time to log how long the summarising process takes
    start_time = time.time()

    try:
        # Read configuration from file
        cp = ConfigParser.ConfigParser()
        cp.read(config_file)

        pidfile = cp.get('summariser', 'pidfile')

        dbcp = ConfigParser.ConfigParser()
        dbcp.read(db_config_file)

        db_backend = dbcp.get('db', 'backend')
        db_hostname = dbcp.get('db', 'hostname')
        db_port = int(dbcp.get('db', 'port'))
        db_name = dbcp.get('db', 'name')
        db_username = dbcp.get('db', 'username')
        db_password = dbcp.get('db', 'password')

    except (ConfigParser.Error, ValueError, IOError), err:
        print 'Error in configuration file %s: %s' % (config_file, str(err))
        print 'The system will exit.'
        sys.exit(1)

    try:
        db_type = dbcp.get('db', 'type')
    except ConfigParser.Error:
        db_type = 'cpu'

    # set up logging
    try:
        if os.path.exists(log_config_file):
            logging.config.fileConfig(log_config_file)
        else:
            set_up_logging(cp.get('logging', 'logfile'),
                           cp.get('logging', 'level'),
                           cp.getboolean('logging', 'console'))
        log = logging.getLogger('summariser')
    except (ConfigParser.Error, ValueError, IOError), err:
        print 'Error configuring logging: %s' % str(err)
        print 'The system will exit.'
        sys.exit(1)

    log.info('Starting apel summariser version %s.%s.%s', *__version__)

    # If the pidfile exists, don't start up.
    try:
        if os.path.exists(pidfile):
            log.error("A pidfile %s already exists.", pidfile)
            log.warning("Check that the summariser is not running, then remove the file.")
            raise Exception("The summariser cannot start while pidfile exists.")
    except Exception, err:
        print "Error initialising summariser: %s" % err
        sys.exit(1)
    try:
        f = open(pidfile, "w")
        f.write(str(os.getpid()))
        f.write("\n")
        f.close()
    except IOError, e:
        log.warning("Failed to create pidfile %s: %s", pidfile, e)
        # If we fail to create a pidfile, don't start the summariser
        sys.exit(1)

    log.info('Created Pidfile')
    # Log into the database
    try:

        log.info('Connecting to the database ... ')
        db = ApelDb(db_backend, db_hostname, db_port, db_username, db_password, db_name)

        log.info('Connected.')
        # This is all the summarising logic, contained in ApelMysqlDb() and the stored procedures.
        if db_type == 'cpu':
            # Make sure that records are not coming from the same site by two different routes
            # N.B. Disabled as check doesn't scale well and isn't that useful.
            # db.check_duplicate_sites()
            db.summarise_jobs()
            db.normalise_summaries()
            db.copy_summaries()
        elif db_type == 'cloud':
            db.summarise_cloud()
        else:
            raise ApelDbException('Unknown database type: %s' % db_type)

        # Calculate end time to output time to logs
        elapsed_time = round(time.time() - start_time, 3)
        log.info('Summarising completed in: %s seconds', elapsed_time)

        log.info(LOG_BREAK)

    except ApelDbException, err:
        log.error('Error summarising: ' + str(err))
        log.error('Summarising has been cancelled.')
        sys.exit(1)
    finally:
        # Clean up pidfile regardless of any excpetions
        # This even executes if sys.exit() is called
        log.info('Removing Pidfile')
        try:
            if os.path.exists(pidfile):
                os.remove(pidfile)
            else:
                log.warning("pidfile %s not found.", pidfile)

        except IOError, e:
            log.warning("Failed to remove pidfile %s: %s", pidfile, e)
            log.warning("The summariser may not start again until it is removed.")

        log.info(LOG_BREAK)


if __name__ == '__main__':
    # Main method for running the summariser.

    ver = "APEL summariser %s.%s.%s" % __version__
    opt_parser = OptionParser(description=__doc__, version=ver)
    opt_parser.add_option('-d', '--db', help='the location of database config file',
                          default='/etc/apel/db.cfg')
    opt_parser.add_option('-c', '--config', help='the location of config file',
                          default='/etc/apel/summariser.cfg')
    opt_parser.add_option('-l', '--log_config', help='Location of logging config file (optional)',
                          default='/etc/apel/logging.cfg')
    (options,args) = opt_parser.parse_args()

    runprocess(options.db, options.config, options.log_config)
