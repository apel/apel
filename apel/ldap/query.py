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
from apel.ldap import LOGGER_ID
import logging
from decimal import Decimal

log = logging.getLogger(LOGGER_ID)

def fetch_specint(site, host='lcg-bdii.cern.ch', port=2170):    
    '''
    Imports benchmark data from LDAP. Current implementation 
    is able to fetch data according to way described here:
    
    https://svn.esc.rl.ac.uk/trac/apel-dev/wiki/KonradNotes/TaskEight
    '''
    glue_ce_capability = 'GlueCECapability'
    glue_ce_unique_id = 'GlueCEUniqueID'
    glue_cluster_unique_id = 'GlueClusterUniqueID'
    cpu_scaling_reference = 'CPUScalingReferenceSI00'
    glue_chunk_key = 'GlueChunkKey'
    glue_host_benchmark = 'GlueHostBenchmarkSI00'
    glue_foreign_key = 'GlueForeignKey'
    
    attrs = [glue_ce_capability, glue_ce_unique_id, glue_cluster_unique_id]
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
            ce_name = entry[1][glue_ce_unique_id][0]
            ce_capabilities=entry[1][glue_ce_capability]
        except (KeyError, IndexError), e:
            log.error('Error during fetching Spec values: '+str(e))
            continue

        for capability in ce_capabilities:
            if capability.startswith(cpu_scaling_reference):
                log.info('Found value in first query: '+
                         str(capability.split('=')[1]))
                values.append((ce_name, 
                               Decimal(capability.split('=')[1])))
                        
    # not found? we have also second way to do this
    attrs = [glue_chunk_key, glue_host_benchmark]
    data = ldap_conn.search_s(top_level,
                              ldap.SCOPE_SUBTREE,
                              '(objectclass=GlueSubcluster)',
                              attrs)
    
    for item in data:
        try:
            cluster_name = item[1][glue_chunk_key][0].split('=')[1]
            value = Decimal(item[1][glue_host_benchmark][0])
        except (KeyError, IndexError), e:
            log.error('Error during fetching Spec values: '+str(e))
            continue
        
        subdata = ldap_conn.search_s(top_level,
                                     ldap.SCOPE_SUBTREE,
                                     '(GlueClusterName=%s)' % cluster_name,
                                     [glue_foreign_key])
        for cluster in subdata:
            try:
                fks = cluster[1][glue_foreign_key]
            except (KeyError, IndexError), e:
                log.error('Error during fetching Spec values: '+str(e))
                continue
            
            for fk in fks:
                if fk.startswith(glue_ce_unique_id):
                    name = fk.split('=')[1]
                    # do not overwrite values from first query
                    if len(filter(lambda x: x[0] == name, values)) == 0:
                        values.append((name, value))

    return values
