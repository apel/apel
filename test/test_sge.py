from datetime import datetime
from unittest import TestCase
from apel.parsers import SGEParser

class ParserSGETest(TestCase):
    '''
    Test case for SGE parser
    '''
    
    def setUp(self):
        self.parser = SGEParser('testSite', 'testHost')
    
    def test_parse_line(self):
        
        line1 = ('dteam:testce.test:dteam:dteam041:STDIN:43:sge:' 
               +'19:1200093286:1200093294:1200093295:0:0:1:0:0:0.000000:0:0:0:0:'
               +'46206:0:0:0.000000:0:0:0:0:337:257:NONE:defaultdepartment:NONE:1' 
               +':0:0.090000:0.000213:0.000000:-U dteam -q dteam:0.000000:NONE:30171136.000000')
        
        line1_values = {"JobName": "43", 
                        "LocalUserID":"dteam041", 
                        "LocalUserGroup": "dteam", 
                        "WallDuration":1,
                        "CpuDuration": 0,
                        "StartTime": datetime.utcfromtimestamp(1200093294),
                        "StopTime": datetime.utcfromtimestamp(1200093295),
                        "MemoryReal":223,
                        "MemoryVirtual": 30171136,
                        "NodeCount": 1,
                        "Processors": 1
                        }
        
        cases = {line1:line1_values}
        
        line2 = ('large:compute-4-19.local:csic:csfiylfl:s001.sh:6972834:sge:0:1318560244:1318560254:1318740255:'
        '100:138:180001:0.005999:0.012998:1448.000000:0:0:0:0:1060:0:0:0.000000:168:0:0:0:89:2:por_defecto:'
        'defaultdepartment:mpi:9:0:1026706.540000:60207.223310:0.001862:-u csfiylfl -q big_small*,large*,offline*,small* -l '
        'arch=x86_64,h_fsize=1G,h_rt=180300,h_stack=16M,h_vmem=1124M,num_proc=1,processor=opteron_6174,s_rt=180000,s_vmem=1G '
        '-pe mpi 9:0.000000:NONE:821923840.000000:0:0')
        
        line2_values = {"JobName": "6972834", 
                        "LocalUserID":"csfiylfl", 
                        "LocalUserGroup": "csic", 
                        "WallDuration": 180001, 
                        "CpuDuration": 1026706,
                        "StartTime": datetime.utcfromtimestamp(1318560254),
                        "StopTime": datetime.utcfromtimestamp(1318740255),
                        "MemoryReal":63131849389,
                        "MemoryVirtual": 821923840,
                        "NodeCount": 1,
                        "Processors": 9
                        }
        cases[line2] = line2_values
        
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
        