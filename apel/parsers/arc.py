from apel.common.datetime_utils import parse_timestamp
from apel.db.records.job import JobRecord
from apel.parsers import Parser


class ARCParser(Parser):
    """
    Parser for ARC accounting records.

    This parser differs from most of the others as ARC saves each accounting
    record in a separate file.
    """
    def parse_arc_file(self, arcfile):
        """
        Parse an ARC accounting file.

        Takes an open ARC accounting file object and returns a JobRecord and the
        number of lines in it.
        """
        arcjob = {}
        lines = 0
        for line in arcfile:
            # Remove any leading or trailing whitespace including newlines.
            line = line.strip()
            lines += 1
            key, value = line.split('=', 1)
            arcjob[key] = value

        if lines == 0 or 'status' not in arcjob or arcjob['status'] != "completed":
            # Empty file, incomplete job, or failed job (respectively)
            return None, lines

        arcjob['accounting_options'] = self.parse_accounting_options(arcjob['accounting_options'])

        apeljob = {}
        apeljob['Site'] = arcjob['accounting_options']['gocdb_name']
        apeljob['SubmitHost'] = arcjob['headnode']
        apeljob['MachineName'] = ''
        apeljob['Queue'] = arcjob['queue']
        apeljob['LocalJobId'] = arcjob['localid']
        apeljob['LocalUserId'] = arcjob['localuser']
        apeljob['GlobalUserName'] = arcjob['usersn']
        apeljob['FQAN'] = ''
        apeljob['VO'] = ''
        apeljob['VOGroup'] = ''
        apeljob['VORole'] = ''
        apeljob['WallDuration'] = arcjob['usedwalltime']
        apeljob['CpuDuration'] = arcjob['usedcputime']
        apeljob['Processors'] = arcjob['processors']
        apeljob['NodeCount'] = arcjob['nodecount']
        apeljob['StartTime'] = parse_timestamp(arcjob['submissiontime'])
        apeljob['EndTime'] = parse_timestamp(arcjob['endtime'])
        apeljob['InfrastructureDescription'] = ''.join(['APEL-ARC-', arcjob['lrms'].upper()])
        apeljob['InfrastructureType'] = 'grid'
        apeljob['MemoryReal'] = arcjob['usedmemory']
        apeljob['MemoryVirtual'] = ''
        apeljob['ServiceLevelType'] = arcjob['accounting_options']['benchmark_type']
        apeljob['ServiceLevel'] = arcjob['accounting_options']['benchmark_value']

        record = JobRecord()
        record.set_all(apeljob)
        return record, lines

    def parse_accounting_options(self, accounting_options):
        options = {}
        for pair in accounting_options.split(','):
            key, value = pair.split(':')
            options[key] = value
        return options
