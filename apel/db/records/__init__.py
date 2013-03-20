'''
   Copyright 2011 Will Rogers

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
Created on 1 Apr 2011

@author: Will Rogers

Interface for apel.db.records.
'''
import time
import datetime

from record import Record, InvalidRecordException
from blahd import BlahdRecord
from cloud import CloudRecord
from cloud_summary import CloudSummaryRecord
from event import EventRecord
from group_attribute import GroupAttributeRecord
from job import JobRecord
from processed import ProcessedRecord

from storage import StorageRecord
from summary import SummaryRecord
from sync import SyncRecord

