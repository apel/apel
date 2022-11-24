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

#   Main script for APEL client.
#   The order of execution is as follows:
#    - fetch benchmark information from LDAP database
#    - join EventRecords and BlahdRecords into JobRecords
#    - summarise jobs
#    - unload JobRecords or SummaryRecords into filesystem
#    - send data to server using SSM
'''
   @author: Konrad Jopek, Will Rogers
'''

from optparse import OptionParser
import sys
import os
import logging.config
import ldap

try:
    import ConfigParser
except ImportError:
    # Renamed in Python 3
    import configparser as ConfigParser

from apel import __version__
from apel.db import ApelDb, ApelDbException
from apel.db.unloader import DbUnloader
from apel.ldap import fetch_specint
from apel.common import set_up_logging
from apel.common.exceptions import install_exc_handler, default_handler
import ssm.agents


DB_BACKEND = 'mysql'
LOGGER_ID = 'client'
LOG_BREAK = '====================='


class ClientConfigException(Exception):
    '''
    Exception raised if client is misconfigured.
    '''
    pass


def run_ssm(scp):
    """Run the SSM according to the values in the ConfigParser object."""
    log = logging.getLogger(LOGGER_ID)

    protocol = ssm.agents.get_protocol(scp, log)
    log.info('Setting up SSM with protocol: %s', protocol)
    brokers, project, token = ssm.agents.get_ssm_args(protocol, scp, log)
    ssm.agents.run_sender(protocol, brokers, project, token, scp, log)


def run_client(ccp):
    '''
    Run the client according to the configuration in the ConfigParser
    object.
    '''
    log = logging.getLogger(LOGGER_ID)

    try:
        spec_updater_enabled = ccp.getboolean('spec_updater', 'enabled')
        joiner_enabled = ccp.getboolean('joiner', 'enabled')

        if spec_updater_enabled or joiner_enabled:
            site_name = ccp.get('spec_updater', 'site_name')
            if site_name == '':
                raise ClientConfigException('Site name must be configured.')

        if spec_updater_enabled:
            ldap_host = ccp.get('spec_updater', 'ldap_host')
            ldap_port = int(ccp.get('spec_updater', 'ldap_port'))
        local_jobs = ccp.getboolean('joiner', 'local_jobs')
        if local_jobs:
            hostname = ccp.get('spec_updater', 'lrms_server')
            if hostname == '':
                raise ClientConfigException('LRMS server hostname must be '
                                            'configured if local jobs are '
                                            'enabled.')

            slt = ccp.get('spec_updater', 'spec_type')
            sl = ccp.getfloat('spec_updater', 'spec_value')

        unloader_enabled = ccp.getboolean('unloader', 'enabled')

        include_vos = None
        exclude_vos = None
        if unloader_enabled:
            unload_dir = ccp.get('unloader', 'dir_location')
            if ccp.getboolean('unloader', 'send_summaries'):
                table_name = 'VSuperSummaries'
            else:
                table_name = 'VJobRecords'
            send_ur = ccp.getboolean('unloader', 'send_ur')
            try:
                include = ccp.get('unloader', 'include_vos')
                include_vos = [vo.strip() for vo in include.split(',')]
            except ConfigParser.NoOptionError:
                # Only exclude VOs if we haven't specified the ones to include.
                include_vos = None
                try:
                    exclude = ccp.get('unloader', 'exclude_vos')
                    exclude_vos = [vo.strip() for vo in exclude.split(',')]
                except ConfigParser.NoOptionError:
                    exclude_vos = None

    except (ClientConfigException, ConfigParser.Error), err:
        log.error('Error in configuration file: %s', err)
        sys.exit(1)

    log.info('Starting apel client version %s.%s.%s', *__version__)

    # Log into the database
    try:
        db_hostname = ccp.get('db', 'hostname')
        db_port = ccp.getint('db', 'port')
        db_name = ccp.get('db', 'name')
        db_username = ccp.get('db', 'username')
        db_password = ccp.get('db', 'password')

        log.info('Connecting to the database ... ')
        db = ApelDb(DB_BACKEND, db_hostname, db_port,
                    db_username, db_password, db_name)
        db.test_connection()
        log.info('Connected.')

    except (ConfigParser.Error, ApelDbException), err:
        log.error('Error during connecting to database: %s', err)
        log.info(LOG_BREAK)
        sys.exit(1)

    log.info('Running manual spec update.')
    specs = []
    index = 1
    while True:
        key = 'manual_spec' + str(index)
        try:
            spec = ccp.get('spec_updater', key)
        except ConfigParser.NoOptionError:
            break
        specs.append(spec)
        index += 1

    if len(specs) > 0:
        try:
            s = ccp.get('spec_updater', 'site_name')
        except ConfigParser.NoOptionError:
            log.error('Site name must be configured '
                      'for manual_spec definitions.')
            sys.exit(1)
        for spec in specs:
            parts = spec.split(',')
            if len(parts) != 3:
                log.warning('Check manual_spec definitions.')
            try:
                sl = float(parts[2])
            except ValueError:
                log.error('Service level must be a number '
                          'for manual_spec definitions.')
                sys.exit(1)
            ce = parts[0]
            slt = parts[1]
            db.update_spec(s, ce, slt, sl)
    log.info('Manual spec update finished. %s updated.', len(specs))

    if spec_updater_enabled:
        log.info(LOG_BREAK)
        log.info('Starting spec updater.')
        try:
            spec_values = fetch_specint(site_name, ldap_host, ldap_port)
            for value in spec_values:
                db.update_spec(site_name, value[0], 'si2k', value[1])
            log.info('Spec updater finished.')
        except ldap.SERVER_DOWN, e:
            log.warning('Failed to fetch spec info: %s', e)
            log.warning('Spec updater failed.')
        except ldap.NO_SUCH_OBJECT, e:
            log.warning('Found no spec values in BDII: %s', e)
            log.warning('Is the site name %s correct?', site_name)

        log.info(LOG_BREAK)

    if joiner_enabled:
        log.info(LOG_BREAK)
        log.info('Starting joiner.')
        # This contains all the joining logic, contained in ApelMysqlDb() and
        # the stored procedures.
        if local_jobs:
            log.info('Updating benchmark information for local jobs:')
            log.info('%s, %s, %s, %s.', site_name, hostname, slt, sl)
            db.update_spec(site_name, hostname, slt, sl)
            log.info('Creating local jobs.')
            db.create_local_jobs()

        db.join_records()
        log.info('Joining complete.')
        log.info(LOG_BREAK)

    # Always summarise - we need the summaries for the sync messages.
    log.info(LOG_BREAK)
    log.info('Starting summariser.')
    # This contains all the summarising logic, contained in ApelMysqlDb() and
    # the stored procedures.
    db.summarise_jobs()
    log.info('Summarising complete.')
    log.info(LOG_BREAK)

    if unloader_enabled:
        log.info(LOG_BREAK)
        log.info('Starting unloader.')

        log.info('Will unload from %s.', table_name)

        interval = ccp.get('unloader', 'interval')
        withhold_dns = ccp.getboolean('unloader', 'withhold_dns')

        unloader = DbUnloader(db, unload_dir, include_vos, exclude_vos,
                              local_jobs, withhold_dns)
        try:
            if interval == 'latest':
                msgs, recs = unloader.unload_latest(table_name, send_ur)
            elif interval == 'gap':
                start = ccp.get('unloader', 'gap_start')
                end = ccp.get('unloader', 'gap_end')
                msgs, recs = unloader.unload_gap(table_name, start, end, send_ur)
            elif interval == 'all':
                msgs, recs = unloader.unload_all(table_name, send_ur)
            else:
                log.warning('Unrecognised interval: %s', interval)
                log.warning('Will not start unloader.')

            if recs > 0:
                log.info('Unloaded %d records in %d messages.', recs, msgs)
            else:
                log.warning('No usage records unloaded. If this is unexpected,'
                            ' please check your config.')

        except KeyError:
            log.warning('Invalid table name: %s, omitting', table_name)
        except ApelDbException, e:
            log.warning('Failed to unload records successfully: %s', e)

        # Always send sync messages
        msgs, recs = unloader.unload_sync()

        if recs > 0:
            log.info('Unloaded %d sync records in %d messages.', recs, msgs)
        else:
            log.warning('No sync records unloaded. If this is unexpected,'
                        ' please check your config.')

        log.info('Unloading complete.')
        log.info(LOG_BREAK)


def main():
    '''
    Parse command line arguments, set up logging and begin the client
    workflow.
    '''
    install_exc_handler(default_handler)
    ver = 'APEL client %s.%s.%s' % __version__
    opt_parser = OptionParser(version=ver, description=__doc__)
    default_conf_location = '/etc/apel/client.cfg'
    default_ssmconf_location = '/etc/apel/sender.cfg'
    default_log_location = '/etc/apel/logging.cfg'

    opt_parser.add_option('-c', '--config',
                          help=('main configuration file for APEL, '
                                'default path: ' + default_conf_location),
                          default=default_conf_location)

    opt_parser.add_option('-s', '--ssm_config',
                          help=('location of SSM config file, '
                                'default path: ' + default_ssmconf_location),
                          default=default_ssmconf_location)

    opt_parser.add_option('-l', '--log_config',
                          help=('location of logging config file (optional), '
                                'default path: ' + default_log_location),
                          default=default_log_location)

    options, unused_args = opt_parser.parse_args()

    # check if config file exists using os.path.isfile fuction
    if os.path.isfile(options.config):
        ccp = ConfigParser.ConfigParser()
        ccp.read(options.config)
    else:
        print("Config file not found at", options.config)
        exit(1)

    # check if ssm config file exists using os.path.isfile function
    if os.path.isfile(options.ssm_config):
        scp = ConfigParser.ConfigParser()
        scp.read(options.ssm_config)
    else:
        print("SSM config file not found at", options.ssm_config)
        exit(1)

    # set up logging
    try:
        if os.path.exists(options.log_config):
            logging.config.fileConfig(options.log_config)
        else:
            set_up_logging(ccp.get('logging', 'logfile'),
                           ccp.get('logging', 'level'),
                           ccp.getboolean('logging', 'console'))
        log = logging.getLogger(LOGGER_ID)
    except (ConfigParser.Error, ValueError, IOError), err:
        print 'Error configuring logging: %s' % str(err)
        print 'The system will exit.'
        sys.exit(1)

    run_client(ccp)

    if ccp.getboolean('ssm', 'enabled'):
        # Send unloaded messages
        log.info(LOG_BREAK)
        log.info('Starting SSM.')
        try:
            run_ssm(scp)
        except SystemExit as e:
            if e.code == 1:
                log.error('SSM failed to run.')
            else:
                log.critical('Unexpected SystemExit. See traceback below.')
                raise e
        else:
            log.info('SSM stopped.')
        log.info(LOG_BREAK)

    log.info('Client finished')


if __name__ == '__main__':
    main()
