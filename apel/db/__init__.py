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
'''

LOGGER_ID = "apeldb"
JOB_MSG_HEADER = "APEL-individual-job-message: v0.3"
SUMMARY_MSG_HEADER = "APEL-summary-job-message: v0.2"
NORMALISED_SUMMARY_MSG_HEADER = "APEL-summary-job-message: v0.3"
SYNC_MSG_HEADER = "APEL-sync-message: v0.1"
CLOUD_MSG_HEADER = 'APEL-cloud-message: v0.4'
CLOUD_SUMMARY_MSG_HEADER = 'APEL-cloud-summary-message: v0.4'
ACCELERATOR_MSG_TYPE = "APEL-accelerator-message"
ACCELERATOR_SUMMARY_MSG_TYPE = "APEL-accelerator-summary-message"

from apel.db.apeldb import ApelDb, Query, ApelDbException
