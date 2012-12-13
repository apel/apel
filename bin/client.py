#!/usr/bin/env python
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
   
   @author: Konrad Jopek

Main script for Apel Client.
The order of execution is as follows:
 - fetch benchmark information from LDAP database
 - join EventRecords and BlahdRecords into JobRecords
 - summarise jobs
 - unload JobRecords or SummaryRecords into filesystem
 - send data to server using SSM
 
'''
    
from optparse import OptionParser
import ConfigParser
import sys
import os
import logging.config
import ldap

from apel.db import ApelDb
from apel import __version__
from apel.db.records import JobRecord, SummaryRecord, SyncRecord
from apel.ldap import fetch_specint
from apel.db.unloader import DbUnloader
from apel.common import set_up_logging

from ssm.brokers import StompBrokerGetter, STOMP_SERVICE
from ssm.ssm2 import Ssm2, Ssm2Exception


def run_ssm(ssm_cfg, log):
    cp = ConfigParser.ConfigParser()
    cp.read(ssm_cfg)
    
    bg = StompBrokerGetter(cp.get('broker','bdii'))
    brokers = bg.get_broker_hosts_and_ports(STOMP_SERVICE, cp.get('broker','network'))
    
    try:
        server_cert = cp.get('certificates','server')
    except ConfigParser.NoOptionError:
        server_cert = None
        
    
    ssm = Ssm2(brokers, 
               cp.get('messaging','path'),
               dest=cp.get('messaging','destination'),
               cert=cp.get('certificates','certificate'),
               key=cp.get('certificates','key'),
               enc_cert=server_cert)
    
    ssm.handle_connect()
    
    ssm.send_all()
    
    log.info('SSM run has finished.')
    
    ssm.close_connection()
    
    log.info('Sending SSM has shut down.')
    log.info('========================================')

def main():
    
    opt_parser = OptionParser(version=__version__, description=__doc__)
    
    opt_parser.add_option('-c', '--config',
                          help='main configuration file for APEL',
                          default='/etc/apel/client.cfg')
    
    opt_parser.add_option('-l', '--log_config', 
                          help='the location of logging config file',
                          default='/etc/apel/logging.cfg')
    
    opt_parser.add_option('-s', '--ssm_config', 
                          help='the location of SSM config file',
                          default='/etc/apel/sender.cfg')
    
    options, _ = opt_parser.parse_args()
    cp     = ConfigParser.ConfigParser()
    cp.read(options.config)

    # set up logging
    try:
        if os.path.exists(options.log_config):
            logging.config.fileConfig(options.log_config)
        else:
            set_up_logging(cp.get('logging', 'logfile'), 
                           cp.get('logging', 'level'),
                           cp.getboolean('logging', 'console'))
        log = logging.getLogger('client')
    except (ConfigParser.Error, ValueError, IOError), err:
        print 'Error configuring logging: %s' % str(err)
        print 'The system will exit.'
        sys.exit(1)
        
    try:
        spec_updater_enabled = cp.getboolean('spec_updater', 'enabled')
        if spec_updater_enabled:
            sitename         = cp.get('spec_updater', 'site_name')
            ldap_host        = cp.get('spec_updater', 'ldap_host')
            ldap_port        = int(cp.get('spec_updater', 'ldap_port'))
        joiner_enabled       = cp.getboolean('joiner', 'enabled')
        local_jobs           = cp.getboolean('joiner', 'local_jobs')
        unloader_enabled     = cp.getboolean('unloader', 'enabled')
        
        include_vos = None
        exclude_vos = None
        if unloader_enabled:
            unload_dir       = cp.get('unloader', 'dir_location')
            table_name       = cp.get('unloader', 'table_name')
            send_ur          = cp.getboolean('unloader', 'send_ur')
            try:
                include      = cp.get('unloader', 'include_vos')
                include_vos  = [ vo.strip() for vo in include.split(',') ]
            except ConfigParser.NoOptionError:
                # Only exclude VOs if we haven't specified the ones to include.
                include_vos = None
                try:
                    exclude      = cp.get('unloader', 'exclude_vos')
                    exclude_vos  = [ vo.strip() for vo in exclude.split(',') ]
                except ConfigParser.NoOptionError:
                    exclude_vos = None
                    
        ssm_enabled          = cp.getboolean('ssm', 'enabled')
        if ssm_enabled:
            ssm_conf_file    = options.ssm_config
            
    except ConfigParser.Error, err:
        log.error('Error in configuration file: ' + str(err))
        sys.exit(1)
   
    log.info('Starting apel client version %s.%s.%s' % __version__)
        
    # Log into the database
    try:
        db_backend  = cp.get('db', 'backend')
        db_hostname = cp.get('db', 'hostname')
        db_port     = cp.getint('db', 'port')
        db_name     = cp.get('db', 'name')
        db_username = cp.get('db', 'username')
        db_password = cp.get('db', 'password')
        
        log.info('Connecting to the database ... ')
        db = ApelDb(db_backend, db_hostname, db_port, db_username, db_password, db_name) 
        log.info('Connected.')

    except (ConfigParser.Error, Exception), err:
        log.error('Error during connecting to database: ' + str(err))
        log.info('=====================')
        sys.exit(1)

    if spec_updater_enabled:
        log.info('=====================')#
        log.info('Starting spec updater.')
        try:
            spec_values = fetch_specint(sitename, ldap_host, ldap_port)
            for value in spec_values:
                db.update_spec(sitename, value[0], 'si2k', value[1])
            log.info('Spec updater finished.')
        except ldap.SERVER_DOWN, e:
            log.warn('Failed to fetch spec info: %s' % e)
            log.warn('Spec updater failed.')
        except ldap.NO_SUCH_OBJECT, e:
            log.warn('Found no spec values in BDII: %s' % e)
            log.warn('Is the site name %s correct?' % sitename)
        log.info('=====================')
        
    if joiner_enabled:
        log.info('=====================')
        log.info('Starting joiner.')
        # This contains all the joining logic, contained in ApelMysqlDb() and the stored procedures.
        db.join_records()
        if local_jobs:
            db.create_local_jobs()
        log.info('Joining complete.')
        log.info('=====================')
    
    # Always summarise - we need the summaries for the sync messages.
    log.info('=====================')
    log.info('Starting summariser.')
    # This contains all the summarising logic, contained in ApelMysqlDb() and the stored procedures.
    db.summarise()
    log.info('Summarising complete.')
    log.info('=====================')
    
    if unloader_enabled:
        log.info('=====================')
        log.info('Starting unloader.')
        
        log.info('Will unload from %s.' % table_name)
        
        interval = cp.get('unloader', 'interval')
        
        unloader = DbUnloader(db, unload_dir, include_vos, exclude_vos, local_jobs)
        try:
            if interval == 'latest':
                msgs, recs = unloader.unload_latest(table_name, send_ur)
            elif interval == 'gap':
                start = cp.get('unloader', 'gap-start')
                end = cp.get('unloader', 'gap-end')
                msgs, recs = unloader.unload_gap(table_name, start, end, send_ur)
            elif interval == 'all':
                msgs, recs = unloader.unload_all(table_name, send_ur)
            else:
                log.warn('Unrecognised interval: %s' % interval)
                log.warn('Will not start unloader.')
        except KeyError:
            log.warning('Invalid table name: %s, omitting' % table_name)
            
        log.info('Unloaded %d records in %d messages.' % (recs, msgs))
            
        # Always send sync messages
        msgs, recs = unloader.unload_all('VSyncRecords', False)
        
        log.info('Unloaded %d sync records in %d messages.' % (recs, msgs))
        
        log.info('Unloading complete.')
        log.info('=====================')
        

    if ssm_enabled:
        log.info('=====================')
        log.info('Starting SSM.')
        run_ssm(ssm_conf_file, log)
        log.info('SSM stopped.')
        log.info('=====================')
    
    log.info('Client finished')


if __name__ == '__main__':
    main()