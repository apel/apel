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

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

from argparse import ArgumentParser
try:
    # Renamed ConfigParser to configparser in Python 3
    import configparser as ConfigParser
except ImportError:
    import ConfigParser
import logging.config
import os
import sys

from apel import __version__
from apel.common import set_up_logging
from apel.db import ApelDb, ApelDbException
from apel.db.unloader import DbUnloader

RECORDS_PER_MESSAGE_MIN = 1
RECORDS_PER_MESSAGE_DEFAULT = 1000
RECORDS_PER_MESSAGE_MAX = 5000


def _bounded_records_per_message(config_object, logger):
    """Retrieve the records per message from config, keeping it within limits."""
    try:
        records_per_message = int(config_object.get('unloader', 'records_per_message'))
        if records_per_message < RECORDS_PER_MESSAGE_MIN:
            logger.warning(
                'records_per_message too small, increasing from %d to %d',
                records_per_message,
                RECORDS_PER_MESSAGE_MIN,
            )
            return RECORDS_PER_MESSAGE_MIN
        elif records_per_message > RECORDS_PER_MESSAGE_MAX:
            logger.warning(
                'records_per_message too large, decreasing from %d to %d',
                records_per_message,
                RECORDS_PER_MESSAGE_MAX,
            )
            return RECORDS_PER_MESSAGE_MAX
        else:
            return records_per_message
    except ConfigParser.NoOptionError:
        logger.info(
            'records_per_message not specified, defaulting to %d.',
            RECORDS_PER_MESSAGE_DEFAULT,
        )
        return RECORDS_PER_MESSAGE_DEFAULT
    except ValueError:
        logger.error(
            'Invalid records_per_message value, must be a postive integer. Defaulting to %d.',
            RECORDS_PER_MESSAGE_DEFAULT,
        )
        return RECORDS_PER_MESSAGE_DEFAULT


if __name__ == '__main__':

    ver = 'Starting APEL dbunloader %s.%s.%s' % __version__
    default_db_conf_location = '/etc/apel/db.cfg'
    default_dbun_conf_location = '/etc/apel/unloader.cfg'
    arg_parser = ArgumentParser()

    arg_parser.add_argument('-d', '--db',
                            help='Location of config file for database',
                            default=default_db_conf_location)
    arg_parser.add_argument('-c', '--config',
                            help='Location of config file for dbunloader',
                            default=default_dbun_conf_location)
    arg_parser.add_argument('-l', '--log_config',
                            help='DEPRECATED - Location of logging config file for dbloader',
                            default=None)
    arg_parser.add_argument('-v', '--version',
                            action='version',
                            version=ver)

    # Parsing arguments into an argparse.Namespace object for structured access.
    options = arg_parser.parse_args()

    # Deprecating functionality.
    if os.path.exists('/etc/apel/logging.cfg') or options.log_config is not None:
        logging.warning('Separate logging config file option has been deprecated.')

    # Set default for newer options as they may not exist in config file.
    cp = ConfigParser.ConfigParser({'interval': 'latest', 'dict_benchmark_type': 'false'})
    cp.read([options.config])

    # set up logging
    try:
        set_up_logging(cp.get('logging', 'logfile'), cp.get('logging', 'level'),
                       cp.getboolean('logging', 'console'))
        log = logging.getLogger('dbunloader')
    except (ConfigParser.Error, ValueError, IOError) as err:
        print('Error configuring logging: %s' % err)
        print('The system will exit.')
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

    except ApelDbException as e:
        log.fatal('Error: %s', e)
        sys.exit(1)
    except Exception as e:
        log.fatal('Cannot get configuration: %s', e)
        sys.exit(1)

    log.info('=====================')
    log.info('Starting APEL dbunloader %s.%s.%s', *__version__)

    unload_dir       = cp.get('unloader', 'dir_location')
    table_name       = cp.get('unloader', 'table_name')
    dict_records     = cp.getboolean('unloader', 'dict_benchmark_type')

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
        include      = cp.get('unloader', 'include_vos')
        include_vos  = [ vo.strip() for vo in include.split(',') ]
    except ConfigParser.NoOptionError:
        # Only exclude VOs if we haven't specified the ones to include.
        try:
            exclude      = cp.get('unloader', 'exclude_vos')
            exclude_vos  = [ vo.strip() for vo in exclude.split(',') ]
        except ConfigParser.NoOptionError:
            pass

    interval = cp.get('unloader', 'interval')

    unloader = DbUnloader(db, unload_dir, include_vos, exclude_vos, local_jobs, withhold_dns, dict_records)

    unloader.records_per_message = _bounded_records_per_message(cp, log)

    try:
        if interval == 'latest':
            msgs, recs = unloader.unload_latest(table_name, send_ur)
        elif interval == 'gap':
            start = cp.get('unloader', 'gap_start')
            end = cp.get('unloader', 'gap_end')
            msgs, recs = unloader.unload_gap(table_name, start, end, send_ur)
        elif interval == 'all':
            msgs, recs = unloader.unload_all(table_name, send_ur)
        else:
            log.warning('Unrecognised interval: %s', interval)
            log.warning('Will not start unloader.')
        log.info('%d records in %d messages unloaded from %s', recs, msgs, table_name)
    except KeyError:
        log.error('Invalid table name: %s, omitting', table_name)
    except ApelDbException as e:
        log.error('Unloading failed: %s', e)

    log.info('Unloading complete.')
    log.info('=====================')
