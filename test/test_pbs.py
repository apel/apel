import datetime
from unittest import TestCase
from apel.parsers import PBSParser
from apel.parsers.pbs import _parse_mpi

class ParserPBSTest(TestCase):
    '''
    Test case for PBS parser
    '''
    
    def setUp(self):
        self.parser = PBSParser('testSite', 'testHost', True)
        

    def test_parse(self):
        line1 = ('10/02/2011 06:41:44;E;21048463.lcgbatch01.gridpp.rl.ac.uk;user=patls009 group=prodatls jobname=cre09_443343882 queue=grid4000M '
                'ctime=1317509574 qtime=1317509574 etime=1317509574 start=1317509945 owner=patls009@lcgce09.gridpp.rl.ac.uk '
                'exec_host=lcg1277.gridpp.rl.ac.uk/5 Resource_List.cput=96:00:00 Resource_List.neednodes=lcg1277.gridpp.rl.ac.uk '
                'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.pmem=4000mb Resource_List.walltime=96:00:00 session=20374 '
                'end=1317534104 Exit_status=0 resources_used.cput=18:15:24 resources_used.mem=2031040kb resources_used.vmem=3335528kb resources_used.walltime=19:23:4')
        
        
        line1_values = {"JobName": "21048463.lcgbatch01.gridpp.rl.ac.uk", 
                        "LocalUserID":"patls009", 
                        "LocalUserGroup": "prodatls", 
                        "WallDuration":69784, 
                        "CpuDuration": 65724,
                        "StartTime": datetime.datetime.utcfromtimestamp(1317509945),
                        "StopTime": datetime.datetime.utcfromtimestamp(1317534104),
                        "MemoryReal":2031040,
                        "MemoryVirtual": 3335528,
                        "NodeCount": 1,
                        "Processors": 1
                        }

        line2 = ('10/01/2011 01:05:30;E;21010040.lcgbatch01.gridpp.rl.ac.uk;user=plhcb010 group=prodlhcb jobname=cre09_655648918 '
                'queue=gridWN ctime=1317427361 qtime=1317427361 etime=1317427361 start=1317427530 owner=plhcb010@lcgce09.gridpp.rl.ac.uk '
                'exec_host=lcg0766.gridpp.rl.ac.uk/7+lcg0766.gridpp.rl.ac.uk/6+lcg0766.gridpp.rl.ac.uk/5+lcg0766.gridpp.rl.ac.uk/4+'
                'lcg0766.gridpp.rl.ac.uk/3+lcg0766.gridpp.rl.ac.uk/2+lcg0766.gridpp.rl.ac.uk/1+lcg0766.gridpp.rl.ac.uk/0 '
                'Resource_List.cput=800:00:00 Resource_List.neednodes=1:ppn=8 Resource_List.nodect=1 Resource_List.nodes=1:ppn=8 '
                'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.walltime=96:00:00 session=7428 end=1317427530 '
                'Exit_status=0 resources_used.cput=00:00:00 resources_used.mem=0kb resources_used.vmem=0kb resources_used.walltime=00:00:00')
        
        line2_values = {"JobName": "21010040.lcgbatch01.gridpp.rl.ac.uk", 
                        "LocalUserID":"plhcb010", 
                        "LocalUserGroup": "prodlhcb", 
                        "WallDuration":0, 
                        "CpuDuration": 0,
                        "StartTime": datetime.datetime.utcfromtimestamp(1317427530),
                        "StopTime": datetime.datetime.utcfromtimestamp(1317427530),
                        "MemoryReal":0,
                        "MemoryVirtual": 0,
                        "NodeCount": 1,
                        "Processors": 8
                        }
        cases = {}
        cases[line1] = line1_values
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
            self.assertTrue(cont.has_key("MemoryVirtual"))
        
            for key in cases[line].keys():
                self.assertEqual(cont[key], cases[line][key], "%s != %s for key %s" % (cont[key], cases[line][key], key))
        
        
    def test_invalid_data(self):
        # missing separator between fields
        line = ('10/02/2011 06:41:44;E;21048463.lcgbatch01.gridpp.rl.ac.uk;user=patls009 group=prodatls jobname=cre09_443343882 queue=grid4000M '
                'ctime=1317509574 qtime=1317509574 etime=1317509574start=1317509945 owner=patls009@lcgce09.gridpp.rl.ac.uk '
                'exec_host=lcg1277.gridpp.rl.ac.uk/5 Resource_List.cput=96:00:00 Resource_List.neednodes=lcg1277.gridpp.rl.ac.uk '
                'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.pmem=4000mb Resource_List.walltime=96:00:00 session=20374 '
                'end=1317534104 Exit_status=0 resources_used.cput=18:15:24 resources_used.mem=2031040kb resources_used.vmem=3335528kb resources_used.walltime=19:23:4')

        self.assertRaises(KeyError, self.parser.parse, line)

    def test_parse_mpi(self):
        
        exec_host = 'lcg0766.gridpp.rl.ac.uk/7+lcg0766.gridpp.rl.ac.uk/6+lcg0766.gridpp.rl.ac.uk/5+lcg0766.gridpp.rl.ac.uk/4+lcg0766.gridpp.rl.ac.uk/3+lcg0766.gridpp.rl.ac.uk/2+lcg0766.gridpp.rl.ac.uk/1+lcg0766.gridpp.rl.ac.uk/0'
        nodecount, processors = _parse_mpi(exec_host)
        
        assert (nodecount, processors) == (1, 8)
        
        
        
        
