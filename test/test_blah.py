import datetime
from unittest import TestCase
from apel.parsers import BlahParser

class ParserBlahTest(TestCase):
    '''
    Test case for LSF parser
    '''
    
    def setUp(self):
        self.parser = BlahParser('testSite', 'testHost')
        

    def test_parse(self):
        line1 = ('"timestamp=2012-05-20 23:59:47" ' 
                +'"userDN=/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg" '
                +'"userFQAN=/atlas/Role=production/Capability=NULL" '
                +'"ceID=cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL" ' 
                +'"jobID=CREAM410741480" "lrmsID=9575064.lrms1" "localUser=11999"')
        
        line1_values = {"TimeStamp": datetime.datetime(2012, 5, 20, 23, 59, 47), 
                        "GlobalUserName":"/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg", 
                        "FQAN": "/atlas/Role=production/Capability=NULL", 
                        "CE": "cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL", 
                        "GlobalJobId": "CREAM410741480",
                        "LrmsId": "9575064.lrms1",
                        }
        
        cases = {}
        cases[line1] = line1_values
        
        for line in cases.keys():
            
            record = self.parser.parse(line)
            cont = record._record_content
        
            # Keys presence in record
            self.assertTrue(cont.has_key("TimeStamp"))
            self.assertTrue(cont.has_key("GlobalUserName"))
            self.assertTrue(cont.has_key("FQAN"))
            self.assertTrue(cont.has_key("CE"))
            self.assertTrue(cont.has_key("GlobalJobId"))
            self.assertTrue(cont.has_key("LrmsId"))
        
            for key in cases[line].keys():
                self.assertEqual(cont[key], cases[line][key], "%s != %s for key %s" % (cont[key], cases[line][key], key))
  
        
    def test_invalid_timestamp(self):
        '''
        Test if parser raises exception for invalid timestamp
        '''
        
        line_invalidtimestamp = ('"timestamp=2012-05-20A23:59:47" ' 
                +'"userDN=/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg" '
                +'"userFQAN=/atlas/Role=production/Capability=NULL" '
                +'"ceID=cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL" ' 
                +'"jobID=CREAM410741480" "lrmsID=9575064.lrms1" "localUser=11999"')
        # should raise InvalidValue error - we have 'A' between date and time
        self.assertRaises(ValueError, self.parser.parse, line_invalidtimestamp)
        
    def test_invalid_record_line(self):
        line_invalid = ('"timestamp=2012-05-20 23:59:47" ' 
                +'"userDN=/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg" '
                +'"userFQAN=/atlas&Role=production/Capability=NULL" '
                +'"ceID=cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL" ' 
                +'"jobID=CREAM410741480"&sd"lrmsID=9575064.lrms1" "localUser=11999"')
        self.assertRaises(ValueError, self.parser.parse, line_invalid)
 