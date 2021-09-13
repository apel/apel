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

   @author: Konrad Jopek
'''

import logging
from apel.db import LOGGER_ID

logger = logging.getLogger(LOGGER_ID)

class ApelDbException(Exception):
    pass

class ApelDb(object):
    '''
    Interface for any database used by the record loader.  Implementations
    should implement the methods.
    '''
    def __new__(cls, backend, host, port, username, pwd, db):
        '''
        Constructs backend object.

        This class behaves as a factory. You cannot instantiate it.
        '''

        BACKENDS = {}

        try:
            from apel.db.backends.mysql import ApelMysqlDb
            BACKENDS['mysql'] = ApelMysqlDb
        except ImportError:
            logger.info('Cannot import mysql backend')

        try:
            from apel.db.backends.oracle import ApelOracleDb
            BACKENDS['oracle'] = ApelOracleDb
        except ImportError:
            logger.debug('Cannot import oracle backend')

        if backend not in BACKENDS.keys():
            raise ApelDbException('Unknown backend: %s' % (backend))

        backend = BACKENDS[backend]
        return backend(host, port, username, pwd, db)

    def test_connection(self):
        '''Connects to the database then closes the connection.'''
        pass

    def load_records(self, record_list, source):
        '''Given a list of records, and the DN of the sender,
        loads them into the database.'''
        pass

    def get_records(self, record_class, query=None):
        '''
        Returns records from database with given record type.
        Query object specifies which rows from database should be loaded.
        '''
        pass


class Query(object):
    '''
    Class for representing queries to DB.

    Simple usage:
    we want to select JobRecords with EventTime > 2011-01-01.
    We must construct query as follows:
    query = Query()
    query.EventTime_gt = parseTimestamp('2011-01-01', '%Y-%m-%d')

    apel_db.get_records(... query, ...)
    '''
    def get_where(self):
        '''
        Returns dynamically created SQL conditions for query.

        For example: field_name > 0 AND field_name < 100
        '''
        parts = self._get_where_helper()
        if not parts:
            return ""
        clauses = len(parts) > 1 and ' AND '.join(parts) or parts[0]
        return " WHERE " + clauses

    def _get_where_helper(self):
        '''
        Private function which uses reflection to get information
        about fields and relations.

        Possible relations are:
        <, >, <=, >=, =

        Exaple usage:
        (Python code -> Sql code)
        query.Field_lt = 0 -> Field < 0
        query.Field_gt = 13 -> Field > 13
        query.Field_le = 10 -> Field <= 10
        query.Field_ge = 12 -> Field >= 12
        query.Field=7 -> Field = 7
        '''
        elems = []

        RELATIONS = {'lt'   : ' < ',
                     'gt'   : ' > ',
                     'le'   : ' <= ',
                     'ge'   : ' >= ',
                     'in'   : ' in ',
                     'notin': ' not in '}

        for elem in self.__dict__:
            if elem.endswith("_in"):
                column = elem[:-3]
                wh = '('
                for item in self.__dict__[elem]:
                    wh += '"' + item + '",'

                wh = wh[:-1] + ')'

                elems.append(column + ' IN ' + wh)
            elif elem.endswith("_notin"):
                column = elem[:-6]
                wh = '('
                for item in self.__dict__[elem]:
                    wh += '"' + item + '",'

                wh = wh[:-1] + ')'

                elems.append(column + ' NOT IN ' + wh)
            elif '_' in elem:
                column, relation = elem.split('_')
                if relation not in RELATIONS:
                    raise ApelDbException('Unknown relation: %s' % relation)
                elems.append( column + RELATIONS[relation] + "'" + str(self.__dict__[elem]) + "'" )
            else:
                elems.append(elem + ' = ' + "'" + str(self.__dict__[elem]) + "'")

        return elems
