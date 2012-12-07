from unittest import TestCase
from datetime import datetime 
from apel.parsers import PBSParser

class ParserPBSTest(TestCase):
    '''
    Test case for PBS parser
    '''
    
    def setUp(self):
        self.parser = PBSParser('testSite', 'testHost')
    
    def test_parse(self):
        line = ('10/02/2011 06:41:44;E;21048463.lcgbatch01.gridpp.rl.ac.uk;user=patls009 group=prodatls jobname=cre09_443343882 queue=grid4000M '
                'ctime=1317509574 qtime=1317509574 etime=1317509574 start=1317509945 owner=patls009@lcgce09.gridpp.rl.ac.uk '
                'exec_host=lcg1277.gridpp.rl.ac.uk/5 Resource_List.cput=96:00:00 Resource_List.neednodes=lcg1277.gridpp.rl.ac.uk '
                'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.pmem=4000mb Resource_List.walltime=96:00:00 session=20374 '
                'end=1317534104 Exit_status=0 resources_used.cput=18:15:24 resources_used.mem=2031040kb resources_used.vmem=3335528kb resources_used.walltime=19:23:4')
        
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
        
        self.assertEqual("21048463.lcgbatch01.gridpp.rl.ac.uk", cont["JobName"])
        self.assertEqual("patls009", cont['LocalUserID'])
        self.assertEqual("prodatls", cont['LocalUserGroup'])
        self.assertEqual(69784, cont['WallDuration'])
        self.assertEqual(65724, cont['CpuDuration'])
        self.assertEqual(datetime.utcfromtimestamp(1317509945), cont["StartTime"])
        self.assertEqual(datetime.utcfromtimestamp(1317534104), cont["StopTime"])
        self.assertEqual(2031040, cont["MemoryReal"])
        self.assertEqual(3335528, cont["MemoryVirtual"])
        
    def test_invalid_data(self):
        # missing separator between fields
        line = ('10/02/2011 06:41:44;E;21048463.lcgbatch01.gridpp.rl.ac.uk;user=patls009 group=prodatls jobname=cre09_443343882 queue=grid4000M '
                'ctime=1317509574 qtime=1317509574 etime=1317509574start=1317509945 owner=patls009@lcgce09.gridpp.rl.ac.uk '
                'exec_host=lcg1277.gridpp.rl.ac.uk/5 Resource_List.cput=96:00:00 Resource_List.neednodes=lcg1277.gridpp.rl.ac.uk '
                'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.pmem=4000mb Resource_List.walltime=96:00:00 session=20374 '
                'end=1317534104 Exit_status=0 resources_used.cput=18:15:24 resources_used.mem=2031040kb resources_used.vmem=3335528kb resources_used.walltime=19:23:4')

        self.assertRaises(KeyError, self.parser.parse, line)
    