# Copyright 2014 The Science and Technology Facilities Council
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from datetime import datetime
import time
from xml.dom.minidom import Document

from apel.db.records import Record, InvalidRecordException


class NormalisedSummaryRecord(Record):
    '''
    Class to represent one normalised summary record.

    A normalised summary record is the same as a summary record except
    that it additionally contains normalised values for CPU and wall
    duration and it does not contain any ServiceLevel information.
    It knows about the structure of the MySQL table and the message format.
    It stores its information in a dictionary self._record_content.  The keys
    are in the same format as in the messages, and are case-sensitive.
    '''

    def __init__(self):
        '''Populate fields required to load the message.'''

        Record.__init__(self)

        # Fields which are required by the message format.
        self._mandatory_fields = ["Site", "Month", "Year", "WallDuration",
                                  "CpuDuration", "NormalisedWallDuration",
                                  "NormalisedCpuDuration", "NumberOfJobs"]

        # This list allows us to specify the order of lines when we construct
        # records. We use the field "Infrastructure" rather than the previously
        # used "InfrastructureType"
        self._msg_fields = ["Site", "Month", "Year", "GlobalUserName", "VO",
                            "VOGroup", "VORole", "SubmitHost", "Infrastructure",
                            "NodeCount", "Processors", "EarliestEndTime",
                            "LatestEndTime", "WallDuration", "CpuDuration",
                            "NormalisedWallDuration", "NormalisedCpuDuration",
                            "NumberOfJobs"]

        # Fields which will have an integer stored in them
        self._int_fields = ["Month", "Year", "NodeCount", "Processors",
                            "WallDuration", "CpuDuration",
                            "NormalisedWallDuration", "NormalisedCpuDuration",
                            "NumberOfJobs"]

        self._datetime_fields = ["EarliestEndTime", "LatestEndTime"]

        self._ignored_fields = ["UpdateTime"]

        # This list specifies the information that goes in the database.
        self._db_fields = self._msg_fields
        # All allowed fields.
        self._all_fields = self._msg_fields

    def _check_fields(self):
        '''
        Add extra checks to the ones in the parent class.
        '''

        # Call the parent's checks first.
        Record._check_fields(self)

        # shorthand
        rc = self._record_content

        month_start = None
        month_end = None
        # For storing the month and year for the subsequent month.
        next_month_year = None
        next_month = None

        try:
            # A bit convoluted for finding the first second in the next month.
            if (int(rc['Month']) == 12):
                next_month_year = int(rc['Year']) + 1
                next_month = 1
            else:
                next_month_year = int(rc['Year'])
                next_month = int(rc['Month']) + 1

            month_start = datetime(int(rc['Year']), int(rc['Month']), 1)
            month_end = datetime(next_month_year, next_month, 1)

        except (KeyError, TypeError, ValueError):
            raise InvalidRecordException("Invalid values for month and/or year.")

        # Check that the EarliestEndTime and LatestEndTime fall within the right
        # month, and that EET < LET.
        try:
            earliest_end = rc['EarliestEndTime']
            latest_end = rc['LatestEndTime']
            if not (month_start <= earliest_end <= month_end):
                raise InvalidRecordException("EarliestEndTime is not within stated month.")
            if not (month_start <= latest_end <= month_end):
                raise InvalidRecordException("LatestEndTime is not within stated month.")

            if earliest_end > latest_end:
                raise InvalidRecordException("LatestEndTime is earlier than EarliestEndTime.")
        except TypeError:
            # These two fields are not compulsory.
            pass

        # Check that the month isn't in the future
        now = datetime.now()
        if month_start > now:
            raise InvalidRecordException("Month specified in record is in the future.")

        if not 1 <= self._record_content['Month'] <= 12:
            raise InvalidRecordException("Month value is out of range")

        if self._record_content['WallDuration'] < 0:
            raise InvalidRecordException("Negative WallDuration")
        if self._record_content['CpuDuration'] < 0:
            raise InvalidRecordException("Negative CpuDuration")
        if self._record_content['NormalisedWallDuration'] < 0:
            raise InvalidRecordException("Negative NormalisedWallDuration")
        if self._record_content['NormalisedCpuDuration'] < 0:
            raise InvalidRecordException("Negative NormalisedCpuDuration")

    def get_ur(self):
        '''
        Returns the NormalisedSummaryRecord in AUR format. See
        https://twiki.cern.ch/twiki/bin/view/EMI/ComputeAccounting

        Namespace information is written only once per record, by dbunloader.
        '''
        # Create the document directly
        doc = Document()
        ur = doc.createElement('aur:SummaryRecord')

        site = doc.createElement('aur:Site')
        site.appendChild(doc.createTextNode(self.get_field('Site')))
        ur.appendChild(site)

        month = doc.createElement('aur:Month')
        month.appendChild(doc.createTextNode(str(self.get_field('Month'))))
        ur.appendChild(month)

        year = doc.createElement('aur:Year')
        year.appendChild(doc.createTextNode(str(self.get_field('Year'))))
        ur.appendChild(year)

        user_id = doc.createElement('aur:UserIdentity')

        if self.get_field('urf:GlobalUserName') is not None:
            global_user_name = doc.createElement('urf:GlobalUserName')
            global_user_name.appendChild(doc.createTextNode(self.get_field('GlobalUserName')))
            global_user_name.setAttribute('urf:type', 'opensslCompat')
            user_id.appendChild(global_user_name)

        if self.get_field('urf:Group') is not None:
            group = doc.createElement('urf:Group')
            group.appendChild(doc.createTextNode(self.get_field('VO')))
            user_id.appendChild(group)

        if self.get_field('VOGroup') is not None:
            vogroup = doc.createElement('urf:GroupAttribute')
            vogroup.setAttribute('urf:type', 'vo-group')
            vogroup.appendChild(doc.createTextNode(self.get_field('VOGroup')))
            user_id.appendChild(vogroup)

        if self.get_field('VORole') is not None:
            vorole = doc.createElement('urf:GroupAttribute')
            vorole.setAttribute('urf:type', 'vo-role')
            vorole.appendChild(doc.createTextNode(self.get_field('VORole')))
            user_id.appendChild(vorole)

        ur.appendChild(user_id)

        subhost = doc.createElement('aur:SubmitHost')
        subhost.appendChild(doc.createTextNode(str(self.get_field('SubmitHost'))))
        ur.appendChild(subhost)

        infra = doc.createElement('aur:Infrastructure')
        infra.setAttribute('urf:type', self.get_field('Infrastructure'))
        ur.appendChild(infra)

        earliest = doc.createElement('aur:EarliestEndTime')
        earliest_text = time.strftime('%Y-%m-%dT%H:%M:%SZ', self.get_field('EarliestEndTime').timetuple())
        earliest.appendChild(doc.createTextNode(earliest_text))
        ur.appendChild(earliest)

        latest = doc.createElement('aur:LatestEndTime')
        latest_text = time.strftime('%Y-%m-%dT%H:%M:%SZ', self.get_field('LatestEndTime').timetuple())
        latest.appendChild(doc.createTextNode(latest_text))
        ur.appendChild(latest)

        wall = doc.createElement('aur:WallDuration')
        wall.appendChild(doc.createTextNode('PT'+str(self.get_field('WallDuration'))+'S'))
        ur.appendChild(wall)

        cpu = doc.createElement('aur:CpuDuration')
        cpu.appendChild(doc.createTextNode('PT'+str(self.get_field('CpuDuration'))+'S'))
        ur.appendChild(cpu)

        nwall = doc.createElement('aur:NormalisedWallDuration')
        nwall.appendChild(doc.createTextNode('PT'+str(self.get_field('NormalisedWallDuration'))+'S'))
        ur.appendChild(nwall)

        ncpu = doc.createElement('aur:NormalisedCpuDuration')
        ncpu.appendChild(doc.createTextNode('PT'+str(self.get_field('NormalisedCpuDuration'))+'S'))
        ur.appendChild(ncpu)

        cpu = doc.createElement('aur:NumberOfJobs')
        cpu.appendChild(doc.createTextNode(str(self.get_field('NumberOfJobs'))))
        ur.appendChild(cpu)

        if self.get_field('Processors') > 0:
            procs = doc.createElement('aur:Processors')
            procs.appendChild(doc.createTextNode(str(self.get_field('Processors'))))
            ur.appendChild(procs)

        if self.get_field('NodeCount') > 0:
            ncount = doc.createElement('aur:NodeCount')
            ncount.appendChild(doc.createTextNode(str(self.get_field('NodeCount'))))
            ur.appendChild(ncount)

        doc.appendChild(ur)
        # We don't want the XML declaration, because the whole XML
        # document will be assembled by another part of the program.
        return doc.documentElement.toxml()
