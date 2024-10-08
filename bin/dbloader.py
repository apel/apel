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

import sys
import os
import time
import logging.config
try:
    # Renamed ConfigParser to configparser in Python 3
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

from daemon.daemon import DaemonContext
from apel.db.loader import Loader, LoaderException
from apel.common import set_up_logging
from apel import __version__
from argparse import ArgumentParser
from optparse import OptionParser


log = None

def runprocess(db_config_file, config_file):
    '''Parse the configuration file and start the loader.'''

    # Read configuration from file
    cp = ConfigParser.ConfigParser()
    cp.read(config_file)

    dbcp = ConfigParser.ConfigParser()
    dbcp.read(db_config_file)

    # set up logging
    try:
        set_up_logging(cp.get('logging', 'logfile'), cp.get('logging', 'level'),
                       cp.getboolean('logging', 'console'))
        global log
        log = logging.getLogger('dbloader')
    except (ConfigParser.Error, ValueError, IOError) as err:
        print('Error configuring logging: %s' % err)
        print('The system will exit.')
        sys.exit(1)

    log.info('Starting apel dbloader version %s.%s.%s', *__version__)

    try:
        qpath = cp.get('loader', 'msgpath')
        db_backend = dbcp.get('db', 'backend')
        db_hostname = dbcp.get('db', 'hostname')
        db_port = int(dbcp.get('db', 'port'))
        db_name = dbcp.get('db', 'name')
        db_username = dbcp.get('db', 'username')
        db_password = dbcp.get('db', 'password')

        interval = cp.getint('loader', 'interval')

        pidfile = cp.get('loader', 'pidfile')

        save_msgs =  cp.getboolean('loader', 'save_messages')

    except Exception as err:
        print("Error in configuration file: %s" % err)
        sys.exit(1)

    # Create a Loader object
    try:
        if os.path.exists(pidfile):
            error = "Cannot start loader.  Pidfile %s already exists." % pidfile
            raise LoaderException(error)
        loader = Loader(qpath, save_msgs, db_backend, db_hostname, db_port, db_name, db_username, db_password, pidfile)
    except Exception as err:
        print("Error initialising loader: %s" % err)
        sys.exit(1)

    # Once it's initialised correctly, set it going.
    run_as_daemon(loader, interval)


def run_as_daemon(loader, interval):
    """
    Given a loader object, start it as a daemon process.
    """
    log.info("The loader will run as a daemon.")
    # We need to preserve the file descriptor for any log files.
    rootlogger = logging.getLogger()
    log_files = [x.stream for x in rootlogger.handlers]
    dc = DaemonContext(files_preserve=log_files)

    with DaemonContext(files_preserve=log_files):
        try:
            loader.startup()

            # every <interval> seconds, process the records in the incoming directory
            while True:
                loader.load_all_msgs()
                time.sleep(interval)

        except SystemExit as e:
            log.info("Received the shutdown signal: %s", e)
        except LoaderException as e:
            log.critical("An unrecoverable exception was thrown: %s", e)
        except Exception as e:
            log.exception("Unexpected exception. Traceback follows...")
        finally:
            log.info("The loader will shutdown.")
            loader.shutdown()

    log.info("=======================")



if __name__ == '__main__':

    ver = "Starting APEL dbloader %s.%s.%s" % __version__
    default_db_conf_location = '/etc/apel/db.cfg'
    default_conf_location = '/etc/apl/loader.cfg'
    arg_parser = ArgumentParser()

    arg_parser.add_argument('-d', '--db',
                            help='Location of DB',
                            default=default_db_conf_location)
    arg_parser.add_argument('-c', '--config',
                            help="Location of config file",
                            default=default_conf_location)
    arg_parser.add_argument('-l', '--log_config',
                            help='DEPRECATED - Location of logging config file (optional)',
                            default=None)
    arg_parser.add_argument('-v', '--version',
                            action='version',
                            version=ver)

    # Using the vars function to output a dict-like view rather than Namespace object.
    options = arg_parser.parse_args()

    # Deprecating functionality.
    if os.path.exists('/etc/apel/logging.cfg') or options['log_config'] is not None:
        logging.warning('Separate logging config file option has been deprecated.')

    runprocess(options['db'], options['config'])
