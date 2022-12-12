"""
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
"""
import time
import datetime

from apel.db.records.record import Record, InvalidRecordException
from apel.db.records.blahd import BlahdRecord
from apel.db.records.cloud import CloudRecord
from apel.db.records.cloud_summary import CloudSummaryRecord
from apel.db.records.event import EventRecord
from apel.db.records.group_attribute import GroupAttributeRecord
from apel.db.records.job import JobRecord
from apel.db.records.processed import ProcessedRecord

from apel.db.records.storage import StorageRecord
from apel.db.records.summary import SummaryRecord
from apel.db.records.normalised_summary import NormalisedSummaryRecord
from apel.db.records.sync import SyncRecord
