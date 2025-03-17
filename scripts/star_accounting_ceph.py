#!/usr/bin/env python3

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
#
#   @author Jounaid Ruhomaun (github.com/jounaidr)

import sys
import json
import subprocess
from datetime import datetime, timezone, timedelta
from dateutil import parser
from optparse import OptionParser
from xml.etree import ElementTree as xml


def main():
    # Command line options for script
    op = OptionParser(usage='python3 star_accounting_ceph.py [options]')
    op.add_option('-p', '--prefix', help='prefix of storage record filename'
                  ' [default: %default]', default='ceph-storage-record')
    op.add_option('-q', '--queue', help='location of message queue where storage record will be stored'
                  ' [default: %default]', default='/var/spool/apel/outgoing')
    op.add_option('-v', '--valid_duration', help='how long the storage record will be valid for (in seconds)'
                  ' [default: %default]', default='3600')
    op.add_option('-s', '--site', help='site where the storage record is being generated (required)')
    op.add_option('-o', '--storage_system', help='storage system where the storage record is being generated (required)')

    # Require --site and --storage_system arguments, if not supplied throw exception
    (options, unused_args) = op.parse_args()
    if not options.site:
        op.error('Site not specified')
    if not options.storage_system:
        op.error('Storage system not specified')

    # Filename for the storage record in the following format: prefix-YYYYMMDD-HHMMSS
    message_filename = options.prefix + datetime.now().strftime("-%Y%m%d-%H%M%S")
    # Location where the storage record will be placed, this should be set to the SSM outgoing directory
    message_queue_location = options.queue + '/' + message_filename
    # Duration for which the storage record is valid
    valid_duration = options.valid_duration
    # Site where storage record is being generated
    site = options.site
    # Site where storage record is being generated
    storage_system = options.storage_system

    try:
        # Retrieve bucket stats
        all_bucket_stats = get_all_bucket_stats()
    except Exception as e:
        print("error getting bucket stats: {}".format(e))
        sys.exit(1)

    root = xml.Element('sr:StorageUsageRecords')
    root.set('xmlns:sr', 'http://eu-emi.eu/namespaces/2011/02/storagerecord')

    for bucket in all_bucket_stats:
        try:
            # Calculate current timestamp for record at this point
            current_time = datetime.now(timezone.utc).isoformat()
            record_id = storage_system + "/sr/" + bucket["id"]
            storage_share = bucket["bucket"]
            file_count = bucket["usage"]["rgw.main"]["num_objects"]
            local_user = bucket["owner"]
            start_time = bucket["mtime"]
            # Calculate end_time based on bucket 'mtime' (start_time) + valid_duration constant
            end_time = str((parser.parse(start_time) + timedelta(0, int(valid_duration)))
                           .strftime('%Y-%m-%d %H:%M:%S.%fZ'))
            resource_capacity_used = bucket["usage"]["rgw.main"]["size_utilized"]
            logical_capacity_used = bucket["usage"]["rgw.main"]["size_actual"]
            resource_capacity_allocated = bucket["bucket_quota"]["max_size"]

        except KeyError as e:
            print("failed to get stats from bucket {} , bucket will not be included in accounting record"
                  .format(bucket["bucket"]))
            print("reason: {}".format(e))
            continue

        try:
            # Format bucket stats into StAR record
            sr_storage_usage_record = xml.SubElement(root, 'sr:StorageUsageRecord')

            sr_record_identity = xml.SubElement(sr_storage_usage_record, 'sr:RecordIdentity')
            sr_record_identity.set('sr:createTime', current_time)
            sr_record_identity.set('sr:recordId', record_id)

            sr_storage_system = xml.SubElement(sr_storage_usage_record, 'sr:StorageSystem')
            sr_storage_system.text = storage_system

            sr_site = xml.SubElement(sr_storage_usage_record, 'sr:Site')
            sr_site.text = site

            sr_storage_share = xml.SubElement(sr_storage_usage_record, 'sr:StorageShare')
            sr_storage_share.text = storage_share

            sr_file_count = xml.SubElement(sr_storage_usage_record, 'sr:FileCount')
            sr_file_count.text = str(file_count)

            sr_subject_identity = xml.SubElement(sr_storage_usage_record, 'sr:SubjectIdentity')
            sr_local_user = xml.SubElement(sr_subject_identity, 'sr:LocalUser')
            sr_local_user.text = local_user

            sr_start_time = xml.SubElement(sr_storage_usage_record, 'sr:StartTime')
            sr_start_time.text = start_time

            sr_end_time = xml.SubElement(sr_storage_usage_record, 'sr:EndTime')
            sr_end_time.text = end_time

            sr_resource_capacity_used = xml.SubElement(sr_storage_usage_record, 'sr:ResourceCapacityUsed')
            sr_resource_capacity_used.text = str(resource_capacity_used)

            sr_logical_capacity_used = xml.SubElement(sr_storage_usage_record, 'sr:LogicalCapacityUsed')
            sr_logical_capacity_used.text = str(logical_capacity_used)

            sr_resource_capacity_allocated = xml.SubElement(sr_storage_usage_record, 'sr:ResourceCapacityAllocated')
            sr_resource_capacity_allocated.text = str(resource_capacity_allocated)

        except xml.ParseError as e:
            print("bucket {} parsing failed, bucket will not be included in accounting record"
                  .format(bucket["bucket"]))
            print("reason: {}".format(e))
            continue

    # Store the formatted storage accounting record as XML at 'message_queue_location'
    xml_accounting_record = xml.ElementTree(root)
    with open(message_queue_location, 'wb') as f:
        xml_accounting_record.write(f, encoding='utf-8', xml_declaration=True)


def get_all_bucket_stats():
    # Run ceph command 'radosgw-admin bucket stats' to get all buckets info from command line
    p = subprocess.Popen(["radosgw-admin", "bucket", "stats"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    stats = json.loads(p.communicate()[0])
    return stats


if __name__ == "__main__":
    main()
