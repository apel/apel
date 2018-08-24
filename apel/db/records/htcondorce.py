'''
   Copyright 2012 Konrad Jopek

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

from apel.db.records.record import Record

class HTCondorCERecord(Record):
    """
    Class to represent a record from BLAHP systems
    """

    def __init__(self):
        '''
        Initializer for BlahdRecord
        '''

        Record.__init__(self)

        self._mandatory_fields = []

        self._db_fields = ["TimeStamp", "GlobalUserName", "FQAN",
                        "VO", "VOGroup", "VORole", "CE", "GlobalJobId", "LrmsId",
                        "Site", "ValidFrom", "ValidUntil", "Processed"]

        self._int_fields = ["Processed"]

        self._all_fields = self._db_fields

        self._datetime_fields = ["TimeStamp", "ValidFrom", "ValidUntil"]