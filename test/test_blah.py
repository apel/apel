import datetime
import unittest

from iso8601 import ParseError

from apel.parsers import BlahParser
from apel.db.records.record import InvalidRecordException


class ParserBlahTest(unittest.TestCase):
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
        # Should raise an exception - we have 'A' between date and time
        try:
            # iso8601 >= 0.1.9 version of test (now stricter in what it accepts)
            self.assertRaises(ParseError, self.parser.parse, line_invalidtimestamp)
        except:
            # iso8601 <= 0.1.8 version of test (should be deprecated)
            self.assertRaises(InvalidRecordException, self.parser.parse, line_invalidtimestamp)
        
    def test_invalid_record_line(self):
        line_invalid = ('"timestamp=2012-05-20 23:59:47" ' 
                +'"userDN=/O=GermanGrid/OU=UniWuppertal/CN=Torsten Harenberg" '
                +'"userFQAN=/atlas&Role=production/Capability=NULL" '
                +'"ceID=cream-2-fzk.gridka.de:8443/cream-pbs-atlasXL" ' 
                +'"jobID=CREAM410741480"&sd"lrmsID=9575064.lrms1" "localUser=11999"')
        self.assertRaises(ValueError, self.parser.parse, line_invalid)

    def test_multiple_fqans(self):
        """The parser should take the first FQAN to be the primary FQAN."""
        lines = (
            '"timestamp=2014-05-18 00:00:58" "userDN=/C=CA/O=Grid/OU=triumf.ca/'
            'CN=Asoka De Silva GC1" "userFQAN=/atlas/Role=pilot/Capability=NULL'
            '" "userFQAN=/atlas/Role=NULL/Capability=NULL" "userFQAN=/atlas/ca/'
            'Role=NULL/Capability=NULL" "userFQAN=/atlas/lcg1/Role=NULL/Capabil'
            'ity=NULL" "ceID=ce1.triumf.ca:8443/cream-pbs-atlas" "jobID=CREAM66'
            '3276716" "lrmsID=15876368.ce1.triumf.ca" "localUser=41200" "client'
            'ID=cream_663276716"',
            '"timestamp=2014-05-18 00:03:00" "userDN=/DC=ch/DC=cern/OU=Organic '
            'Units/OU=Users/CN=atlpilo2/CN=531497/CN=Robot: ATLAS Pilot2" "user'
            'FQAN=/atlas/Role=pilot/Capability=NULL" "userFQAN=/atlas/Role=NULL'
            '/Capability=NULL" "userFQAN=/atlas/lcg1/Role=NULL/Capability=NULL"'
            ' "userFQAN=/atlas/usatlas/Role=NULL/Capability=NULL" "ceID=ce1.tri'
            'umf.ca:8443/cream-pbs-atlas" "jobID=CREAM503347888" "lrmsID=158764'
            '80.ce1.triumf.ca" "localUser=41200" "clientID=cream_503347888"',
        )
        values = (
            (datetime.datetime(2014, 5, 18, 00, 00, 58),
             '/C=CA/O=Grid/OU=triumf.ca/CN=Asoka De Silva GC1',
             '/atlas/Role=pilot/Capability=NULL',  # primary FQAN is first one
             'atlas',
             '/atlas',
             'Role=pilot',
             'ce1.triumf.ca:8443/cream-pbs-atlas',
             'CREAM663276716',
             '15876368.ce1.triumf.ca',
             datetime.datetime(2014, 5, 17, 00, 00, 58),
             datetime.datetime(2014, 6, 15, 00, 00, 58),
             0
             ),
            (datetime.datetime(2014, 5, 18, 00, 03, 00),
             '/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=atlpilo2/CN=531497/CN'
                '=Robot: ATLAS Pilot2',
             '/atlas/Role=pilot/Capability=NULL',  # primary FQAN is first one
             'atlas',
             '/atlas',
             'Role=pilot',
             'ce1.triumf.ca:8443/cream-pbs-atlas',
             'CREAM503347888',
             '15876480.ce1.triumf.ca',
             datetime.datetime(2014, 5, 17, 00, 03, 00),
             datetime.datetime(2014, 6, 15, 00, 03, 00),
             0
             ),
        )

        fields = ('TimeStamp', 'GlobalUserName', 'FQAN', 'VO', 'VOGroup',
                  'VORole', 'CE', 'GlobalJobId', 'LrmsId', 'ValidFrom',
                  'ValidUntil', 'Processed')

        cases = {}
        for line, value in zip(lines, values):
            cases[line] = dict(zip(fields, value))

        for line in cases.keys():
            record = self.parser.parse(line)
            cont = record._record_content

            # Check that 'Site' has been set
            self.assertEqual(cont['Site'], 'testSite')

            for key in cases[line].keys():
                # Check all fields are present
                self.assertTrue(key in cont, "Key '%s' not in record." % key)
                # Check values are correct
                self.assertEqual(cont[key], cases[line][key],
                                 "'%s' != '%s' for key '%s'" %
                                 (cont[key], cases[line][key], key))

if __name__ == '__main__':
    unittest.main()
