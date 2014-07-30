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

import iso8601
import datetime
import re


def valid_from(date, days=1):
    '''
    Method for BlahParser
    Returns calculated value for ValidFrom field.
    
    By default it returns Timestamp - 1 day
    '''
    delta = datetime.timedelta(days=days)
    return date-delta


def valid_until(date, days=28):
    '''
    Method for BlahParser
    Returns calculated value for ValidUntil field.
    
    By default it returns Timestamp + 28 days
    '''
    delta = datetime.timedelta(days=days)
    return date + delta


def parse_timestamp(datetime_string):
    '''
    Parse timestamp encoded as a string in various forms.  Return
    a TZ-unaware datetime object, which is in UTC.
    
    If timezone information is not present in the string, it
    assumes that the timezone is UTC.  
    '''
    dt = iso8601.parse_date(datetime_string)
    utcdt = dt.astimezone(iso8601.iso8601.UTC)
    # internal representation of datetimes is UTC without timezones
    return utcdt.replace(tzinfo=None)


def parse_time(timestring):
    '''
    Return seconds from times of the form d-h:m:s or h:m:s.
    '''
    if '-' in timestring:
        days, sub_days = timestring.split('-')
    else:
        days, sub_days = 0, timestring
    hours, minutes, seconds = sub_days.split(':')
    return 86400*int(days) + 3600*int(hours) + 60*int(minutes) + int(seconds)


def iso2seconds(isoduration):
    '''
    Parses time interval encoded as ISO string.  Returns time in seconds.
    '''
    pattern = "(^P)" # P required at the beginning
    pattern += "([0-9]+Y)?" # years
    pattern += "([0-9]+M)?" # months
    pattern += "([0-9]+W)?" # weeks
    pattern += "([0-9]+D)?" # days
    pattern += "(T)?"       # T indicates time values are starting
    pattern += "([0-9]+H)?" # hours
    pattern += "([0-9]+M)?" # minutes
    pattern += "([0-9]+\.?[0-9]*S)?"  # seconds
    pattern += "$"          # end of string

    cp = re.compile(pattern)
    match = cp.match(isoduration)
    values = match.groups()
    intvals = []
    for item in values:
        try:
            # remove letter from end then get an int
            if '.' in item:  # If item is a decimal
                intvals.append(int(round(float(item[:-1]))))
            else:
                intvals.append(int(item[:-1]))
        except (ValueError, TypeError):
            intvals.append(0)

    # ignore group 0 ("P") and group 5 ("T")
    seconds = intvals[1] * 31536000 + \
            intvals[2] * 2628000 + \
            intvals[3] * 604800 + \
            intvals[4] * 86400 + \
            intvals[6] * 3600 + \
            intvals[7] * 60 + \
            intvals[8] 
    
    return seconds