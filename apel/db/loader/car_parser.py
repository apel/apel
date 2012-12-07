'''
   Copyright 2012 Konrad Jopek

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

from apel.common import iso2seconds, parse_timestamp
from xml_parser import XMLParser
from apel.db.records.job import JobRecord
import logging

log = logging.getLogger('loader')


class CarParser(XMLParser):
    '''
    Parser for Computing Accounting Records
    
    For documentation please visit: 
    https://twiki.cern.ch/twiki/bin/view/EMI/ComputeAccountingRecord
    '''
    
    # main namespace for records
    NAMESPACE = "http://eu-emi.eu/namespaces/2012/11/computerecord"
    
    # time format in CAR records
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    
    
    def get_records(self):
        '''
        Returns list of parsed records from CAR file.
        
        Please notice that this parser _requires_ valid
        structure of XML document, including namespace
        information and prefixes in XML tag (like urf:UsageRecord).
        '''
        records = []
        
        xml_storage_records = self.doc.getElementsByTagNameNS(self.NAMESPACE, 'UsageRecord')
        
        if len(xml_storage_records) == 0:
            raise Exception('File does not contain car records!') 
        
        for xml_storage_record in xml_storage_records:
            record = self.parseCarRecord(xml_storage_record)
            records.append(record)

        return records
    
    
    def parseCarRecord(self, xml_record):
        '''
        Main function for parsing CAR record.
        
        Interesting data can be fetched from 2 places:
         * as a content of node (here called text node)
         * as a attribute value (extracted by getAttr)
        '''
        functions = {
            'Site'             : lambda nodes: self.getText(nodes['Site'][0].childNodes),
            'SubmitHost'       : lambda nodes: self.getText(nodes['SubmitHost'][0].childNodes),
            'MachineName'      : lambda nodes: self.getText(nodes['MachineName'][0].childNodes),
            'LocalJobId'       : lambda nodes: self.getText(nodes['LocalJobId'][0].childNodes),
            'LocalUserId'      : lambda nodes: self.getText(nodes['LocalUserId'][0].childNodes),
            'GlobalUserName'   : lambda nodes: self.getText(nodes['GlobalUserName'][0].childNodes),
            'FQAN'             : lambda nodes: self.getText(
                                        self.getTagByAttr(nodes['GroupAttribute'], 
                                                          'type', 'FQAN')[0].childNodes),
            'VO'               : lambda nodes: self.getText(nodes['Group'][0].childNodes),
            'VOGroup'          : lambda nodes: self.getText(
                                        self.getTagByAttr(nodes['GroupAttribute'], 
                                                          'type', 'group')[0].childNodes),
            'VORole'           : lambda nodes: self.getText(
                                        self.getTagByAttr(nodes['GroupAttribute'],
                                                          'type', 'role')[0].childNodes),
            'WallDuration'     : lambda nodes: iso2seconds(self.getText(
                                        nodes['WallDuration'][0].childNodes)),
            'CpuDuration'      : lambda nodes: iso2seconds(self.getText(
                                        nodes['CpuDuration'][0].childNodes)),
            'Processors'       : lambda nodes: self.getText(nodes['Processors'][0].childNodes),
            'NodeCount'        : lambda nodes: self.getText(nodes['NodeCount'][0].childNodes),
            'MemoryReal'       : lambda nodes: self.getText(nodes['Processors'][0].childNodes),
            'MemoryVirtual'    : lambda nodes: self.getText(nodes['NodeCount'][0].childNodes),
            'StartTime'        : lambda nodes: parse_timestamp(self.getText(
                                        nodes['StartTime'][0].childNodes), self.TIME_FORMAT),
            'EndTime'          : lambda nodes: parse_timestamp(self.getText(
                                        nodes['EndTime'][0].childNodes), self.TIME_FORMAT),
            'InfrastructureDescription'      : lambda nodes: self.getAttr(nodes['Infrastructure'][0], 'description'),
            'InfrastructureType'             : lambda nodes: self.getAttr(nodes['Infrastructure'][0], 'type'),
            'ServiceLevelType' : lambda nodes: self.getAttr(
                                        nodes['ServiceLevel'][0], 'type'),
            'ServiceLevel'     : lambda nodes: self.getText(
                                        nodes['ServiceLevel'][0].childNodes),
            }

        tags = ['Site', 'SubmitHost', 'MachineName', 'LocalJobId', 'LocalUserId', 
                'GlobalUserName', 'GroupAttribute',
                'Group', 'WallDuration', 'CpuDuration', 
                'Processors', 'NodeCount', 'StartTime', 'EndTime', 'Infrastructure',
                'ServiceLevel']

        # here we copy keys from functions
        # we only want to change 'RecordId' to 'RecordIdentity',
        nodes = {}.fromkeys(tags)
        data = {}
        
        for node in nodes:
            # empty list = element have not been found in XML file
            nodes[node] = xml_record.getElementsByTagNameNS(self.NAMESPACE, node)
        
        for field in functions:
            try:
                data[field] = functions[field](nodes)
            except IndexError, e:
                log.debug('Failed to parse field %s: %s' % (field, e))
            except KeyError, e:
                log.debug('Failed to parse field %s: %s' % (field, e))
            
        jr = JobRecord()
        jr.set_all(data)
        
        return jr
