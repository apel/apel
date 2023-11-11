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
    # used to protect user DN information
    DN_FIELD = 'GlobalUserName'
    WITHHELD_DN = 'withheld'

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
        # Fields which should contain associative arrays
        self._dict_fields = []
        # The dictionary into which all the information goes
        self._record_content = {}

    def set_all(self, fielddict):
        '''
        Copies all values for given dictionary to internal record's storage.
        Checks the field type and corrects it if it is necessary.
        '''
        for key in fielddict:
            self.set_field(key, fielddict[key])


    def set_field(self, key, value):
        '''
        Sets one field in the record's internal storage.
        '''
        if key in self._db_fields:
            self._record_content[key] = self.checked(key, value)
        else:
            if key not in self._ignored_fields:
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
            if value is None and name in self._mandatory_fields:
                raise InvalidRecordException('NULL in mandatory field: %s' % str(name))

            elif value is None:
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
                try:
                    return datetime.utcfromtimestamp(value)
                except ValueError as e:
                    # Given timestamp is probably out of range
                    raise InvalidRecordException(e)
            elif name in self._dict_fields:
                try:
                    return self._clean_up_dict(value)
                except ValueError as e:
                    raise InvalidRecordException(e)
            else:
                return value
        except ValueError:
            raise InvalidRecordException('Invalid content for field: %s (%s)' % (name, str(value)))

    def _clean_up_dict(self, dict_like):
        """Take a dict-like string and return a dict object with float values."""
        # Pull out the combined key:value elements from the string.
        elements = dict_like.strip('{}').split(',')
        # Separate the combined key:value elements into paired items.
        pairs = list((a.strip(), float(b.strip())) for a, b in (element.split(':') for element in elements))

        out_dict = {}
        for key, value in pairs:
            # Check for duplicates before inserting into the dictionary.
            if key in out_dict:
                raise ValueError('Duplicate keys found in %s' % dict_like)
            else:
                out_dict[key] = value
        return out_dict

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
            # log.info("Empty record: can't load.")
            return

        lines = text.strip().splitlines()

        # remove the bit before ': '
        self._record_content = {}
        for line in lines:
            try:
                key, value = [x.strip() for x in line.split(':', 1)]

                # This loop handles the v0.4 messages that have dictionaries in certain fields
                # It won't loop or do anything if _dict_fields is empty
                for field in self._dict_fields:
                    if field == key:

                        # Retrieve the benchmark type based on the preferntial order set in the extract method
                        benchmark_type, value = self._extract_benchmark_dict({key: value}, field)

                        if "ServiceLevelType" not in self._record_content:
                            # Set the benchmark type if it is its first occurence.
                            self._record_content["ServiceLevelType"] = benchmark_type
                        elif self._record_content["ServiceLevelType"] != benchmark_type:
                            # If a different benchmark type is retrieved from another field, raise a warning
                            raise InvalidRecordException("Mixture of benchmark types detected")
                        # Else the ServiceLevelType is already set to benchmark_type so nothing to do.

                        # Set the field to the value retrieved as that's what needs to do into the database
                        self._record_content[field] = self.checked(field, value)
                        break

                self.set_field(key, value)
            except IndexError:
                raise InvalidRecordException("Record contains a line  "
                                             "without a key-value pair: %s" % line)

        # Now, go through the logic to fill the contents[] dictionary.
        # The logic can get a bit involved here.

        self._check_fields()


    def get_msg(self, withhold_dns=False):
        '''
        Get the information about the record as a string in the format used
        for APEL's messages.  self._record_content holds the appropriate
        keys and values.

        If there is no relevant information for the key, its value should be
        None.  In this case, no line is included in the message unless
        it is a mandatory field.  If the field is mandatory, an
        exception is raised.
        '''
        # Check that the record is consistent.
        self._check_fields()
        # for certain records, we can replace GlobalUserName with 'withheld'
        # to protect private data
        dn = self.get_field(Record.DN_FIELD)
        if dn is not None and withhold_dns:
            self.set_field(Record.DN_FIELD, Record.WITHHELD_DN)

        msg = ""
        for key in self._msg_fields:
            # reset value each time.
            value = None
            try:
                if key in self._datetime_fields:
                    # convert datetime to epoch time for the message
                    # assume that the datetime is UTC
                    ttuple = self._record_content[key].timetuple()
                    value = str(int(calendar.timegm(ttuple)))
                else:
                    value = str(self._record_content[key]) # make sure we have a string
            except (KeyError, AttributeError):
                # It's only a problem if a mandatory field is missing;
                # otherwise just don't write the line to the message.
                if key in self._mandatory_fields:
                    raise InvalidRecordException('No mandatory key: %s found' % key)
            if value is None or value.isspace() or value == "":
                # Don't write a line to the message unless there's something
                # to say.
                continue

            if key in self._dict_fields:
                # Create dictionary fields for v0.4 message formats.
                benchmark_type = self._record_content['ServiceLevelType']
                msg += key+ ": {" + benchmark_type + ": " + value + "}\n"
            else:
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

            # Check if we have an integer by trying to cast to an int.
            try:
                value = int(value)
            except (ValueError, TypeError):
                if key in self._mandatory_fields:
                    raise InvalidRecordException("Mandatory int field " + key +
                                    " doesn't contain an integer.")
                elif check_for_null(value):
                    contents[key] = None
                elif value is not None:
                    raise InvalidRecordException("Int field " + key +
                                    " doesn't contain an integer.")

        # Change null values for floats to the null object -> NULL in the DB.
        for key in self._float_fields:
            try:
                value = contents[key]
            except KeyError:
                value = None

            # Check if we have an float by trying to cast to a float.
            try:
                value = float(value)
            except (ValueError, TypeError):
                if key in self._mandatory_fields:
                    raise InvalidRecordException("Mandatory decimal field " + key +
                                    " doesn't contain a float.")
                elif check_for_null(value):
                    contents[key] = None
                elif value is not None:
                    raise InvalidRecordException("Decimal field " + key +
                                    " doesn't contain a float.")

        # Change null values for Datetimes to the null object -> NULL in the DB.
        for key in self._datetime_fields:
            try:
                value = contents[key]
            except KeyError:
                value = None

            # Check if we have a datetime in this field.
            # We have to check this slightly differently than an int/float
            # as there doesn't seem to be a nice function to attempt to
            # cast an object to a datetime.
            if not isinstance(value, datetime):
                if key in self._mandatory_fields:
                    raise InvalidRecordException("Mandatory datetime field " + key +
                                   " doesn't contain a datetime.")
                elif check_for_null(value):
                    contents[key] = None
                elif value is not None:
                    raise InvalidRecordException("Datetime field " + key +
                                    " doesn't contain an datetime.")

    def _extract_benchmark_dict(self, fielddict, field):
        """Extract a preferrred benchmark type and value from a fielddict"""

        benchmark_priority = ("hepscore23", "hepspec", "si2k")

        if field in fielddict:
            try:
                cleaned_dict = self._clean_up_dict(fielddict[field])
                # Covert keys to lower case
                cleaned_dict = {k.lower(): v for k, v in cleaned_dict.items()}
            except ValueError as e:
                raise InvalidRecordException("Expecting dictionary-like value. %s" % e)

            for benchmark_type in benchmark_priority:
                if benchmark_type in cleaned_dict:
                    return benchmark_type, cleaned_dict[benchmark_type]
            else:
                raise InvalidRecordException("No valid benchmark type found")
