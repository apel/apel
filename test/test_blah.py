import datetime
from unittest import TestCase
from apel.parsers import BlahParser

class ParseBlahTest(TestCase):
    '''
    Test case for BLAH parser
    '''
    def setUp(self):
        self.parser = BlahParser('testSite', 'testHost')

    def test_parse(self):
        """
        Simple test for blahd parser
        """
        line = ('"timestamp=2012-05-20 23:59:47" ' 
                +'"userDN=/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg" '
                +'"userFQAN=/atlas/Role=production/Capability=NULL" '
                +'"ceID=cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL" ' 
                +'"jobID=CREAM410741480" "lrmsID=9575064.lrms1" "localUser=11999"')
        
        record = self.parser.parse(line)
        
        cont = record._record_content
        
        # Keys presence in record
        self.assertTrue(cont.has_key("TimeStamp"))
        self.assertTrue(cont.has_key("GlobalUserName"))
        self.assertTrue(cont.has_key("FQAN"))
        self.assertTrue(cont.has_key("CE"))
        self.assertTrue(cont.has_key("GlobalJobId"))
        self.assertTrue(cont.has_key("LrmsId"))

        # Data correctness in record
        # Note that the blahd timestamp is in UTC.
        self.assertEqual(datetime.datetime(2012, 5, 20, 23, 59, 47), cont['TimeStamp'])
        self.assertEqual("/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg", cont['GlobalUserName'])
        self.assertEqual("/atlas/Role=production/Capability=NULL", cont["FQAN"])
        self.assertEqual("cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL", cont["CE"])
        self.assertEqual("CREAM410741480", cont["GlobalJobId"])
        self.assertEqual("9575064.lrms1", cont["LrmsId"])
    
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