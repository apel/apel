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

try:
    # Renamed ConfigParser to configparser in Python 3
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

import logging.config
from optparse import OptionParser
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
    opt_parser = OptionParser()
    opt_parser.add_option('-d', '--db', help='location of configuration file for database',
                          default='/etc/apel/db.cfg')
    opt_parser.add_option('-c', '--config', help='Location of configuration file for dbunloader',
                          default='/etc/apel/unloader.cfg')
    opt_parser.add_option('-l', '--log_config', help='Location of logging configuration file for dbloader',
                          default='/etc/apel/logging.cfg')

    (options, args) = opt_parser.parse_args()

    # Set default for 'interval' as it is a new option so may not be in config.
    cp = ConfigParser.ConfigParser({'interval': 'latest'})
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

    unloader = DbUnloader(db, unload_dir, include_vos, exclude_vos, local_jobs, withhold_dns)

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
