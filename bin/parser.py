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

# APEL parser. This is an universal script which supports following systems:
# - BLAH
# - PBS
# - SGE
# - LSF

'''
    @author: Konrad Jopek, Will Rogers
'''

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from future.builtins import str

import logging.config
import os
import sys
import re
import gzip
import bz2
from argparse import ArgumentParser
try:
    # Renamed ConfigParser to configparser in Python 3
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

from apel import __version__
from apel.db import ApelDb, ApelDbException
from apel.db.records import ProcessedRecord
from apel.common import calculate_hash, set_up_logging, LOG_BREAK
from apel.common.exceptions import install_exc_handler, default_handler
from apel.parsers.blah import BlahParser
from apel.parsers.lsf import LSFParser
from apel.parsers.sge import SGEParser
from apel.parsers.pbs import PBSParser
from apel.parsers.slurm import SlurmParser
from apel.parsers.htcondor import HTCondorParser


LOGGER_ID = 'parser'
# How many records should be put/fetched to/from database
# in single query
BATCH_SIZE = 1000
DB_BACKEND = 'mysql'
PARSERS = {
           'PBS': PBSParser,
           'LSF': LSFParser,
           'SGE': SGEParser,
           'SLURM': SlurmParser,
           'blah' : BlahParser,
           'HTCondor': HTCondorParser,
           }


class ParserConfigException(Exception):
    '''
    Exception raised when parser is misconfigured.
    '''
    pass

def find_sub_dirs(dirpath):
    '''
    Given a directory path, return a list of paths of any subdirectories,
    including the directory itself.
    '''
    alldirs = []
    for root, unused_dirs, unused_files in os.walk(dirpath):
        alldirs.append(root)

    return alldirs


def parse_file(parser, apel_db, fp, replace):
    '''
    Parses file from blah/batch system

    @param parser: parser object of correct type
    @param apel_db: object to access APEL database
    @param fp: file object with log
    @return: number of correctly parsed files from file,
             total number of lines in file
    '''
    log = logging.getLogger(LOGGER_ID)
    records = []

    # we will save information about errors
    # default behaviour: show the list of errors with information
    # how many times given error was raised
    exceptions = {}

    line_number = 0
    parsed = 0
    failed = 0
    ignored = 0

    for line_number, line in enumerate(fp, start=1):
        line = line.decode('utf-8')

        try:
            record = parser.parse(line)
        except Exception as e:
            log.debug('Error %s on line %d', e, line_number)
            failed += 1
            if str(e) in exceptions:
                exceptions[str(e)] += 1
            else:
                exceptions[str(e)] = 1
        else:
            if record is not None:
                records.append(record)
                parsed += 1
            else:
                ignored += 1
            if len(records) % BATCH_SIZE == 0 and len(records) != 0:
                apel_db.load_records(records, replace=replace)
                del records
                records = []

    apel_db.load_records(records, replace=replace)

    if line_number == 1:
        log.info('Ignored empty file.')
    elif parsed == 0:
        log.warning('Failed to parse file.  Is %s correct?', parser.__class__.__name__)
    else:
        log.info('Parsed %d lines', parsed)
        log.info('Ignored %d lines (incomplete jobs)', ignored)
        log.info('Failed to parse %d lines', failed)

        for error in exceptions:
            log.error('%s raised %d times', error, exceptions[error])

    return parsed, line_number


def scan_dir(parser, dirpath, reparse, expr, apel_db, processed):
    '''
    Check all files in a directory and parse them if:
     - the names match the regular expression
     - the file is not already in the list of processed files

     Add newly parsed files to the processed files list and return it.
    '''
    skipped_warning_flag = False
    log = logging.getLogger(LOGGER_ID)
    updated = []
    try:
        log.info('Scanning directory: %s', dirpath)

        for item in sorted(os.listdir(dirpath)):
            abs_file = os.path.join(dirpath, item)
            if os.path.isfile(abs_file) and expr.match(item):
                # first, calculate the hash of the file:
                file_hash = calculate_hash(abs_file)
                found = False
                unparsed = False
                # next, try to find corresponding entry
                # in database
                for pf in processed:
                    if pf.get_field('Hash') == file_hash:
                        # we found corresponding record
                        # we will leave this record unmodified
                        updated.append(pf)
                        found = True
                        # Check for zero parsed lines so we can warn later on.
                        if pf.get_field('Parsed') == 0:
                            unparsed = True
                        break  # If we find a match, no need to keep checking.

                if reparse or not found:
                    try:
                        log.info('Parsing file: %s', abs_file)
                        # try to open as a bzip2 file, then as a gzip file,
                        # and if it fails try as a regular file
                        #
                        # bz2/gzip doesn't raise an exception when trying
                        # to open a non-gzip file.  Only a read (such as
                        # during parsing) does that.  For files of a wrong
                        # format we will get IOError, empty files can
                        # give EOFError as well.
                        for method in (bz2.BZ2File, gzip.open, open):
                            try:
                                with method(abs_file, 'rb') as fp:
                                    parsed, total = parse_file(parser, apel_db,
                                                               fp, reparse)
                                break
                            except (IOError, EOFError):
                                if method == open:
                                    raise
                    except IOError as e:
                        log.error('Cannot parse file %s: %s', item, e)
                    except ApelDbException as e:
                        log.error('Failed to parse %s due to a database problem: %s', item, e)
                    else:
                        pr = ProcessedRecord()
                        pr.set_field('HostName', parser.machine_name)
                        pr.set_field('Hash', file_hash)
                        pr.set_field('FileName', abs_file)
                        pr.set_field('StopLine', total)
                        pr.set_field('Parsed', parsed)
                        updated.append(pr)
                elif unparsed:
                    if not skipped_warning_flag:
                        log.info("Files skipped: rerun at DEBUG log level to see details.")
                        skipped_warning_flag = True
                    log.debug('Skipping file (failed to parse previously): %s',
                              abs_file)
                else:
                    if not skipped_warning_flag:
                        log.info("Files skipped: rerun at DEBUG log level to see details.")
                        skipped_warning_flag = True
                    log.debug('Skipping file (already parsed): %s ', abs_file)
            elif os.path.isfile(abs_file):
                log.debug('Filename does not match pattern: %s', item)

        return updated

    except KeyError as e:
        log.fatal('Improperly configured.')
        log.fatal('Check the section for %s , %s', parser, e)
        sys.exit(1)

def handle_parsing(log_type, apel_db, cp):
    '''
    Create the appropriate parser, and scan the configured directory
    for log files, parsing them.

    Update the database with the parsed files.
    '''
    log = logging.getLogger(LOGGER_ID)
    log.info('Setting up parser for %s files', log_type)
    if log_type == 'blah':
        section = 'blah'
    else:
        section = 'batch'

    site = cp.get('site_info', 'site_name')
    if site is None or site == '':
        raise ParserConfigException('Site name must be configured.')

    machine_name = cp.get('site_info', 'lrms_server')
    if machine_name is None or machine_name == '':
        raise ParserConfigException('LRMS hostname must be configured.')

    processed_files = []
    updated_files = []
    # get all processed records from generator
    for record_list in apel_db.get_records(ProcessedRecord):
        processed_files.extend(
                [record for record in record_list
                 if record.get_field('HostName') == machine_name])

    root_dir = cp.get(section, 'dir')

    try:
        reparse = cp.getboolean(section, 'reparse')
        if reparse:
            log.warning('Parser will reparse all logfiles found.')
    except ConfigParser.NoOptionError:
        reparse = False

    try:
        mpi = cp.getboolean(section, 'parallel')
    except ConfigParser.NoOptionError:
        mpi = False

    try:
        parser = PARSERS[log_type](site, machine_name, mpi)
    except (NotImplementedError) as e:
        raise ParserConfigException(e)
    except KeyError as e:
        raise ParserConfigException("Not a valid parser type: %s" % e)

    # Set parser specific options
    if log_type == 'LSF':
        try:
            parser.set_scaling(cp.getboolean('batch', 'scale_host_factor'))
        except ConfigParser.NoOptionError:
            log.warning("Option 'scale_host_factor' not found in section 'batch"
                        "'. Will default to 'false'.")
    elif log_type == 'SGE':
        try:
            parser.set_ms_timestamps(cp.getboolean('batch', 'ge_ms_timestamps'))
        except ConfigParser.NoOptionError:
            log.warning("Option 'ge_ms_timestamps' not found in section 'batch'"
                        " . Will default to 'false'.")

    # regular expressions for blah log files and for batch log files
    try:
        prefix = cp.get(section, 'filename_prefix')
        expr = re.compile('^' + prefix + '.*')
    except ConfigParser.NoOptionError:
        try:
            expr = re.compile(cp.get(section, 'filename_pattern'))
        except ConfigParser.NoOptionError:
            log.warning('No pattern specified for %s log file names.', log_type)
            log.warning('Parser will try to parse all files in directory')
            expr = re.compile('(.*)')

    if os.path.isdir(root_dir):
        if cp.getboolean(section, 'subdirs'):
            to_scan = find_sub_dirs(root_dir)
        else:
            to_scan = [root_dir]
        for directory in to_scan:
            updated_files.extend(scan_dir(parser, directory, reparse, expr, apel_db, processed_files))
    else:
        log.warning('Directory for %s logs was not set correctly, omitting', log_type)

    apel_db.load_records(updated_files)
    log.info('Finished parsing %s log files.', log_type)


def main():
    '''
    Parse command line arguments, do initial setup, then initiate
    parsing process.
    '''
    install_exc_handler(default_handler)

    ver = "APEL parser %s.%s.%s" % __version__

    default_conf_location = '/etc/apel/parser.cfg'
    arg_parser = ArgumentParser(description=__doc__)

    arg_parser.add_argument('-c', '--config',
                            help='Location of config file',
                            default=default_conf_location)
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

    # Read configuration from file
    try:
        cp = ConfigParser.ConfigParser()
        cp.read(options.config)
    except Exception as e:
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
        sys.exit(1)

    # set up logging
    try:
        set_up_logging(
            cp.get('logging', 'logfile'),
            cp.get('logging', 'level'),
            cp.getboolean('logging', 'console')
        )
    except (ConfigParser.Error, ValueError, IOError) as err:
        print('Error configuring logging: %s' % str(err))
        print('The system will exit.')
        sys.exit(1)

    log = logging.getLogger(LOGGER_ID)
    log.info(LOG_BREAK)
    log.info('Starting apel parser version %s.%s.%s', *__version__)

    # database connection
    try:
        apel_db = ApelDb(DB_BACKEND,
                         cp.get('db', 'hostname'),
                         cp.getint('db', 'port'),
                         cp.get('db', 'username'),
                         cp.get('db', 'password'),
                         cp.get('db', 'name'))
        apel_db.test_connection()
        log.info('Connection to DB established')
    except KeyError as e:
        log.fatal('Database configured incorrectly.')
        log.fatal('Check the database section for option: %s', e)
        sys.exit(1)
    except Exception as e:
        log.fatal("Database exception: %s", e)
        log.fatal('Parser will exit.')
        log.info(LOG_BREAK)
        sys.exit(1)

    log.info(LOG_BREAK)
    # blah parsing
    try:
        if cp.getboolean('blah', 'enabled'):
            handle_parsing('blah', apel_db, cp)
    except (ParserConfigException, ConfigParser.NoOptionError) as e:
        log.fatal('Parser misconfigured: %s', e)
        log.fatal('Parser will exit.')
        log.info(LOG_BREAK)
        sys.exit(1)

    log.info(LOG_BREAK)
    # batch parsing
    try:
        if cp.getboolean('batch', 'enabled'):
            handle_parsing(cp.get('batch', 'type'), apel_db, cp)
    except (ParserConfigException, ConfigParser.NoOptionError) as e:
        log.fatal('Parser misconfigured: %s', e)
        log.fatal('Parser will exit.')
        log.info(LOG_BREAK)
        sys.exit(1)

    log.info('Parser has completed.')
    log.info(LOG_BREAK)
    sys.exit(0)

if __name__ == '__main__':
    main()
