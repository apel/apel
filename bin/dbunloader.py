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
'''
   @author: Konrad Jopek, Will Rogers
'''

import logging.config
import sys
import os
from apel.common import set_up_logging
from apel.db import ApelDb, ApelDbException
from apel.db.unloader import DbUnloader
from apel import __version__
from optparse import OptionParser
import ConfigParser

    
if __name__ == '__main__':
    opt_parser = OptionParser()
    opt_parser.add_option('-d', '--db', help='location of configuration file for database',
                          default='/etc/apel/db.cfg')
    opt_parser.add_option('-c', '--config', help='Location of configuration file for dbunloader',
                          default='/etc/apel/unloader.cfg')
    opt_parser.add_option('-l', '--log_config', help='Location of logging configuration file for dbloader',
                          default='/etc/apel/logging.cfg')
    
    (options, args) = opt_parser.parse_args()
    
    cp = ConfigParser.ConfigParser()
    cp.read([options.config])
    
    # set up logging
    try:
        if os.path.exists(options.log_config):
            logging.config.fileConfig(options.log_config)
        else:
            set_up_logging(cp.get('logging', 'logfile'), 
                           cp.get('logging', 'level'),
                           cp.getboolean('logging', 'console'))
        log = logging.getLogger('dbunloader')
    except (ConfigParser.Error, ValueError, IOError), err:
        print 'Error configuring logging: %s' % str(err)
        print 'The system will exit.'
        sys.exit(1)
        
    db = None
    
    dbcp = ConfigParser.ConfigParser()
    dbcp.read([options.db])
    
    try:
        db = ApelDb(dbcp.get('db', 'backend'),
                    dbcp.get('db', 'hostname'),
                    dbcp.getint('db', 'port'),
                    dbcp.get('db', 'username'),
                    dbcp.get('db', 'password'),
                    dbcp.get('db', 'name'))
        
    except ApelDbException, e:
        log.fatal('Error: %s' % e)
        sys.exit(1)
    except Exception, e:
        log.fatal('Cannot get configuration: %s' % e)
        sys.exit(1)
    
    log.info('=====================')
    log.info('Starting APEL dbunloader %s.%s.%s' % __version__)
    
    unload_dir       = cp.get('unloader', 'dir_location')
    table_name       = cp.get('unloader', 'table_name')
    
    try:
        unloader_id = cp.getboolean('unloader', 'unloader_id')
    except ConfigParser.NoOptionError:
        unloader_id = 'sent'  #If the option is not defined we use the value that was used pre 1.1.3 for backwards compatibility
        
    try:
        send_ur = cp.getboolean('unloader', 'send_ur')
    except ConfigParser.NoOptionError:
        send_ur = False
        
    try:
        local_jobs = cp.getboolean('unloader', 'local_jobs')
    except ConfigParser.NoOptionError:
        local_jobs = False
        
    try:
        withhold_dns     = cp.getboolean('unloader', 'withhold_dns')
    except ConfigParser.NoOptionError:
        withhold_dns = False
        
    include_vos      = None
    exclude_vos      = None
    try:
        include_vos_parameter      = cp.get('unloader', 'include_vos')
        include_vos  = [ vo.strip() for vo in include_vos_parameter.split(',') ]
    except ConfigParser.NoOptionError:
        # Only exclude VOs if we haven't specified the ones to include.
        try:
            exclude_vos_parameter      = cp.get('unloader', 'exclude_vos')
            exclude_vos  = [ vo.strip() for vo in exclude_vos_parameter.split(',') ]
        except ConfigParser.NoOptionError:
            pass
    
    include_sites      = None
    exclude_sites      = None
    try:
        include_sites_parameter      = cp.get('unloader', 'include_sites')
        include_sites  = [ site.strip() for site in include_sites_parameter.split(',') ]
    except ConfigParser.NoOptionError:
        # Only exclude Sites if we haven't specified the ones to include.
        try:
            exclude_sites_parameter      = cp.get('unloader', 'exclude_sites')
            exclude_sites  = [ site.strip() for site in exclude_sites_parameter.split(',') ]
        except ConfigParser.NoOptionError:
            pass
    
    unloader = DbUnloader(db, unload_dir, include_vos, exclude_vos, local_jobs, withhold_dns, include_sites, exclude_sites, unloader_id)
    try:
        msgs, recs = unloader.unload_latest(table_name, send_ur)
        log.info('%d records in %d messages unloaded from %s' % (recs, msgs, table_name))
    except KeyError:
        log.error('Invalid table name: %s, omitting' % table_name)
    except ApelDbException, e:
        log.error('Unloading failed: %s' % e)
        
    log.info('Unloading complete.')
    log.info('=====================') 
