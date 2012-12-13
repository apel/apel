'''
   Copyright (C) 2011, 2012 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
    @author: Will Rogers

Module containing the Record class.
'''

from apel.db import LOGGER_ID

from datetime import datetime
import time
import calendar
import logging

log = logging.getLogger(LOGGER_ID)


class InvalidRecordException(Exception):
    pass

def get_unix_time(py_date):
    '''Converts a python datetime object into Unix time.'''
    return time.mktime(py_date.timetuple()) 

def check_for_null(value):
    '''Check if a string is one of the different message values 
    which we accept as null.  This returns True if value is None.'''
    nulls = ['none', 'null', '']
    return str(value).lower() in nulls

class Record(object):
    '''
    Represents one APEL database row or record.
    
    The class is designed so that each record type should inherit from this
    one.  There is some logic which is a little tricky used to convert
    the contents of a message into a sensible python format.
    '''
    
    def __init__(self):
        '''
        Just defines the required lists which give content and order
        of a particular record.  These fields will be populated by 
        subclasses.
        '''
        # Fields which are required by the message format.
        self._mandatory_fields = []
        # All the keys which may be used in messages in the correct order.
        self._msg_fields = []
        # The information that goes in the database.
        self._db_fields = []
        # Fields which are permitted in a message, but are currently ignored.
        self._ignored_fields = [] 
        # All possible information, including some which may not go in
        # a message and fields ignored in received messages
        self._all_fields = []
        # Fields which should contain integers
        self._int_fields = []
        # Fields which should contain floating point numbers
        self._float_fields = []
        # Fields which should contain datetime (will be stored as a integers)
        self._datetime_fields = []
        # The dictionary into which all the information goes
        self._record_content = {}
    
    def set_all(self, fielddict):
        '''
        Copies all values for given dictionary to internal record's storage.
        Checks the field type and corrects it if it is necessary.
        '''
        for key in fielddict:
            if key in self._db_fields:
                self._record_content[key] = self.checked(key, fielddict[key])
            else:
                if not key in self._ignored_fields:
                    raise InvalidRecordException('Unknown field: %s' % key)
                
    def set_field(self, key, value):
        '''
        Sets one field in the record's internal storage.
        '''
        if key in self._db_fields:
            self._record_content[key] = self.checked(key, value)
        else:
            if not key in self._ignored_fields:
                raise InvalidRecordException('Unknown field: %s' % key)


    def get_field(self, name):
        '''
        Returns the content of the 'name' field.

        It can raise an error in case the record does not contain
        the mandatory field.

        @params: name Name of the field
        @return: Value of the field
        '''

        try:
            value = self._record_content[name]
            return value
        except KeyError:
            if name in self._mandatory_fields:
                raise InvalidRecordException('Missing mandatory field: %s' % name)
            else:
                return None


    def checked(self, name, value):
        '''
        Returns value converted to correct type if this is possible.
        Otherwise it raises an error.
        '''
        try:
            # Convert any null equivalents to a None object
            if check_for_null(value):
                value = None
            # firstly we must ensure that we do not put None
            # in mandatory field
            if value == None and name in self._mandatory_fields:
                raise InvalidRecordException('NULL in mandatory field: %s' % str(name))
            
            elif value == None:
                return value
            
            if name in self._int_fields: # integer values
                try:
                    return int(value)
                except ValueError:
                    raise InvalidRecordException('Invalid int value %s in field %s' % (value, name))
                
            elif name in self._float_fields: # float values
                try:
                    return float(value)
                except ValueError:
                    raise InvalidRecordException('Invalid float value %s in field %s' % (value, name))
                
            elif name in self._datetime_fields: 
                
                # if it is already a datetime, return it
                if type(value) == datetime:
                    return value
                # We accept ints or floats as seconds since the epoch
                try:
                    value = int(value)
                    return datetime.utcfromtimestamp(value)
                except ValueError:
                    # Not a datetime or an int, so it has to be a string representation.
                    # We get ISO format dates when parsing CAR or StAR.
                    isofmt = '%Y-%m-%dT%H:%M:%S%Z' # %Z denotes timezone
                    # A trailing Z in the ISO format denotes UTC.  We make this explicit for parsing.
                    dtval = value.replace('Z', 'UTC') 
                    try:
                        dt = datetime.utcfromtimestamp(time.mktime(time.strptime(dtval, isofmt)))
                        return dt
                    except ValueError: # Failed to parse timestamp
                        raise InvalidRecordException('Unknown datetime format!: %s' % value)
            else:
                return value
        except ValueError:
            raise InvalidRecordException('Invalid content for field: %s (%s)' % (name, str(value)))

    def load_from_tuple(self, tup):
        '''
        Given a tuple from a mysql database, load fields.
        '''
        assert len(tup) == len(self._db_fields), 'Different length of tuple and fields list'
        self.set_all(dict(zip(self._db_fields, tup)))

    def load_from_msg(self, text):
        '''
        Given text extracted from a message, load fields.  
        This uses the lists defined as part of any subclass to know 
        how to deal with any part of a message.
        '''
        
        if (text == "") or text.isspace():
#           log.info("Empty record: can't load.")
            return
            
        text = text.strip()
        lines = text.split('\n')
                
        # remove the bit before ': '
        self._record_content = {}
        for line in lines:
            try:
                value = line.split(':', 1)
                key = value[0].strip()
                self.set_all({key:value[1].strip()})
#                self._record_content[key] = value[1].strip()
            except IndexError:
                raise InvalidRecordException("Record contains a line  " +\
                                             "without a key-value pair: %s" % line)
        # Now, go through the logic to fill the contents[] dictionary.
        # The logic can get a bit involved here.
        
        self._check_fields()
        
    
    def get_msg(self):
        '''
        Get the information about the record as a string in the format used
        for APEL's messages.  self._record_content holds the appropriate
        keys and values.
        '''
        # firstly, we must ensure, that record is completed 
        # and no field is missing
        # _check_fields method may also check the internal logic inside the
        # record
        self._check_fields() 
        msg = ""
        for key in self._msg_fields:
            try:
                if key in self._datetime_fields:
                    # convert datetime to epoch time for the message
                    # assume that the datetime is UTC
                    ttuple = self._record_content[key].timetuple()
                    value = str(int(calendar.timegm(ttuple)))
                else:    
                    value = str(self._record_content[key]) # make sure we have a string
            except (KeyError, AttributeError):
                if key in self._mandatory_fields:
                    raise InvalidRecordException('No mandatory key: %s found' % key)
            if value == None or value.isspace() or value == "":
                # Don't write a line to the message unless there's something
                # to say.
                continue
                
            # otherwise, add the line
            msg += key + ": " + value + "\n"
        
        return msg
    
    
    def get_db_tuple(self, source=None):
        '''
        Returns record content as a tuple. Appends the source of the record 
        (i.e. the sender's DN) if this is supplied.  Includes exactly the 
        fields used in the DB by using the self._db_fields list.
        '''
        # firstly, we must ensure, that record is completed 
        # and no field is missing
        # _check_fields method may also check the internal logic inside the
        # record
        self._check_fields() 
        # Order is crucial here, so we use the list of DB fields to 
        # get the right values, then append the user's DN.
        l = []
        for key in self._db_fields:
            try:
                l.append(self._record_content[key])
            except KeyError:
                if key in self._mandatory_fields:
                    raise InvalidRecordException('Mandatory field: %s was not found' % key)
                else:
                    l.append('None')
                    
        if source is not None:
            l.append(source)
            
        # create a tuple from all the relevant info
        return tuple(l)
    
    ##########################################################################
    # Private methods below
    ##########################################################################
    
    def _check_fields(self):
        
        # shorthand
        contents = self._record_content
        
        # Check that all the required information is present.
        for key in self._mandatory_fields:
            if key not in contents:
                raise InvalidRecordException("Mandatory field " + key + " not specified.")
            value = contents[key]
            if check_for_null(value):
                raise InvalidRecordException("Mandatory field " + key + " not specified.")

        # Check that no extra fields are specified.
        # Is this inefficient?
        for key in contents.keys():
            if key not in self._all_fields:
                raise InvalidRecordException("Unexpected field " + key + " in message.")

        # Fill the dictionary even if we don't have the relevant data.
        # The string values are getting 'None' (not None!) instead of going into the 
        # DB as NULL.
        current_keys = contents.keys()
        for key in self._msg_fields:
            if key not in current_keys: # key not already in the dictionary
                contents[key] = "None"
            if check_for_null(contents[key]):
                contents[key] = "None"
        
        
        # Change the null values for integers to None (not 'None'!) -> NULL in the DB.
        for key in self._int_fields:
            try:
                value = contents[key]
            except KeyError:
                value = None
                    
            # check if we have an integer in this field
            try:
                value = int(value)
            except (ValueError, TypeError), e:
                if key in self._mandatory_fields:
                    raise InvalidRecordException("Mandatory int field " + key + 
                                    " doesn't contain an integer.")
                elif check_for_null(value):
                    contents[key] = None 
                elif value != None:
                    raise InvalidRecordException("Int field " + key + 
                                    " doesn't contain an integer.")
