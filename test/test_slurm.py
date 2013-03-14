from datetime import datetime
from unittest import TestCase
from apel.parsers import SlurmParser

class ParserSlurmTest(TestCase):
    '''
    Test case for SLURM parser
    '''
    
    def setUp(self):
        self.parser = SlurmParser('testSite', 'testHost', True)
    
    def test_parse_line(self):
        
        line1 = ('667|sleep|root|root|2013-03-11T12:47:37|2013-03-11T12:47:40|00:00:03|12|debug|4|2|cloud-vm-[03-04]|560K|100904K ')
        
        line1_values = {"JobName": "667", 
                        "LocalUserID":"root", 
                        "LocalUserGroup": "root", 
                        "WallDuration":3,
                        "CpuDuration": 12,
                        "StartTime": datetime(2013, 3, 11, 12, 47, 37),
                        "StopTime": datetime(2013, 3, 11, 12, 47, 40),
                        "MemoryReal": 560,
                        "MemoryVirtual": 100904,
                        "NodeCount": 2,
                        "Processors": 4
                        }
        
        cases = {line1:line1_values}
        
        
        
        for line in cases.keys():
            record = self.parser.parse(line)
            cont = record._record_content
            
            self.assertTrue(cont.has_key("Site"))
            self.assertTrue(cont.has_key("JobName"))
            self.assertTrue(cont.has_key("LocalUserID"))
            self.assertTrue(cont.has_key("LocalUserGroup"))
            self.assertTrue(cont.has_key("WallDuration"))
            self.assertTrue(cont.has_key("CpuDuration"))
            self.assertTrue(cont.has_key("StartTime"))
            self.assertTrue(cont.has_key("StopTime"))
            self.assertTrue(cont.has_key("MemoryReal"))
            self.assertTrue(cont.has_key("MemoryReal"))
        
        
            for key in cases[line].keys():
                self.assertEqual(cont[key], cases[line][key], "%s != %s for key %s" % (cont[key], cases[line][key], key))
        