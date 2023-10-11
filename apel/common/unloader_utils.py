#!/usr/bin/env python

# Copyright 2021 UK Research and Innovation
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

import logging

try:
    import ConfigParser
except ImportError:
    # Renamed in Python 3
    import configparser as ConfigParser

log = logging.getLogger(__name__)

RECORDS_PER_MESSAGE_MIN = 1
RECORDS_PER_MESSAGE_DEFAULT = 1000
RECORDS_PER_MESSAGE_MAX = 5000


def check_records_per_message(cp):
    """Check the range of the records_per_message entry in ConfigParser object.

    If it is out of range then set to closest bound within range. Else if
    it doesn't exist, set value to default.
    """
    try:
        records_per_message = int(cp.get('unloader', 'records_per_message'))

    except ConfigParser.NoSectionError:
        log.info(
            '[unloader] section not present, defaulting to %d.',
            RECORDS_PER_MESSAGE_DEFAULT,
        )
    except ConfigParser.NoOptionError:
        log.info(
            'records_per_message not specified, defaulting to %d.',
            RECORDS_PER_MESSAGE_DEFAULT,
        )
    except ValueError:
        log.error(
            'Invalid records_per_message value, must be a postive integer. '
            'Defaulting to %d.',
            RECORDS_PER_MESSAGE_DEFAULT,
        )
    else:  # When no errors are thrown
        if records_per_message < RECORDS_PER_MESSAGE_MIN:
            log.warning(
                'records_per_message too small, increasing from %d to %d',
                records_per_message,
                RECORDS_PER_MESSAGE_MIN,
            )
            return RECORDS_PER_MESSAGE_MIN
        elif records_per_message > RECORDS_PER_MESSAGE_MAX:
            log.warning(
                'records_per_message too large, decreasing from %d to %d',
                records_per_message,
                RECORDS_PER_MESSAGE_MAX,
            )
            return RECORDS_PER_MESSAGE_MAX
        else:
            return records_per_message

    # Return default when specific errors thrown
    return RECORDS_PER_MESSAGE_DEFAULT
