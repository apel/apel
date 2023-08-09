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

@author Will Rogers

Module containing the RecordFactory class.
'''

from future.builtins import object

from apel.db.records.job import JobRecord, JobRecord04
from apel.db.records.summary import SummaryRecord, SummaryRecord04
from apel.db.records.normalised_summary import NormalisedSummaryRecord, NormalisedSummaryRecord04
from apel.db.records.sync import SyncRecord
from apel.db.records.cloud import CloudRecord
from apel.db.records.cloud_summary import CloudSummaryRecord
from apel.db import (JOB_MSG_HEADER, SUMMARY_MSG_HEADER,
                     NORMALISED_SUMMARY_MSG_HEADER, SYNC_MSG_HEADER,
                     CLOUD_MSG_HEADER, CLOUD_SUMMARY_MSG_HEADER)

from apel.db.loader.car_parser import CarParser
from apel.db.loader.aur_parser import AurParser
from apel.db.loader.star_parser import StarParser
from apel.db.loader.xml_parser import get_primary_ns

import logging

# Set up logging
log = logging.getLogger(__name__)

class RecordFactoryException(Exception):
    '''Exception for use by the RecordFactory.'''
    pass


class RecordFactory(object):
    '''
    Class to create message objects for the appropriate message.  We only
    expect to make JobRecord and SummaryRecord objects, but this shouldn't
    restrict the capability to make more.
    '''
    # Message headers; remove version numbers from the end.
    JR_HEADER = JOB_MSG_HEADER.split(':')[0].strip()
    SR_HEADER = SUMMARY_MSG_HEADER
    NSR_HEADER = NORMALISED_SUMMARY_MSG_HEADER
    SYNC_HEADER = SYNC_MSG_HEADER.split(':')[0].strip()
    CLOUD_HEADER = CLOUD_MSG_HEADER.split(':')[0].strip()
    CLOUD_SUMMARY_HEADER = CLOUD_SUMMARY_MSG_HEADER.split(':')[0].strip()

    def create_records(self, msg_text):
        '''
        Given the text from a message, create a list of record objects and
        return that list.
        '''
        # remove any whitespace
        msg_text = msg_text.strip()
        try:
            # XML format
            if msg_text.startswith('<'):
                # Get the primary XML namespace
                primary_ns = get_primary_ns(msg_text)
                if primary_ns == CarParser.NAMESPACE:
                    created_records = self._create_cars(msg_text)
                    # Not available yet.
                elif primary_ns == AurParser.NAMESPACE:
                    # created_records = self._create_aurs(msg_text)
                    raise RecordFactoryException('Aggregated usage record not yet supported.')
                elif primary_ns == StarParser.NAMESPACE:
                    created_records = self._create_stars(msg_text)
                else:
                    raise RecordFactoryException('XML format not recognised.')
            # APEL format
            else:
                lines = msg_text.splitlines()

                header = lines.pop(0)
                # recreate message as string having removed header
                msg_text = '\n'.join(lines)

                # crop the string to before the first ':'
                index = header.index(':')
                msg_header_type = header[0:index].strip()
                # msg_header_version = header[index:].strip()

                record_mapping = {
                    RecordFactory.JR_HEADER: JobRecord,
                    RecordFactory.SR_HEADER: SummaryRecord,
                    RecordFactory.NSR_HEADER: NormalisedSummaryRecord,
                    RecordFactory.SYNC_HEADER: SyncRecord,
                    RecordFactory.CLOUD_HEADER: CloudRecord,
                    RecordFactory.CLOUD_SUMMARY_HEADER: CloudSummaryRecord,
                }

                try:
                    record_type = record_mapping[msg_header_type]
                except KeyError:
                    try:
                        # Use the full header to distinguish normalised and non-norm summaries.
                        record_type = record_mapping[header]
                    except KeyError:
                        raise RecordFactoryException('Message type %s not recognised.' % header)

                created_records = self._create_record_objects(msg_text, record_type)

            return created_records

        except ValueError as e:
            raise RecordFactoryException('Message header is incorrect: %s' % e)

    def _create_record_objects(self, msg_text, record_class):
        """Given the text from a record message, return a list of record objects."""
        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []

        for record in records:
            # unnecessary hack?
            if record != '' and not record.isspace():
                j = record_class()
                j.load_from_msg(record)
                msgs.append(j)

        return msgs

    def _create_cars(self, msg_text):
        '''
        Given a CAR message in XML format, create a list of JobRecord
        objects and return it.
        '''
        parser = CarParser(msg_text)
        records = parser.get_records()
        return records

    def _create_aurs(self, msg_text):
        '''
        Given a CAR message in XML format, create a list of JobRecord
        objects and return it.
        '''
        parser = AurParser(msg_text)
        records = parser.get_records()
        return records

    def _create_stars(self, msg_text):
        '''
        Given a StAR message in XML format, create a list of StorageRecord
        and GroupAttributes objects and return it.
        '''

        parser = StarParser(msg_text)
        records = parser.get_records()
        return records
