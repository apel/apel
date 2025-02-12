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

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from future.builtins import str

from argparse import ArgumentParser
import datetime
import logging.config
import os
import sys
try:
    # Renamed ConfigParser to configparser in Python 3
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

from apel.db import ApelDb, ApelDbException
from apel.common import set_up_logging, LOG_BREAK
from apel import __version__


def runprocess(db_config_file, config_file):
    '''Parse the configuration file, connect to the database and run the
       summarising process.'''

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

    except (ConfigParser.Error, ValueError, IOError) as err:
        print('Error in configuration file %s: %s' % (config_file, str(err)))
        print('The system will exit.')
        sys.exit(1)

    try:
        db_type = dbcp.get('db', 'type')
    except ConfigParser.Error:
        db_type = 'cpu'

    # set up logging
    try:
        set_up_logging(cp.get('logging', 'logfile'), cp.get('logging', 'level'),
                       cp.getboolean('logging', 'console'))
        log = logging.getLogger('summariser')
    except (ConfigParser.Error, ValueError, IOError) as err:
        print('Error configuring logging: %s' % str(err))
        print('The system will exit.')
        sys.exit(1)

    log.info('Starting apel summariser version %s.%s.%s', *__version__)
    # Keep track of when this summariser run started to:
    # - log how long the summarising process takes,
    # - possibly identify stale summaries later.
    start_time = datetime.datetime.now()

    # If the pidfile exists, don't start up.
    try:
        if os.path.exists(pidfile):
            log.error("A pidfile %s already exists.", pidfile)
            log.warning("Check that the summariser is not running, then remove the file.")
            raise Exception("The summariser cannot start while pidfile exists.")
    except Exception as err:
        print("Error initialising summariser: %s" % err)
        sys.exit(1)
    try:
        with open(pidfile, "w") as f:
            f.write(str(os.getpid()))
            f.write("\n")
    except IOError as e:
        log.warning("Failed to create pidfile %s: %s", pidfile, e)
        # If we fail to create a pidfile, don't start the summariser
        sys.exit(1)

    log.info('Created Pidfile')

    # Configure options for stale summary clean up.
    try:
        stale_summary_clean_up = cp.getboolean('summariser',
                                               'delete_stale_summaries')

        stale_summary_age_limit_days = cp.getint('summariser',
                                                 'stale_summary_window_days')

    except ConfigParser.NoOptionError as _error:
        log.debug("No settings defined to clean up stale summaries.")
        stale_summary_clean_up = False
        stale_summary_age_limit_days = None

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
            # Optionally clean up any newly stale cloud summary records.
            if stale_summary_clean_up:
                db.clean_stale_cloud_summaries(start_time,
                                               stale_summary_age_limit_days)

        else:
            raise ApelDbException('Unknown database type: %s' % db_type)

        # Calculate end time to output time to logs
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        log.info('Summarising completed in: %s seconds',
                 round(elapsed_time, 3))

        log.info(LOG_BREAK)

    except ApelDbException as err:
        log.error('Error summarising: %s', err)
        log.error('Summarising has been cancelled.')
        sys.exit(1)
    finally:
        # Close the database connection before final cleanup
        db.db.close()
        # Clean up pidfile regardless of any excpetions
        # This even executes if sys.exit() is called
        log.info('Removing Pidfile')
        try:
            if os.path.exists(pidfile):
                os.remove(pidfile)
            else:
                log.warning("pidfile %s not found.", pidfile)

        except IOError as e:
            log.warning("Failed to remove pidfile %s: %s", pidfile, e)
            log.warning("The summariser may not start again until it is removed.")

        log.info(LOG_BREAK)


if __name__ == '__main__':
    # Main method for running the summariser.

    ver = "APEL summariser %s.%s.%s" % __version__
    default_db_conf_file = '/etc/apel/db.cfg'
    default_conf_file = '/etc/apel/summariser.cfg'
    arg_parser = ArgumentParser(description=__doc__)

    arg_parser.add_argument('-d', '--db',
                            help='Location of database config file',
                            default=default_db_conf_file)
    arg_parser.add_argument('-c', '--config',
                            help='Location of config file',
                            default=default_conf_file)
    arg_parser.add_argument('-l', '--log_config',
                            help='DEPRECATED - Location of logging config file',
                            default=None)
    arg_parser.add_argument('-v', '--version',
                            action='version',
                            version=ver)

    # Parsing arguments into an argparse.Namespace object for structured access.
    options = arg_parser.parse_args()

    # Deprecating functionality.
    if os.path.exists('/etc/apel/logging.cfg') or options.log_config is not None:
        logging.warning('Separate logging config file option has been deprecated.')

    runprocess(options.db, options.config)
