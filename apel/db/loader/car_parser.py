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
   
   @author: Konrad Jopek, Will Rogers
'''

from apel.common import iso2seconds, parse_timestamp
from xml_parser import XMLParser, XMLParserException
from apel.db.records.job import JobRecord
import logging

log = logging.getLogger(__name__)


class CarParser(XMLParser):
    '''
    Parser for Compute Accounting Records
    
    For documentation please visit: 
    https://twiki.cern.ch/twiki/bin/view/EMI/ComputeAccountingRecord
    '''
    # main namespace for records
    NAMESPACE = "http://eu-emi.eu/namespaces/2012/11/computerecord"
    
    def get_records(self):
        '''
        Returns list of parsed records from CAR file.
        
        Please notice that this parser _requires_ valid
        structure of XML document, including namespace
        information and prefixes in XML tag (like urf:UsageRecord).
        '''
        cars = self.doc.getElementsByTagNameNS(self.NAMESPACE, 'UsageRecord')
        
        if len(cars) == 0:
            raise XMLParserException('File does not contain car records!') 
        
        return [ self.parse_car(car) for car in cars ] 
    
    def retrieve_cpu(self, nodes):
        '''
        Given all the nodes from the XML document, retrieve the appropriate value
        for CPU duration.
        
        If no attribute is present, use the value.  This is necessary to 
        be backward-compatible with the first version of the new APEL client,
        which omitted the attribute.
        If more than one attribute is present, 
        use <CpuDuration urf:usageType="all">value</CpuDuration>.
        '''
        cpu = ''
        cpu_nodes = self.getTagByAttr(nodes['CpuDuration'], 'usageType', 'all')
        if len(cpu_nodes) == 1:
            cpu = self.getText(cpu_nodes[0].childNodes)
        elif len(cpu_nodes) == 0:
            cpu = self.getText(nodes['CpuDuration'][0].childNodes)
        
        return cpu
    
    def retrieve_rmem(self, nodes):
        '''
        Given all the nodes from the XML document, retrieve the appropriate values
        for virtual and physical memory.
        
        Memory accounting is inexact in APEL.  Choose metric="average" if present, 
        otherwise metric="max" or finally metric omitted.
        
        This is further complicated by the different possible storageUnit values.
        '''
        rmem = None
        mem_nodes = self.getTagByAttr(nodes['Memory'], 'type', 'Physical')
        
        for node in mem_nodes:
            if (node.hasAttributeNS(self.NAMESPACE, 'metric') and 
                    node.getAttributeNS(self.NAMESPACE, 'metric') == 'average'):
                rmem = node.firstChild.data
            elif (node.hasAttributeNS(self.NAMESPACE, 'metric') and 
                    (node.getAttributeNS(self.NAMESPACE, 'metric') == 'max')):
                rmem = node.firstChild.data
            else:
                rmem = node.firstChild.data
        return rmem

    
    def parse_car(self, xml_record):
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
            'Queue'            : lambda nodes: self.getText(nodes['Queue'][0].childNodes),
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
            'CpuDuration'      : lambda nodes: iso2seconds(self.retrieve_cpu(nodes)),
            'Processors'       : lambda nodes: self.getText(nodes['Processors'][0].childNodes),
            'NodeCount'        : lambda nodes: self.getText(nodes['NodeCount'][0].childNodes),
            'MemoryReal'       : lambda nodes: None,
            'MemoryVirtual'    : lambda nodes: None,
            'StartTime'        : lambda nodes: parse_timestamp(self.getText(
                                        nodes['StartTime'][0].childNodes)),
            'EndTime'          : lambda nodes: parse_timestamp(self.getText(
                                        nodes['EndTime'][0].childNodes)),
            'InfrastructureDescription'      : lambda nodes: self.getAttr(nodes['Infrastructure'][0], 'description'),
            'InfrastructureType'             : lambda nodes: self.getAttr(nodes['Infrastructure'][0], 'type'),
            'ServiceLevelType' : lambda nodes: self.getAttr(
                                        nodes['ServiceLevel'][0], 'type'),
            'ServiceLevel'     : lambda nodes: self.getText(
                                        nodes['ServiceLevel'][0].childNodes),
            }

        tags = ['Site', 'SubmitHost', 'MachineName', 'Queue', 'LocalJobId', 'LocalUserId', 
                'GlobalUserName', 'GroupAttribute',
                'Group', 'WallDuration', 'CpuDuration', 'Memory', 
                'Processors', 'NodeCount', 'StartTime', 'EndTime', 'Infrastructure',
                'ServiceLevel']

        # Create a dictionary of all the tags we want to retrieve from the XML
        nodes = {}.fromkeys(tags)
        data = {}
        
        for node in nodes:
            # Create a list of nodes which match the tags we want.
            # Note that this only matches the one namespace we have defined.
            nodes[node] = xml_record.getElementsByTagNameNS(self.NAMESPACE, node)
        
        for field in functions:
            try:
                data[field] = functions[field](nodes)
            except (IndexError, KeyError, AttributeError), e:
                log.debug('Failed to parse field %s: %s', field, e)
            
        jr = JobRecord()
        jr.set_all(data)
        
        return jr
