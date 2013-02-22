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
   
   @author: Will Rogers, Konrad Jopek
'''

from apel.common import iso2seconds, parse_timestamp
from xml_parser import XMLParser
from apel.db.records.summary import SummaryRecord
from apel.db.loader.car_parser import CarParser
import logging

log = logging.getLogger('loader')


class AurParser(XMLParser):
    '''
    Parser for Computing Accounting Records
    
    For documentation please visit: 
    https://twiki.cern.ch/twiki/bin/view/EMI/ComputeAccountingRecord
    '''
    
    # main namespace for records
    NAMESPACE = "http://eu-emi.eu/namespaces/2012/11/aggregatedcomputerecord"
    
    def get_records(self):
        '''
        Returns list of parsed records from CAR file.
        
        Please notice that this parser _requires_ valid
        structure of XML document, including namespace
        information and prefixes in XML tag (like urf:UsageRecord).
        '''
        records = []
        
        xml_storage_records = self.doc.getElementsByTagNameNS(self.NAMESPACE, 'SummaryRecord')
        
        if len(xml_storage_records) == 0:
            raise Exception('File does not contain AUR records!') 
        
        for xml_storage_record in xml_storage_records:
            record = self.parseAurRecord(xml_storage_record)
            records.append(record)

        return records
    
    
    def parseAurRecord(self, xml_record):
        '''
        Main function for parsing AUR record.
        
        Interesting data can be fetched from 2 places:
         * as a content of node (here called text node)
         * as a attribute value (extracted by getAttr)
        '''
        functions = {
            'Site'             : lambda nodes: self.getText(nodes['Site'][0].childNodes),
            'Month'            : lambda nodes: self.getText(nodes['Month'][0].childNodes),
            'Year'             : lambda nodes: self.getText(nodes['Year'][0].childNodes),
            'GlobalUserName'   : lambda nodes: self.getText(nodes['GlobalUserName'][0].childNodes),
            'VO'               : lambda nodes: self.getText(nodes['Group'][0].childNodes),
            'VOGroup'          : lambda nodes: self.getText(
                                        self.getTagByAttr(nodes['GroupAttribute'], 
                                                          'type', 'vo-group')[0].childNodes, CarParser.NAMESPACE),
            'VORole'           : lambda nodes: self.getText(
                                        self.getTagByAttr(nodes['GroupAttribute'],
                                                          'type', 'role')[0].childNodes),
            'MachineName'      : lambda nodes: self.getText(nodes['MachineName'][0].childNodes),
            'SubmitHost'       : lambda nodes: self.getText(nodes['SubmitHost'][0].childNodes),
            'InfrastructureType' : lambda nodes: self.getAttr(
                                            nodes['Infrastructure'][0], 'type',
                                            CarParser.NAMESPACE),
            'EarliestEndTime'  : lambda nodes: parse_timestamp(self.getText(
                                        nodes['EarliestEndTime'][0].childNodes)),
            'LatestEndTime'  : lambda nodes: parse_timestamp(self.getText(
                                        nodes['LatestEndTime'][0].childNodes)),
            'WallDuration'     : lambda nodes: iso2seconds(self.getText(
                                        nodes['WallDuration'][0].childNodes)),
            'CpuDuration'      : lambda nodes: iso2seconds(self.getText(
                                        nodes['CpuDuration'][0].childNodes)),
            'ServiceLevelType' : lambda nodes: self.getAttr(
                                        nodes['ServiceLevel'][0], 'type', CarParser.NAMESPACE),
            'ServiceLevel'     : lambda nodes: self.getText(
                                        nodes['ServiceLevel'][0].childNodes),
            'NumberOfJobs'     : lambda nodes: self.getText(nodes['NumberOfJobs'][0].childNodes),
            'NodeCount'        : lambda nodes: self.getText(nodes['NodeCount'][0].childNodes),
            'Processors'       : lambda nodes: self.getText(nodes['Processors'][0].childNodes),
            }

        tags = ['Site', 'Month', 'Year', 'GlobalUserName', 'Group', 
                'GroupAttribute', 'SubmitHost', 'Infrastructure',
                'EarliestEndTime', 'LatestEndTime', 'WallDuration', 'CpuDuration', 
                'ServiceLevel', 'NumberOfJobs', 'NodeCount', 'Processors']

        nodes = {}.fromkeys(tags)
        data = {}
        
        for node in nodes:

            nodes[node] = xml_record.getElementsByTagNameNS(AurParser.NAMESPACE, node)
            # Some of the nodes are in the CAR namespace.
            nodes[node].extend(xml_record.getElementsByTagNameNS(CarParser.NAMESPACE, node))
        
        for field in functions:
            try:
                data[field] = functions[field](nodes)
            except IndexError, e:
                log.debug('Failed to parse field %s: %s' % (field, e))
            except KeyError, e:
                log.debug('Failed to parse field %s: %s' % (field, e))
        
        sr = SummaryRecord()
        sr.set_all(data)
        
        return sr
