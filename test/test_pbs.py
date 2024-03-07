import datetime
import unittest

from apel.parsers import PBSParser
from apel.parsers.pbs import _parse_mpi


class ParserPBSTest(unittest.TestCase):
    '''
    Test case for PBS parser
    '''

    def setUp(self):
        self.parser = PBSParser('testSite', 'testHost', True)

    def test_parse(self):
        lines = (
            ('10/02/2011 06:41:44;E;21048463.lcgbatch01.gridpp.rl.ac.uk;user=patls009 group=prodatls jobname=cre09_443343882 queue=grid4000M '
             'ctime=1317509574 qtime=1317509574 etime=1317509574 start=1317509945 owner=patls009@lcgce09.gridpp.rl.ac.uk '
             'exec_host=lcg1277.gridpp.rl.ac.uk/5 Resource_List.cput=96:00:00 Resource_List.neednodes=lcg1277.gridpp.rl.ac.uk '
             'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.pmem=4000mb Resource_List.walltime=96:00:00 session=20374 '
             'end=1317534104 Exit_status=0 resources_used.cput=18:15:24 resources_used.mem=2031040kb resources_used.vmem=3335528kb resources_used.walltime=19:23:4'),
            ('10/01/2011 01:05:30;E;21010040.lcgbatch01.gridpp.rl.ac.uk;user=plhcb010 group=prodlhcb jobname=cre09_655648918 '
             'queue=gridWN ctime=1317427361 qtime=1317427361 etime=1317427361 start=1317427530 owner=plhcb010@lcgce09.gridpp.rl.ac.uk '
             'exec_host=lcg0766.gridpp.rl.ac.uk/7+lcg0766.gridpp.rl.ac.uk/6+lcg0766.gridpp.rl.ac.uk/5+lcg0766.gridpp.rl.ac.uk/4+'
             'lcg0766.gridpp.rl.ac.uk/3+lcg0766.gridpp.rl.ac.uk/2+lcg0766.gridpp.rl.ac.uk/1+lcg0766.gridpp.rl.ac.uk/0 '
             'Resource_List.cput=800:00:00 Resource_List.neednodes=1:ppn=8 Resource_List.nodect=1 Resource_List.nodes=1:ppn=8 '
             'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.walltime=96:00:00 session=7428 end=1317427530 '
             'Exit_status=0 resources_used.cput=00:00:00 resources_used.mem=0kb resources_used.vmem=0kb resources_used.walltime=00:00:00'),
            ('11/30/2015 15:39:52;E;24940336.b0;user=atlaspt5 group=atlaspt jobname=cream_830820758 queue=atlas ctime=1448913907 qtime=1448913907 et'
             'ime=1448913907 start=1448914025 owner=atlaspt5@bugaboo-hep.westgrid.ca exec_host=b341/2 Resource_List.file=15gb Resource_List.neednode'
             's=1 Resource_List.nodect=1 Resource_List.nodes=1 Resource_List.pmem=2000mb Resource_List.pvmem=4000mb Resource_List.vmem=4000mb Resour'
             'ce_List.walltime=48:00:00 session=22256 total_execution_slots=1 unique_node_count=1 end=1448926792 Exit_status=271 resources_used.cput'
             '=03:32:02 resources_used.energy_used=0 resources_used.mem=2574308kb resources_used.vmem=4032516kb resources_used.walltime=03:32:47'),
            # This example is from Torque 5.1.2 where time is now in seconds
            ('11/30/2015 15:42:06;E;24940336.b0;user=atlaspt5 group=atlaspt jobname=cream_830820758 queue=atlas ctime=1448913907 qtime=1448913907 et'
             'ime=1448913907 start=1448914025 owner=atlaspt5@bugaboo-hep.westgrid.ca exec_host=b341/2 Resource_List.file=15gb Resource_List.neednode'
             's=1 Resource_List.nodect=1 Resource_List.nodes=1 Resource_List.pmem=2000mb Resource_List.pvmem=4000mb Resource_List.vmem=4000mb Resour'
             'ce_List.walltime=48:00:00 session=22256 total_execution_slots=1 unique_node_count=1 end=1448926926 Exit_status=0 resources_used.cput=1'
             '2722 resources_used.energy_used=0 resources_used.mem=2574308kb resources_used.vmem=4032516kb resources_used.walltime=12767'),
            # Torque-4.2.8 reports cores as exec_host=b372/4+b372/5+b372/6+b372/7
            ('03/21/2015 12:10:19;E;21414868.b0;user=atprd008 group=atprd jobname=cream_944593744 queue=atlas ctime=1426952581 qtime=1426952581 etim'
             'e=1426952581 start=1426952875 owner=atprd008@bugaboo-hep.westgrid.ca exec_host=b372/4+b372/5+b372/6+b372/7 Resource_List.file=15gb Res'
             'ource_List.nodect=1 Resource_List.nodes=1pn=4 Resource_List.pmem=2666mb Resource_List.vmem=16000mb Resource_List.walltime=16:00:00 ses'
             'sion=5353 end=1426965019 Exit_status=0 resources_used.cput=13:01:39 resources_used.mem=7813056kb resources_used.vmem=12127680kb resour'
             'ces_used.walltime=03:22:24'),
            # Torque 5.1.0 reports cores as exec_host=b391/0-3 and total_execution_slots=4
            ('20150327:03/27/2015 00:06:27;E;21430205.b0;user=atprd006 group=atprd jobname=cream_238467179 queue=atlas ctime=1427422724 qtime=142742'
             '2724 etime=1427422724 start=1427422975 owner=atprd006@bugaboo-hep.westgrid.ca exec_host=b391/0-3 Resource_List.file=15gb Resource_List'
             '.neednodes=1pn=4 Resource_List.nodect=1 Resource_List.nodes=1pn=4 Resource_List.pmem=2666mb Resource_List.vmem=16000mb Resource_List.w'
             'alltime=16:00:00 session=26754 total_execution_slots=4 unique_node_count=1 end=1427439987 Exit_status=0 resources_used.cput=18:31:56 r'
             'esources_used.energy_used=0 resources_used.mem=8212056kb resources_used.vmem=12526772kb resources_used.walltime=04:43:32'),
            # Torque 5.1.3 has cput in secondss but walltime in hh:mm:ss
            ('12/07/2016 01:08:31;E;37803854.b0;user=atcant2 group=atcant jobna'
             'me=cream_105055799 queue=atlas ctime=1481101558 qtime=1481101558 '
             'etime=1481101558 start=1481101655 owner=atcant@bug.eastgrid.io ex'
             'ec_host=b126/2 Resource_List.file=15gb Resource_List.neednodes=1 '
             'Resource_List.nodect=1 Resource_List.nodes=1 Resource_List.pmem=2'
             '000mb Resource_List.walltime=50:00:00 session=1664 total_executio'
             'n_slots=1 unique_node_count=1 end=1481101711 Exit_status=0 resour'
             'ces_used.cput=9 resources_used.energy_used=0 resources_used.mem=4'
             '1512kb resources_used.vmem=325428kb resources_used.walltime=00:00'
             ':56'),
        )

        values = (
            ("21048463.lcgbatch01.gridpp.rl.ac.uk", "patls009", "prodatls",
             69784, 65724, datetime.datetime.utcfromtimestamp(1317509945),
             datetime.datetime.utcfromtimestamp(1317534104), 2031040, 3335528,
             1, 1),
            ("21010040.lcgbatch01.gridpp.rl.ac.uk", "plhcb010", "prodlhcb", 0,
             0, datetime.datetime.utcfromtimestamp(1317427530),
             datetime.datetime.utcfromtimestamp(1317427530), 0, 0, 1, 8),
            ("24940336.b0", "atlaspt5", "atlaspt", 3*3600+32*60+47,
             3*3600+32*60+2, datetime.datetime.utcfromtimestamp(1448914025),
             datetime.datetime.utcfromtimestamp(1448926792), 2574308, 4032516,
             1, 1),
            ("24940336.b0", "atlaspt5", "atlaspt", 12767, 12722,
             datetime.datetime.utcfromtimestamp(1448914025),
             datetime.datetime.utcfromtimestamp(1448926926), 2574308, 4032516,
             1, 1),
            ("21414868.b0", "atprd008", "atprd", 3*3600+22*60+24,
             13*3600+1*60+39, datetime.datetime.utcfromtimestamp(1426952875),
             datetime.datetime.utcfromtimestamp(1426965019), 7813056, 12127680,
             1, 4),
            ("21430205.b0", "atprd006", "atprd", 4*3600+43*60+32,
             18*3600+31*60+56, datetime.datetime.utcfromtimestamp(1427422975),
             datetime.datetime.utcfromtimestamp(1427439987), 8212056, 12526772,
             1, 4),
            ("37803854.b0", "atcant2", "atcant", 56, 9,
             datetime.datetime.utcfromtimestamp(1481101655),
             datetime.datetime.utcfromtimestamp(1481101711), 41512, 325428,
             1, 1),
        )

        fields = ('JobName', 'LocalUserID', 'LocalUserGroup', 'WallDuration',
                  'CpuDuration', 'StartTime', 'StopTime', 'MemoryReal',
                  'MemoryVirtual', 'NodeCount', 'Processors')

        cases = {}
        for line, value in zip(lines, values):
            cases[line] = dict(zip(fields, value))

        for line in cases.keys():

            record = self.parser.parse(line)
            cont = record._record_content

            self.assertEqual(cont['Site'], 'testSite')
            self.assertEqual(cont['Infrastructure'], 'APEL-CREAM-PBS')
            self.assertEqual(cont['MachineName'], 'testHost')

            for key in cases[line].keys():
                # Check all fields are present
                self.assertTrue(key in cont, "Key '%s' not in record." % key)
                # Check values are correct
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

        exec_hosts = ('lcg0766.gridpp.rl.ac.uk/7+lcg0766.gridpp.rl.ac.uk/6+lcg0766.gridpp.rl.ac.uk/5+lcg0766.gridpp.rl.ac.uk/4+lcg0766.gridpp.rl.ac.uk/3+lcg0766.gridpp.rl.ac.uk/2+lcg0766.gridpp.rl.ac.uk/1+lcg0766.gridpp.rl.ac.uk/0',
                      'b372/4+b372/5+b372/6+b372/7',
                      'b391/0-3',
                      'b391/0-1,5,11',
                      )
        # List of (node, cpu) counts for above exec_hosts
        counts = ((1, 8),
                  (1, 4),
                  (1, 4),
                  (1, 4),
                  )
        for exec_host, count in zip(exec_hosts, counts):
            nodecount, processors = _parse_mpi(exec_host)

            self.assertEqual(nodecount, count[0])
            self.assertEqual(processors, count[1])

    def test_value_errors(self):
        """Test that the parser raises a ValueError for certain problems."""
        lines = (
            # End time less than start time
            ('11/30/2015 15:39:52;E;24940336.b0;user=atlaspt5 group=atlaspt jobname=cream_830820758 queue=atlas ctime=1448913907 qtime=1448913907 et'
             'ime=1448913907 start=1448926792 owner=atlaspt5@bugaboo-hep.westgrid.ca exec_host=b341/2 Resource_List.file=15gb Resource_List.neednode'
             's=1 Resource_List.nodect=1 Resource_List.nodes=1 Resource_List.pmem=2000mb Resource_List.pvmem=4000mb Resource_List.vmem=4000mb Resour'
             'ce_List.walltime=48:00:00 session=22256 total_execution_slots=1 unique_node_count=1 end=1448914025 Exit_status=271 resources_used.cput'
             '=03:32:02 resources_used.energy_used=0 resources_used.mem=2574308kb resources_used.vmem=4032516kb resources_used.walltime=03:32:47'),
        )

        for line in lines:
            self.assertRaises(ValueError, self.parser.parse, line)

    def test_incomplete_job(self):
        """Test that the parser returns None for an incomplete job."""
        line = ('11/30/2015 15:42:06;A;24940336.b0;user=atlaspt5 group=atlaspt jobname=cream_830820758 queue=atlas ctime=1448913907 qtime=1448913907 et'
                'ime=1448913907 start=1448914025 owner=atlaspt5@bugaboo-hep.westgrid.ca exec_host=b341/2 Resource_List.file=15gb Resource_List.neednode'
                's=1 Resource_List.nodect=1 Resource_List.nodes=1 Resource_List.pmem=2000mb Resource_List.pvmem=4000mb Resource_List.vmem=4000mb Resour'
                'ce_List.walltime=48:00:00 session=22256 total_execution_slots=1 unique_node_count=1 end=1448926926 Exit_status=0 resources_used.cput=1'
                '2722 resources_used.energy_used=0 resources_used.mem=2574308kb resources_used.vmem=4032516kb resources_used.walltime=12767')

        self.assertEqual(self.parser.parse(line), None)

    def test_non_mpi(self):
        """Test that node and cpu count are set to zero if MPI isn't used."""
        parser = PBSParser('testSite', 'testHost', False)

        line = ('10/01/2011 01:05:30;E;21010040.lcgbatch01.gridpp.rl.ac.uk;user=plhcb010 group=prodlhcb jobname=cre09_655648918 '
                'queue=gridWN ctime=1317427361 qtime=1317427361 etime=1317427361 start=1317427530 owner=plhcb010@lcgce09.gridpp.rl.ac.uk '
                'Resource_List.cput=800:00:00 Resource_List.neednodes=1:ppn=8 Resource_List.nodect=1 Resource_List.nodes=1:ppn=8 '
                'Resource_List.opsys=sl5 Resource_List.pcput=96:00:00 Resource_List.walltime=96:00:00 session=7428 end=1317427530 '
                'Exit_status=0 resources_used.cput=00:00:00 resources_used.mem=0kb resources_used.vmem=0kb resources_used.walltime=00:00:00')

        record = parser.parse(line)
        cont = record._record_content

        self.assertEqual(cont['NodeCount'], 0)
        self.assertEqual(cont['Processors'], 0)

if __name__ == '__main__':
    unittest.main()
