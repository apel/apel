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

Class representing a job from any batch system.
'''

from apel.db.records import Record

class EventRecord(Record):
    """
    Class to represent a batch system record.
    """

    def __init__(self):

        Record.__init__(self)

        self._mandatory_fields = []

        self._db_fields = ["Site", "JobName", "LocalUserID", "LocalUserGroup",
                           "WallDuration", "CpuDuration", "StartTime", "StopTime", "Infrastructure",
                           "MachineName", "Queue", "MemoryReal", "MemoryVirtual", "Processors", "NodeCount"]

        self._all_fields = self._db_fields

        self._int_fields = ["WallDuration", "CpuDuration", "MemoryReal",
                            "MemoryVirtual", "Processors", "NodeCount"]

        self._datetime_fields = ["StartTime", "StopTime"]
