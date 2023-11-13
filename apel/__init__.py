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

   @author Konrad Jopek, Will Rogers
'''
__version__ = (1, 9, 2)

# Define the database schema version which this version of the code
# is expecting to use.
# The two numbers need not necessarily be in sync.
# A check is made immediately after the first DB
# connection by reading the SchemaVersionHistory table to compare what
# is found there (most recent update) with the string defined here.
EXPECTED_SCHEMA_VERSION = '1.9.1'
