import unittest

from apel.db.loader.xml_parser import XMLParser, get_primary_ns


class XMLParserTest(unittest.TestCase):
    '''
    Test case for XMLParser
    '''
    
    data1 = '''<?xml version="1.0"?>
<ns:node xmlns:ns="http://fake.namespace.org">
   <ns:title>Some title</ns:title>
   <ns:values>
     <ns:value>data1</ns:value>
     <ns:value>data2</ns:value>
   </ns:values>
   
   <ns:attributes ns:attr="value">
      <ns:attribute ns:id="test1">attribute 1</ns:attribute>
      <ns:attribute ns:id="test2">attribute 2</ns:attribute>
   </ns:attributes>
</ns:node>'''
    
    def setUp(self):
        self.parser = XMLParser(self.data1)
        self.parser.NAMESPACE = 'http://fake.namespace.org'
    
    def test_get_text(self):
        values = self.parser.doc.getElementsByTagNameNS(self.parser.NAMESPACE, 'value')
        self.assertEqual('data1', self.parser.getText(values[0].childNodes))
        self.assertEqual('data2', self.parser.getText(values[1].childNodes))
    
    def test_get_tag_by_attr(self):
        attributes = self.parser.doc.getElementsByTagNameNS(self.parser.NAMESPACE, 'attribute')
        #print len(attributes)
        self.assertEqual(len(self.parser.getTagByAttr(attributes, 'id', 'test1')), 1)
        self.assertEqual(len(self.parser.getTagByAttr(attributes, 'id', 'test2')), 1)
    
    def test_get_attr(self):
        attributes_tag = self.parser.doc.getElementsByTagNameNS(self.parser.NAMESPACE, 'attributes')[0]
        self.assertEqual(self.parser.getAttr(attributes_tag, 'attr'), 'value')

    def test_get_primary_ns(self):
        test_xml = '<?xml version="1.0" ?><ur:UsageRecord xmlns:ur="booboob"/>'
        ns = get_primary_ns(test_xml)
        self.assertEqual("booboob", ns)

if __name__ == '__main__':
    unittest.main()
