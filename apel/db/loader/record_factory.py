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

from apel.common.message_schemas import IP_MSG_SCHEMA
from apel.db.records.job import JobRecord
from apel.db.records.summary import SummaryRecord
from apel.db.records.normalised_summary import NormalisedSummaryRecord
from apel.db.records.sync import SyncRecord
from apel.db.records.cloud import CloudRecord
from apel.db.records.cloud_summary import CloudSummaryRecord
from apel.db.records.ip_record import IPRecord
from apel.db import (JOB_MSG_HEADER, SUMMARY_MSG_HEADER,
                     NORMALISED_SUMMARY_MSG_HEADER, SYNC_MSG_HEADER,
                     CLOUD_MSG_HEADER, CLOUD_SUMMARY_MSG_HEADER,
                     IP_MSG_TYPE)

from apel.db.loader.car_parser import CarParser
from apel.db.loader.aur_parser import AurParser
from apel.db.loader.star_parser import StarParser
from apel.db.loader.xml_parser import get_primary_ns

import json
import jsonschema
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
#                    # Not available yet.
                elif primary_ns == AurParser.NAMESPACE:
                    # created_records = self._create_aurs(msg_text)
                    raise RecordFactoryException('Aggregated usage record not yet supported.')
                elif primary_ns == StarParser.NAMESPACE:
                    created_records = self._create_stars(msg_text)
                else:
                    raise RecordFactoryException('XML format not recognised.')
            # JSON format
            elif msg_text.startswith('{'):
                # Convert the message to a dictionary so it can be
                # interrogated.
                try:
                    json_msg = json.loads(msg_text)
                except ValueError as error:
                    raise RecordFactoryException('Malformed JSON: %s' % error)

                # Create record objects from the JSON.
                try:
                    if json_msg['Type'] == IP_MSG_TYPE:
                        created_records = self._create_ip_records(json_msg)

                    else:
                        raise RecordFactoryException(
                            'Unsupported JSON message type: %s' %
                            json_msg['Type']
                        )

                # Catch the case where the JSON message type is not defined.
                except KeyError as key_error:
                    raise RecordFactoryException(
                        'Type of JSON message not provided.'
                    )

            # APEL format
            else:
                lines = msg_text.splitlines()

                header = lines.pop(0)
                # recreate message as string having removed header
                msg_text = '\n'.join(lines)

                created_records = []

                # crop the string to before the first ':'
                index = header.index(':')
                if (header[0:index].strip() == RecordFactory.JR_HEADER):
                    created_records = self._create_jrs(msg_text)
                elif (header.strip() == RecordFactory.SR_HEADER):
                    created_records = self._create_srs(msg_text)
                elif (header.strip() == RecordFactory.NSR_HEADER):
                    created_records = self._create_nsrs(msg_text)
                elif (header[0:index].strip() == RecordFactory.SYNC_HEADER):
                    created_records = self._create_syncs(msg_text)
                elif (header[0:index].strip() == RecordFactory.CLOUD_HEADER):
                    created_records = self._create_clouds(msg_text)
                elif (header[0:index].strip() == RecordFactory.CLOUD_SUMMARY_HEADER):
                    created_records = self._create_cloud_summaries(msg_text)
                else:
                    raise RecordFactoryException('Message type %s not recognised.' % header)

            return created_records

        except ValueError, e:
            raise RecordFactoryException('Message header is incorrect: %s' % e)

    ######################################################################
    # Private methods below
    ######################################################################

    def _create_ip_records(self, json_msg):
        '''Given a dictionary, attempt to return a list of IPRecord objects.'''
        # Before attempting to create the records, verify the supplied json
        # against the message schema.
        try:
            jsonschema.validate(json_msg, IP_MSG_SCHEMA)
        # Catch the case where json_msg does not conform to the
        # expected JSON schema for the JSON message type.
        except jsonschema.ValidationError as validation_error:
            raise RecordFactoryException(
                'IP message invalid against schema: %s' % validation_error
            )

        created_records = []
        for record_dict in json_msg['UsageRecords']:
            ip_record = IPRecord()
            ip_record.set_all(record_dict)
            created_records.append(ip_record)

        return created_records

    def _create_jrs(self, msg_text):
        '''
        Given the text from a job record message, create a list of
        JobRecord objects and return it.
        '''

        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []

        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                j = JobRecord()
                j.load_from_msg(record)
                msgs.append(j)

        return msgs


    def _create_srs(self, msg_text):
        '''
        Given the text from a summary record message, create a list of
        JobRecord objects and return it.
        '''

        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                s = SummaryRecord()
                s.load_from_msg(record)
                msgs.append(s)

        return msgs


    def _create_nsrs(self, msg_text):
        """
        Given the text from a normalised summary record message, create a list
        of JobRecord objects and return it.
        """

        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if record != '' and not record.isspace():
                ns = NormalisedSummaryRecord()
                ns.load_from_msg(record)
                msgs.append(ns)

        return msgs

    def _create_syncs(self, msg_text):
        '''
        Given the text from a sync message, create a list of
        SyncRecord objects and return it.
        '''

        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                s = SyncRecord()
                s.load_from_msg(record)
                msgs.append(s)

        return msgs


    def _create_clouds(self, msg_text):
        '''
        Given the text from a cloud message, create a list of
        SyncRecord objects and return it.
        '''

        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                c = CloudRecord()
                c.load_from_msg(record)
                msgs.append(c)

        return msgs

    def _create_cloud_summaries(self, msg_text):
        '''
        Given the text from a cloud summary message, create a list of
        SyncRecord objects and return it.
        '''

        msg_text = msg_text.strip()

        records = msg_text.split('%%')
        msgs = []
        for record in records:
            # unnecessary hack?
            if (record != '') and not (record.isspace()):
                c = CloudSummaryRecord()
                c.load_from_msg(record)
                msgs.append(c)

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
