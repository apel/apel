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

from apel.db import ApelDb, ApelDbException
from apel.common import set_up_logging
from apel import __version__

def runprocess(db_config_file, config_file, log_config_file):
    '''Parse the configuration file, connect to the database and run the 
       summarising process.'''

    try:
        # Read configuration from file
        cp = ConfigParser.ConfigParser()
        cp.read(config_file)
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
        if os.path.exists(options.log_config):
            logging.config.fileConfig(options.log_config)
        else:
            set_up_logging(cp.get('logging', 'logfile'), 
                           cp.get('logging', 'level'),
                           cp.getboolean('logging', 'console'))
        log = logging.getLogger('summariser')
    except (ConfigParser.Error, ValueError, IOError), err:
        print 'Error configuring logging: %s' % str(err)
        print 'The system will exit.'
        sys.exit(1)
        
    log.info('Starting apel summariser version %s.%s.%s' % __version__)
        
    # Log into the database
    try:

        log.info('Connecting to the database ... ')
        db = ApelDb(db_backend, db_hostname, db_port, db_username, db_password, db_name) 
   
        log.info('Connected.')
        # This is all the summarising logic, contained in ApelMysqlDb() and the stored procedures.
        if db_type == 'cpu':
            db.summarise()
        elif db_type == 'cloud':
            db.summarise_cloud()
        else:
            raise ApelDbException('Unknown database type: %s' % db_type)
        
        log.info('Summarising complete.')
        log.info('=====================')

    except Exception, err:
        log.error('Error summarising: ' + str(err))
        log.error('Summarising has been cancelled.')
        log.info('=====================')
        sys.exit(1)


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

