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

import ldap
import logging
from decimal import Decimal, InvalidOperation

log = logging.getLogger(__name__)

# Constants used in BDII
GLUE_CE_CAPABILITY = 'GlueCECapability'
CPU_SCALING_REFERENCE = 'CPUScalingReferenceSI00'
GLUE_CE_UNIQUE_ID = 'GlueCEUniqueID'
GLUE_CLUSTER_UNIQUE_ID = 'GlueClusterUniqueID'
GLUE_CHUNK_KEY = 'GlueChunkKey'
GLUE_HOST_BENCHMARK = 'GlueHostBenchmarkSI00'
GLUE_FOREIGN_KEY = 'GlueForeignKey'

def parse_ce_capability(capability_string):
    '''
    We expect a value of the form:
    CPUScalingReferenceSI00=<value>
    where <value> is a decimal number.
    Return value as a decimal.
    '''
    decimal_value = None
    try:
        if capability_string.startswith(CPU_SCALING_REFERENCE):
            value = capability_string.split('=')[1]
            decimal_value = Decimal(value)
    except (InvalidOperation, IndexError):
        log.info('Failed to parse scaling reference: %s', capability_string)

    return decimal_value


def fetch_specint(site, host='lcg-bdii.egi.eu', port=2170):
    '''
    Imports benchmark data from LDAP. Current implementation
    is able to fetch data according to way described here:

    https://svn.esc.rl.ac.uk/trac/apel-dev/wiki/KonradNotes/TaskEight
    '''

    attrs = [GLUE_CE_CAPABILITY, GLUE_CE_UNIQUE_ID, GLUE_CLUSTER_UNIQUE_ID]
    values = []
    ldap_conn = ldap.initialize('ldap://%s:%d' % (host, port))

    top_level = 'mds-vo-name=%s,mds-vo-name=local,o=grid' % site

    try:
        # test query
        data = ldap_conn.search_s(top_level,
                           ldap.SCOPE_SUBTREE,
                           '(objectclass=GlueCE)',
                           attrs)
    except ldap.NO_SUCH_OBJECT:  # found no results by the first method
        top_level = 'mds-vo-name=%s,o=grid' % site
        data = ldap_conn.search_s(top_level,
                              ldap.SCOPE_SUBTREE,
                              '(objectclass=GlueCE)',
                              attrs)

    for entry in data:

        try:
            ce_name = entry[1][GLUE_CE_UNIQUE_ID][0]
            ce_capabilities=entry[1][GLUE_CE_CAPABILITY]
        except (KeyError, IndexError) as e:
            log.error('Error during fetching Spec values: %s', e)
            continue

        for capability in ce_capabilities:
            si2k = parse_ce_capability(capability)
            if si2k is not None:
                log.debug('Found value in first query: %s',
                          capability.split('=')[1])
                values.append((ce_name,
                           Decimal(capability.split('=')[1])))

    # not found? we have also second way to do this
    attrs = [GLUE_CHUNK_KEY, GLUE_HOST_BENCHMARK]
    data = ldap_conn.search_s(top_level,
                              ldap.SCOPE_SUBTREE,
                              '(objectclass=GlueSubcluster)',
                              attrs)

    for item in data:
        try:
            cluster_name = item[1][GLUE_CHUNK_KEY][0].split('=')[1]
            value = Decimal(item[1][GLUE_HOST_BENCHMARK][0])
        except (KeyError, IndexError) as e:
            log.error('Error during fetching Spec values: %s', e)
            continue

        subdata = ldap_conn.search_s(top_level,
                                     ldap.SCOPE_SUBTREE,
                                     '(GlueClusterName=%s)' % cluster_name,
                                     [GLUE_FOREIGN_KEY])
        for cluster in subdata:
            try:
                fks = cluster[1][GLUE_FOREIGN_KEY]
            except (KeyError, IndexError) as e:
                log.error('Error during fetching Spec values: %s', e)
                continue

            for fk in fks:
                if fk.startswith(GLUE_CE_UNIQUE_ID):
                    name = fk.split('=')[1]
                    # do not overwrite values from first query
                    if not any(x[0] == name for x in values):
                        values.append((name, value))

    return values
