#!/usr/bin/env python

# Migrate from the old apel client database to the new apel client database.

from __future__ import print_function
from builtins import str

from apel.common.parsing_utils import parse_fqan

import MySQLdb
import sys
import time
import datetime
import warnings

# how often to commit records to target database
COMMIT_THRESHOLD=500
SUMMARISE_THRESHOLD=10000

SPECINT = 'si2k'

# procedure used to insert each record into the new schema
CREATE_PROC = '''
CREATE PROCEDURE InsertJobRecord(
  site VARCHAR(255), submitHost VARCHAR(255), machineName VARCHAR(255),
  queue VARCHAR(100), localJobId VARCHAR(255),
  localUserId VARCHAR(255), globalUserName VARCHAR(255),
  fullyQualifiedAttributeName VARCHAR(255),
  vo VARCHAR(255),
  voGroup VARCHAR(255), voRole VARCHAR(255),
  wallDuration INT, cpuDuration INT, processors INT, nodeCount INT,
  startTime DATETIME, endTime DATETIME, infrastructureDescription VARCHAR(100), infrastructureType VARCHAR(20),
  memoryReal INT, memoryVirtual INT,
  serviceLevelType VARCHAR(50), serviceLevel DECIMAL(10,3),
  publisherDN VARCHAR(255))
BEGIN
    INSERT INTO JobRecords(SiteID, SubmitHostID, MachineNameID, QueueID,
LocalJobId, LocalUserId, GlobalUserNameID, FQAN,
        VOID, VOGroupID, VORoleID, WallDuration, CpuDuration, Processors, NodeCount,
        StartTime, EndTime, EndYear, EndMonth, InfrastructureDescription, InfrastructureType, MemoryReal, MemoryVirtual, ServiceLevelType,
        ServiceLevel, PublisherDNID)
    VALUES (
        SiteLookup(site), SubmitHostLookup(submitHost), MachineNameLookup(machineName),
        QueueLookup(queue), localJobId, localUserId,
        DNLookup(globalUserName), fullyQualifiedAttributeName, VOLookup(vo),
        VOGroupLookup(voGroup), VORoleLookup(voRole), wallDuration, cpuDuration,
        IFNULL(processors, 0), IFNULL(nodeCount, 0), startTime, endTime,
        YEAR(endTime), MONTH(endTime), infrastructureDescription, infrastructureType, memoryReal,
        memoryVirtual, serviceLevelType, serviceLevel, DNLookup(publisherDN)
        );
END'''

REMOVE_PROC = 'DROP PROCEDURE IF EXISTS InsertJobRecord'

SELECT_STMT = '''SELECT ExecutingSite, LocalJobID, LocalUserID, LCGUserVO, LcgUserID,
                ElapsedTimeSeconds, BaseCpuTimeSeconds, StartTimeUTC, StopTimeUTC,
                ExecutingCE, MemoryReal, MemoryVirtual, SpecInt2000
                from LcgRecords WHERE EventDate >= "%s"'''

CALLPROC_STMT = """CALL InsertJobRecord(%s, %s, %s, 'None', %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, NULL, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

DUPLICATES_JOIN = """ FROM JobRecords AS t
                      LEFT JOIN MachineNames as m
                      on (t.MachineNameID = m.id)
                      INNER JOIN (SELECT LocalJobId,
                                  EndTime
                                  FROM JobRecords
                                  LEFT JOIN MachineNames
                                  on (JobRecords.MachineNameID = MachineNames.id)
                                  WHERE MachineNames.name != 'MachineName' )
                                  AS u
                      ON (m.name = 'MachineName' AND t.LocalJobId = u.LocalJobId AND t.EndTime = u.EndTime); """

COUNT_DUPLICATES_STMT = "SELECT count(*) " + DUPLICATES_JOIN

DELETE_DUPLICATES_STMT = "DELETE t " + DUPLICATES_JOIN

def parse_timestamp(string, fmt="%Y-%m-%dT%H:%M:%SZ"):
    '''
    Method for parsing timestamp
    '''
    if string is None:
        return None

    return datetime.datetime(*time.strptime(string, fmt)[:-2])


def get_start_of_month(months_ago):
    '''
    We want to get the datetime corresponding to the start of a month.
    If <months_ago> = 0, get the start of the current month.
    If <months_ago> > 0, get the start of the month preceding the current
    month by <months_ago> months.
    '''
    today = datetime.datetime.utcnow().date()

    target_month = (today.month - months_ago) % 12
    if target_month == 0:
        target_month = 12

    target_year = today.year + (today.month - months_ago - 1) // 12

    midnight = datetime.time.min
    target_date = datetime.date(target_year, target_month, 1)
    start_of_target_month = datetime.datetime.combine(target_date, midnight)
    return start_of_target_month


def remove_proc(cursor):
    '''
    Drop the procedure used for inserting job records.  Ignore the warning
    that it doesn't exist.
    '''
    # copy warning filters
    original_filters = warnings.filters[:]
    # suppress warning when dropping procedure which doesn't exist
    warnings.simplefilter('ignore')
    cursor.execute(REMOVE_PROC)
    # restore warning filters
    warnings.filters = original_filters


def copy_records(db1, db2, cutoff):
    '''
    Copy all records from the LcgRecords table in db1 to the JobRecords
    table in db2 whose EndTime is greater than the cutoff datetime.
    '''
    c1 = db1.cursor(cursorclass=MySQLdb.cursors.SSCursor)
    c2 = db2.cursor()

    remove_proc(c2)
    c2.execute(CREATE_PROC)

    # extract records from source database into a cursor object
    c1.execute(SELECT_STMT % cutoff)

    counter = 0
    inserted = 0
    errors = {}
    start = time.time()
    batch_start = time.time()
    sys.stdout.write('% 21s % 12s\n' % ('Records processed', 'Time taken'))
    for r in c1:
        (site, jobid, userid, fqan, global_user_name, wall_duration, cpu_duration, start_time, end_time, submit_host, memory_real, memory_virtual, specint) = r

        role, group, vo = parse_fqan(fqan)

        if global_user_name == None:
            global_user_name = 'None'
        if role == None:
            role = 'None'
        if group == None:
            group = 'None'
        if vo == None:
            vo = 'None'

        start_time = parse_timestamp(start_time)
        end_time = parse_timestamp(end_time)

        try:
            c2.execute(CALLPROC_STMT, (site, submit_host, 'MachineName', jobid, userid, global_user_name,
                               fqan, vo, group, role, wall_duration , cpu_duration, start_time, end_time,
                               'migration_script', 'grid', memory_real, memory_virtual, SPECINT, specint, 'Import'))
            inserted += 1

        except Exception as err:
            try:
                # mysql code for duplicate record is 1062
                if err[0] == 1062:
                    err = 'Duplicate record not inserted'
                errors[str(err)] += 1
            except (KeyError, TypeError):
                errors[str(err)] = 1

        counter += 1
        if counter % COMMIT_THRESHOLD == 0:
            db2.commit()

        if counter % SUMMARISE_THRESHOLD == 0 and counter != 0:
            batch_stop = time.time()
            sys.stdout.write('% 13d % 15.3f\n' % (counter, batch_stop - batch_start))
            sys.stdout.flush()
            batch_start = time.time()

    sys.stdout.write('\n    %d of %d records copied in %.3f seconds.\n\n' % (inserted, counter, time.time() - start))
    db2.commit()

    for item in errors:

        sys.stderr.write("    Error: ")
        sys.stderr.write(str(item))
        sys.stderr.write(" occurred ")
        sys.stderr.write(str(errors[item]))
        sys.stderr.write(' times.\n')


def delete_old_records(db, cutoff):
    '''
    Delete all records in the JobRecords table whose EndTimes are before the
    cutoff datetime.
    '''
    c = db.cursor()

    c.execute('DELETE FROM JobRecords where date(EndTime) < "%s"' % cutoff)
    c.execute(REMOVE_PROC)
    db.commit()

def delete_duplicates(db):
    '''
    Delete all records that have been migrated but are duplicates of records
    that are in the database already
    '''
    c = db.cursor()

    c.execute(COUNT_DUPLICATES_STMT)
    num_duplicates = c.fetchone()[0]
    sys.stdout.write('    Found %d duplicate entries\n' % num_duplicates)

    sys.stdout.write('    Deleting duplicates\n')
    c.execute(DELETE_DUPLICATES_STMT)
    num_deleted = db.affected_rows()
    sys.stdout.write('    Deleted %d duplicate entries\n\n\n' % num_deleted)

    db.commit()

def main():
    '''
    Parse the commandline arguments, connect to the databases and start
    the copying and deleting processes.
    '''
    if len(sys.argv) != 4:
        print('Usage: '+sys.argv[0]+' <sourcedb> <destdb> <months_to_keep>')
        print('where:')
        print('     <sourcedb> - hostname:database_name:username:password')
        print('     <destdb> - as per source db')
        print('     <months_to_keep> - number of complete months\' data to retain')
        sys.exit()

    try:
        host1, dbname1, user1, pw1 = sys.argv[1].split(':')
        host2, dbname2, user2, pw2 = sys.argv[2].split(':')
    except (IndexError, ValueError):
        print('DB connection details must be in the format:')
        print('  hostname:database_name:username:password')
        sys.exit()

    try:
        months_to_keep = int(sys.argv[3])
    except ValueError:
        print('<months_to_keep> must be an integer')
        sys.exit()

    cutoff = get_start_of_month(months_to_keep)

    # connect to both databases
    try:
        db1 =  MySQLdb.connect(host=host1, db=dbname1, user=user1, passwd=pw1)
        db2 =  MySQLdb.connect(host=host2, db=dbname2, user=user2, passwd=pw2)
    except MySQLdb.Error as e:
        print('Error connecting to database: %s' % str(e))
        sys.exit()

    # copy records
    sys.stdout.write("\n\n    Copying all records newer than %s" % cutoff)
    sys.stdout.write("\n    from %s:%s to %s:%s ...\n\n" % (host1, dbname1, host2, dbname2))
    copy_records(db1, db2, cutoff)

    # delete records
    sys.stdout.write("\n    Deleting all records older than %s\n" % cutoff)
    sys.stdout.write("    from %s:%s ...\n" % (host2, dbname2))
    delete_old_records(db2, cutoff)
    sys.stdout.write("    Done.\n\n\n")

    # delete duplicates
    delete_duplicates(db2)
    sys.stdout.write("    Complete.\n\n\n")


if __name__ == '__main__':
    main()
