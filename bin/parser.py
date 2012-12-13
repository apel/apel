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

APEL2 parser. This is an universal script which supports following systems:
 - BLAH
 - PBS
 - SGE
 - LSF (5.x, 6.x, 7.x 8.x)
'''

import logging.config
import os
import sys
import re
import gzip
import ConfigParser
from optparse import OptionParser

from apel import __version__
from apel.db import ApelDb, ApelDbException
from apel.common import calculate_hash, set_up_logging
from apel.parsers import LOGGER_ID
from apel.parsers.blah import BlahParser
from apel.parsers.lsf import LSFParser
from apel.parsers.sge import SGEParser
from apel.parsers.pbs import PBSParser
from apel.parsers.slurm import SlurmParser
from apel.db.records import ProcessedRecord

log = None

def parse_file(log_type, cp, apel_db, batch_size, fp):
    '''
    Parses file from blah/batch system
    
    @param log_type: type of system (Blah, PBS, LSF, SGE)
    @param db_config: database configuration
    @param config: dictionary with config
    @param apel_db: object to access APEL database
    @param fp: file object with log
    @return: number of correctly parsed files from file, 
             total number of lines in file 
    '''
    
    parsers = {
               'PBS': PBSParser,
               'LSF': LSFParser,
               'SGE': SGEParser,
               'SLURM': SlurmParser,
               'Blah' : BlahParser
               }
    parser = parsers[log_type](siteName=cp.get('HostInfo', 'sitename'),
                        machineName=cp.get('HostInfo', 'lrmsserver'))
    
    records = []
    
    # we will save information about errors
    # default behaviour: show the list of errors with information
    # how many times given error was raised
    exceptions = {}
    
    fine = 0
    
    for i, line in enumerate(fp):
        try:
            record = parser.parse(line)
        except Exception, e:
            log.debug('Error %s on line %d' % (str(e), i))
            if exceptions.has_key(str(e)):
                exceptions[str(e)] += 1
            else:
                exceptions[str(e)] = 1
        else:
            if record is not None:
                records.append(record)
                fine += 1
            if len(records) % batch_size == 0 and len(records) != 0:
                apel_db.load_records(records)
                del records
                records = []
        
    
    apel_db.load_records(records)
    log.info('Parsed: %d/%d lines' % (fine, i+1))
    
    for error in exceptions:
        log.error('%s raised %d times' % (error, exceptions[error]))
    
    return fine, i

def scan_dir(log_type, dir_location, apel_db,
             batch_size, cp, processed_files,
             new_processed_db, hostname):
    # regular expressions for blah log files and for batch log files
    try:
        if log_type == 'Blah':
            expr = re.compile(cp.get('Blah', 'pattern'))
        else:
            expr = re.compile(cp.get('Batch', 'pattern'))
    except ConfigParser.NoOptionError:
        log.warning('Cannot find pattern for files for: %s' % log_type)
        log.warning('Parser will try to parse all files in directory')
        expr = re.compile('(.*)')
        
    try:
        log.info('Parsing %s files' % log_type)
        log.info('Directory: %s' % dir_location)
        
        for item in os.listdir(dir_location):
            abs_file = os.path.join(dir_location, item)
            if os.path.isfile(abs_file) and expr.match(item):
                gz = abs_file.endswith('.gz')
                
                # firstly we calculate the hash
                # for file:
                file_hash = calculate_hash(abs_file, gz)
                found = False
                # next, try to find corresponding entry
                # in database
                for pf in processed_files:
                    if pf.get_field('Hash') == file_hash:
                        # we found corresponding record
                        # we will leave this record unmodified
                        new_processed_db.append(pf)
                        found = True
                        log.info('File: %s already parsed, omitting' % abs_file)
                        
                if not found:
                    try:
                        log.info('Parsing file: %s' % abs_file)
                        if gz:
                            fp = gzip.open(abs_file)
                        else:
                            fp = open(abs_file, 'r')
                        parsed, total = parse_file(log_type, cp, apel_db, batch_size, fp)
                        fp.close()
                    except IOError, e:
                        log.error('Cannot open file %s due to: %s' % 
                                     (item, str(e)))
                    except ApelDbException, e:
                        log.error('Failed to parse %s due to a database problem: %s' % (item, e))
                    else:
                        pr = ProcessedRecord()
                        pr.set_field('HostName', hostname)
                        pr.set_field('Hash',file_hash)
                        pr.set_field('FileName', abs_file)
                        pr.set_field('StopLine', total)
                        pr.set_field('Parsed', parsed)
                        new_processed_db.append(pr)
                        
            else:
                log.info('Not a regular file: %s [omitting]' % item)
                
        log.info('%s log files parsed correctly' % log_type)
    except KeyError, e:
        log.fatal('Improperly configured.')
        log.fatal('Check the section for %s parser, %s' % (log_type, str(e)))
        sys.exit(1)
    

def main():
    
    opt_parser = OptionParser(description=__doc__, version=__version__)
    opt_parser.add_option("-c", "--config", help="the location of config file", 
                          default="/etc/apel/parser.cfg")
    opt_parser.add_option("-l", "--log_config", help="the location of logging config file", 
                          default="/etc/apel/parserlog.cfg")
    (options,_) = opt_parser.parse_args()
    
    config = None
    blah_dir, batch_dir = '', ''
    
    # Read configuration from file 
    try:
        cp = ConfigParser.ConfigParser()
        cp.read(options.config) 
    except Exception, e:
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
        sys.exit(1)
    
    # set up logging
    try:
        if os.path.exists(options.log_config):
            logging.config.fileConfig(options.log_config)
        else:
            set_up_logging(cp.get('logging', 'logfile'), 
                           cp.get('logging', 'level'),
                           cp.getboolean('logging', 'console'))
    except (ConfigParser.Error, ValueError, IOError), err:
        print 'Error configuring logging: %s' % str(err)
        print 'The system will exit.'
        sys.exit(1)

    global log
    log = logging.getLogger('parser')
    log.info('Starting apel parser version %s.%s.%s' % __version__)

    # database connection
    try:
        apel_db = ApelDb(cp.get('db', 'backend'),
                         cp.get('db', 'hostname'),
                         cp.getint('db', 'port'),
                         cp.get('db', 'username'),
                         cp.get('db', 'password'),
                         cp.get('db', 'name'))
        apel_db.test_connection()
        log.info('Connection to DB established')
    except KeyError, e:
        log.fatal('Improperly configured.');
        log.fatal('Check the database section for option: %s' % str(e))
        sys.exit(1)
    except Exception, e:
        log.fatal("Database exception: %s" % str(e))
        sys.exit(1)

    try:
        site = cp.get('HostInfo', 'sitename')
        hostname = cp.get('HostInfo', 'lrmsserver')
        slt = cp.get('HostInfo', 'serviceleveltype')
        sl = cp.getfloat('HostInfo', 'servicelevel')
        
        apel_db.update_spec(site, hostname, slt, sl)
        log.info("Updating benchmark information for local jobs:") 
        log.info("%s, %s, %s, %s." % (site, hostname, slt, sl))
    except KeyError, e:
        log.fatal('Cannot find submithost in configuration file')
        log.fatal('Check the HostInfo section for option: %s' % str(e))
        sys.exit(1)

    # find files which have been already parsed    
    processed_files = []
    new_db = []
    for record_list in apel_db.get_records(ProcessedRecord):
        processed_files += filter(lambda record: record.get_field('HostName') == hostname, 
                                  record_list)
        
    # No of records inserted in one go.
    batch_size = 1000
        
    if cp.getboolean('Blah', 'enabled'):
        if os.path.isdir(cp.get('Blah', 'dir')):
            blah_dir = cp.get('Blah', 'dir')
            scan_dir('Blah', blah_dir, apel_db,
                     batch_size, cp, processed_files,
                     new_db, hostname)
    # parse batch files
        else:
            log.warn('Directory with BLAH logs was not set correctly, omitting')

    if cp.getboolean('Batch', 'enabled'):
        if os.path.isdir(cp.get('Batch', 'dir')):
            batch_dir = cp.get('Batch', 'dir')
            scan_dir(cp.get('Batch', 'type'), batch_dir, apel_db,
                     batch_size, cp, processed_files,
                     new_db, hostname)
        else:
            log.warn('Directory with batch logs was not set correctly, omitting')    
    
    
    # save the current state
    apel_db.clean_processed_files(hostname)
    apel_db.load_records(new_db, None)
    
    sys.exit(0)
    
if __name__ == '__main__':
    main()
