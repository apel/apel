"""
   Copyright (C) 2023 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Helper methods to perform JSON operations.
"""

JSON_MSG_BOILERPLATE = """{
    "Type": "%s",
    "Version": "%s",
    "UsageRecords": %s
}"""

def to_message(type, version, *usage_records):
    """ Generate JSON message format """
    return (
        JSON_MSG_BOILERPLATE % (type, version, list(usage_records))
    ).replace("'", '"')