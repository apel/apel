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
from builtins import object
import xml.dom.minidom

class XMLParserException(Exception):
    '''
    Exception for use by the XMLParser classes.
    '''
    pass

class XMLParser(object):
    '''
    Base class for CarParser and StarParser

    Implements general functionality for parsing XML files
    '''
    # for XMLParser NAMESPACE is empty
    NAMESPACE = ''

    def __init__(self, text):
        '''
        Initializes XMLParser (CarParser/StarParser) with content from XML file
        '''
        self.text = text
        self.doc = xml.dom.minidom.parseString(self.text)


    def getText(self, nodes):
        '''
        Returns content of text nodes.
        '''
        data = (''.join([ node.nodeType == node.TEXT_NODE and node.data or '' for node in nodes ]))
        return data


    def getAttr(self, node, name, namespace=None):
        '''
        Returns attribute value for given node and attribute name
        '''
        if namespace is None:
            return node.getAttributeNS(self.NAMESPACE, name)
        else:
            return node.getAttributeNS(namespace, name)


    def getTagByAttr(self, nodes, name, value, namespace=None):
        '''
        Looks for all tags having attribute 'name' with value 'value'
        '''
        if namespace is None:
            namespace = self.NAMESPACE

        retList = []
        for node in nodes:
            if (node.hasAttributeNS(namespace, name) and
                    self.getAttr(node, name, namespace) == value):
                retList.append(node)
        return retList


def get_primary_ns(msg_text):
    '''
    Return the XML namespace value for the top-level element in the
    XML document.
    Note that this has to load the XML document.
    '''
    d = xml.dom.minidom.parseString(msg_text)
    return d.firstChild.namespaceURI
