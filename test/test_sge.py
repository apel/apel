from datetime import datetime
import unittest

import mock

import apel.parsers
import apel.parsers.sge

class ParserSGETest(unittest.TestCase):
    '''
    Test case for SGE parser
    '''

    def setUp(self):
        self.parser = apel.parsers.SGEParser('testSite', 'testHost', True)

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
                        "NodeCount": 0,
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
                        "CpuDuration": 1026707,
                        "StartTime": datetime.utcfromtimestamp(1318560254),
                        "StopTime": datetime.utcfromtimestamp(1318740255),
                        "MemoryReal":63131849389,
                        "MemoryVirtual": 821923840,
                        "NodeCount": 0,
                        "Processors": 9
                        }
        cases[line2] = line2_values

        line3 = 'lcg_analysis:cn446.htc.esc.qmul:pilatl:pilatl10:cream_297073580:1630912:sge:5:1358189999:1358190002:1358210574:0:1:20365.78:1211.1274098:61.49143143:385648.000000:0:0:0:0:2236317:1450:0:0.000000:0:0:0:0:245899:291449:pilatl.p:defaultdepartment:NONE:1:0:1272.61884123:430.743820:37.845289:-q lcg_analysis:0.000000:NONE:1546682368.000000:0:0'

        line3_values = {"JobName": "1630912",
                        "LocalUserID":"pilatl10",
                        "LocalUserGroup": "pilatl",
                        "WallDuration": 20366,
                        "CpuDuration": 1273,
                        "StartTime": datetime.utcfromtimestamp(1358190002),
                        "StopTime": datetime.utcfromtimestamp(1358210574),
                        "MemoryReal":451667631,
                        "MemoryVirtual": 1546682368,
                        "NodeCount": 0,
                        "Processors": 1
                        }

        cases[line3] = line3_values

        line4 = ("grid.q:node101.cm.cluster:prdatl:prdatl26:cream_324080374:329"
                 "4013:sge:0:1404167579:1404169049:1404169408:0:0:359:32.189106"
                 ":18.607171:99104.000000:0:0:0:0:1957472:1546:0:483672.000000:"
                 "20488:0:0:0:151429:47022:NONE:defaultdepartment:NONE:1:0:50.7"
                 "96277:4.497218:0.339940:-u prdatl26 -q grid.q -binding no_job"
                 "_binding 0 0 0 0 no_explicit_binding:0.000000:NONE:5944487936"
                 ".000000:0:0:NONE")

        line4_values = {'JobName': "3294013",
                        'LocalUserID': "prdatl26",
                        'LocalUserGroup': "prdatl",
                        'WallDuration': 359,
                        'CpuDuration': 51,
                        'StartTime': datetime.utcfromtimestamp(1404169049),
                        'StopTime': datetime.utcfromtimestamp(1404169408),
                        'MemoryReal': int(4.497218*1024*1024),
                        'MemoryVirtual': 5944487936,
                        'NodeCount': 0,
                        'Processors': 1
                        }

        cases[line4] = line4_values

        for line in list(cases.keys()):
            record = self.parser.parse(line)
            cont = record._record_content

            self.assertIn("Site", cont)
            self.assertIn("JobName", cont)
            self.assertIn("LocalUserID", cont)
            self.assertIn("LocalUserGroup", cont)
            self.assertIn("WallDuration", cont)
            self.assertIn("CpuDuration", cont)
            self.assertIn("StartTime", cont)
            self.assertIn("StopTime", cont)
            self.assertIn("MemoryReal", cont)


            for key in list(cases[line].keys()):
                self.assertEqual(cont[key], cases[line][key], "%s != %s for key %s" % (cont[key], cases[line][key], key))

    def test_univa_timestamps(self):
        """
        Univa Grid Engine timestamps changed from seconds to milliseconds in
        version 8.2.0. This tests the new format accounting log.
        """
        self.parser.set_ms_timestamps(True)

        line = ("grid.q:node101.cm.cluster:atlas:atlas235:cream_814542935:38725"
                "61:sge:0:1412932860657:1412932865141:1412933085629:0:0:220.488"
                ":7.301:5.469:123796:0:0:0:0:601325:794:0:237152:728:0:0:0:5439"
                "6:1217:NONE:defaultdepartment:NONE:1:0:12.770:0.803193:0.08415"
                "9:-u atlas235 -q grid.q -binding no_job_binding 0 0 0 0 no_exp"
                "licit_binding:0.000000:NONE:1291231232:0:0:NONE:NONE:124411904"
                ":115065856:grid-cream-02.hpc.susx.ac.uk:NONE:qsub /tmp/cream_8"
                "14542935")

        values = {'JobName': "3872561",
                  'LocalUserID': "atlas235",
                  'LocalUserGroup': "atlas",
                  'WallDuration': 220,
                  'CpuDuration': 13,
                  'StartTime': datetime.utcfromtimestamp(1412932865),
                  'StopTime': datetime.utcfromtimestamp(1412933086),
                  'MemoryReal': int(0.803193*1024*1024),
                  'MemoryVirtual': 1291231232,
                  'NodeCount': 0,
                  'Processors': 1
                  }

        record = self.parser.parse(line)
        cont = record._record_content

        for key in values:
            self.assertEqual(cont[key], values[key],
                             "%s != %s for key %s" % (cont[key], values[key],
                                                      key))

    def test_set_ms_timestamp(self):
        """Check that this method works as exepected."""
        self.assertFalse(self.parser._ms_timestamps, "Non-default ms setting")

        self.parser.set_ms_timestamps(True)
        self.assertTrue(self.parser._ms_timestamps, "_ms_timestamps not set")

        self.parser.set_ms_timestamps(False)
        self.assertFalse(self.parser._ms_timestamps, "_ms_timestamps not unset")

    def test_parse_line_with_multiplier(self):
        '''
        Multiplier (cpu, wall) functionality testing.
        '''
        cputmult = 2.0
        wallmult = 2.0
        line = ('large:compute-4-19.local:csic:csfiylfl:s001.sh:6972834:sge:0:1318560244:1318560254:1318740255:'
        '100:138:180001:0.005999:0.012998:1448.000000:0:0:0:0:1060:0:0:0.000000:168:0:0:0:89:2:por_defecto:'
        'defaultdepartment:mpi:9:0:1026706.540000:60207.223310:0.001862:-u csfiylfl -q big_small*,large*,offline*,small* -l '
        'arch=x86_64,h_fsize=1G,h_rt=180300,h_stack=16M,h_vmem=1124M,num_proc=1,processor=opteron_6174,s_rt=180000,s_vmem=1G '
        '-pe mpi 9:0.000000:NONE:821923840.000000:0:0')

        line_values = {"JobName": "6972834",
                        "LocalUserID":"csfiylfl",
                        "LocalUserGroup": "csic",
                        "WallDuration": int(wallmult*180001),
                        "CpuDuration": int(cputmult*1026707),
                        "StartTime": datetime.utcfromtimestamp(1318560254),
                        "StopTime": datetime.utcfromtimestamp(1318740255),
                        "MemoryReal":63131849389,
                        "MemoryVirtual": 821923840,
                        "NodeCount": 0,
                        "Processors": 9
                        }

        try:
            patcher = mock.patch.object(apel.parsers.sge.SGEParser,'_load_multipliers')
            fake = patcher.start()
            fake.return_value = { "compute-4-19.local": { "cputmult": cputmult, "wallmult": wallmult }}
            parser = apel.parsers.sge.SGEParser('testSite', 'testHost', True)
            record = parser.parse(line)
            cont = record._record_content
            for k,v in line_values.items():
                self.assertEqual(v, cont[k])
        finally:
            patcher.stop()

    def test_get_cpu_multiplier(self):
        '''
        Testing _get_cpu_multiplier() function with the following arguments:
            - Empty dictionary.
            - Dictionary with key 'cputmult'.
            - Dictionary with keys 'cputmult' and 'wallmult'.
        '''
        for d,v in [({}, 1.0),
                  ({"compute-4-19.local": {"cputmult": 2.0}}, 2.0),
                  ({"compute-4-19.local": {"cputmult": 2.0, "wallmult": 2.0}}, 2.0)]:
            try:
                patcher = mock.patch.object(apel.parsers.sge.SGEParser,'_load_multipliers')
                fake = patcher.start()
                fake.return_value = d
                parser = apel.parsers.sge.SGEParser('testSite', 'testHost', True)
                self.assertEqual(v, parser._get_cpu_multiplier('compute-4-19.local'))
            finally:
                patcher.stop()

    def test_get_wall_multiplier(self):
        '''
        Testing _get_wall_multiplier() function with the following arguments:
            - Empty dictionary.
            - Dictionary with key 'wallmult'.
            - Dictionary with keys 'cputmult' and 'wallmult'.
        '''
        for d,v in [({}, 1.0),
                  ({"compute-4-19.local": {"wallmult": 2.0}}, 2.0),
                  ({"compute-4-19.local": {"cputmult": 2.0, "wallmult": 2.0}}, 2.0)]:
            try:
                patcher = mock.patch.object(apel.parsers.sge.SGEParser,'_load_multipliers')
                fake = patcher.start()
                fake.return_value = d
                parser = apel.parsers.sge.SGEParser('testSite', 'testHost', True)
                self.assertEqual(v, parser._get_wall_multiplier('compute-4-19.local'))
            finally:
                patcher.stop()

    def test_load_multipliers_qhost_error(self):
        '''
        Testing load_multipliers() when qhost command exits with error.
        '''
        try:
            patcher = mock.patch('apel.parsers.sge.subprocess')
            subprocess = patcher.start()
            subprocess.Popen.return_value.returncode = 1
            subprocess.Popen.return_value.communicate = lambda: ('', 'foo')
            parser = apel.parsers.SGEParser('testSite', 'testHost', True)
            self.assertEqual({}, parser._load_multipliers())
        finally:
            patcher.stop()

    def test_load_multipliers_xml_unique(self):
        '''
        Testing either 'cputmult' or 'wallmult' appearances in the following conditions:
            - 'cputmult' with a valid (float) value.
            - 'cputmult' with a non-valid (string) value.
            - 'wallmult' with a valid (float) value.
            - 'wallmult' with a non-valid (string) value.
        '''
        qhost_output = """<?xml version='1.0'?>
            <qhost xmlns:xsd="http://arc.liv.ac.uk/repos/darcs/sge/source/dist/util/resources/schemas/qhost/qhost.xsd">
             <host name='global'>
               <hostvalue name='arch_string'>-</hostvalue>
               <hostvalue name='num_proc'>-</hostvalue>
               <hostvalue name='m_socket'>-</hostvalue>
               <hostvalue name='m_core'>-</hostvalue>
               <hostvalue name='m_thread'>-</hostvalue>
               <hostvalue name='load_avg'>-</hostvalue>
               <hostvalue name='mem_total'>-</hostvalue>
               <hostvalue name='mem_used'>-</hostvalue>
               <hostvalue name='swap_total'>-</hostvalue>
               <hostvalue name='swap_used'>-</hostvalue>
             </host>
             <host name='compute-4-19.local'>
               <hostvalue name='arch_string'>lx-amd64</hostvalue>
               <hostvalue name='num_proc'>24</hostvalue>
               <hostvalue name='m_socket'>24</hostvalue>
               <hostvalue name='m_core'>24</hostvalue>
               <hostvalue name='m_thread'>24</hostvalue>
               <hostvalue name='load_avg'>24.22</hostvalue>
               <hostvalue name='mem_total'>45.1G</hostvalue>
               <hostvalue name='mem_used'>22.4G</hostvalue>
               <hostvalue name='swap_total'>10.0G</hostvalue>
               <hostvalue name='swap_used'>132.5M</hostvalue>
               <resourcevalue name='%s' dominance='hf'>%s</resourcevalue>
             </host>
            </qhost>
        """
        for c,v,d in [('cputmult', 2.2, {'compute-4-19.local': {'cputmult': 2.2}}),
                      ('cputmult', 'foo', {}),
                      ('wallmult', 2.2, {'compute-4-19.local': {'wallmult': 2.2}}),
                      ('wallmult', 'foo', {})]:
            try:
                patcher = mock.patch('apel.parsers.sge.subprocess')
                subprocess = patcher.start()
                subprocess.Popen.return_value.returncode = 0
                subprocess.Popen.return_value.communicate = lambda: (qhost_output % (c,v), '')
                parser = apel.parsers.SGEParser('testSite', 'testHost', True)
                self.assertEqual(d, parser._load_multipliers())
            finally:
                patcher.stop()

    def test_load_multipliers_xml_both(self):
        '''
        For the sake of completeness with regard to the function above: testing both 'cputmult' and 'wallmult'
        appearances coexisting in the following conditions:
            - 'cputmult' with a valid (float) value ; 'wallmult' with a non-valid (string) value.
            - 'cputmult' with a non-valid (string) value ; 'wallmult' with a valid (float) value.
            - both 'cputmult' and 'wallmult' with a valid (float) value.
            - both 'cputmult' and 'wallmult' with a non-valid (string) value.
        '''
        qhost_output = """<?xml version='1.0'?>
            <qhost xmlns:xsd="http://arc.liv.ac.uk/repos/darcs/sge/source/dist/util/resources/schemas/qhost/qhost.xsd">
             <host name='global'>
               <hostvalue name='arch_string'>-</hostvalue>
               <hostvalue name='num_proc'>-</hostvalue>
               <hostvalue name='m_socket'>-</hostvalue>
               <hostvalue name='m_core'>-</hostvalue>
               <hostvalue name='m_thread'>-</hostvalue>
               <hostvalue name='load_avg'>-</hostvalue>
               <hostvalue name='mem_total'>-</hostvalue>
               <hostvalue name='mem_used'>-</hostvalue>
               <hostvalue name='swap_total'>-</hostvalue>
               <hostvalue name='swap_used'>-</hostvalue>
             </host>
             <host name='compute-4-19.local'>
               <hostvalue name='arch_string'>lx-amd64</hostvalue>
               <hostvalue name='num_proc'>24</hostvalue>
               <hostvalue name='m_socket'>24</hostvalue>
               <hostvalue name='m_core'>24</hostvalue>
               <hostvalue name='m_thread'>24</hostvalue>
               <hostvalue name='load_avg'>24.22</hostvalue>
               <hostvalue name='mem_total'>45.1G</hostvalue>
               <hostvalue name='mem_used'>22.4G</hostvalue>
               <hostvalue name='swap_total'>10.0G</hostvalue>
               <hostvalue name='swap_used'>132.5M</hostvalue>
               <resourcevalue name='cputmult' dominance='hf'>%s</resourcevalue>
               <resourcevalue name='wallmult' dominance='hf'>%s</resourcevalue>
             </host>
            </qhost>
        """
        for c,w,d in [(2.2, 'foo', {'compute-4-19.local': {'cputmult': 2.2}}),
                      ('foo', 2.2, {'compute-4-19.local': {'wallmult': 2.2}}),
                      (2.2, 2.2, {'compute-4-19.local': {'cputmult': 2.2, 'wallmult': 2.2}}),
                      ('foo', 'bar', {})]:
            try:
                patcher = mock.patch('apel.parsers.sge.subprocess')
                subprocess = patcher.start()
                subprocess.Popen.return_value.returncode = 0
                subprocess.Popen.return_value.communicate = lambda: (qhost_output % (c,w), '')
                parser = apel.parsers.SGEParser('testSite', 'testHost', True)
                self.assertEqual(d, parser._load_multipliers())
            finally:
                patcher.stop()

    def test_mpi_false(self):
        """Check that non-mpi parsers return zero procs even if at least 1."""
        line = ('dteam:testce.test:dteam:dteam041:STDIN:43:sge:19:1200093286:12'
                '00093294:1200093295:0:0:1:0:0:0.000000:0:0:0:0:46206:0:0:0.0:0'
                ':0:0:0:337:257:NONE:defaultdepartment:NONE:1:0:0.09:0.000213:0'
                '.0:-U dteam -q dteam:0.0:NONE:30171136.0')
        parser = apel.parsers.SGEParser('testSite', 'testHost', False)
        record = parser.parse(line)
        self.assertEqual(record._record_content['Processors'], 0,
                         "Processors not zero for non-mpi parser")


if __name__ == '__main__':
    unittest.main()
