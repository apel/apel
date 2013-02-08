import datetime
from unittest import TestCase
from apel.parsers import LSFParser

class ParserLSFTest(TestCase):
    '''
    Test case for LSF parser
    '''
    
    def setUp(self):
        self.parser = LSFParser('testSite', 'testHost', True)
        

    def test_parse(self):
        line1 = ('"JOB_FINISH" "5.1" 1089407406 699195 283 33554482 1 1089290023 0 0 1089406862 '
                '"raortega" "8nm" "" "" "" "lxplus015" "prog/step3c" "" "/afs/cern.ch/user/r/raortega/log/bstep3c-362.txt" '
                '"/afs/cern.ch/user/r/raortega/log/berr-step3c-362.txt" "1089290023.699195" 0 1 "tbed0079" 64 3.3 "" '
                '"/afs/cern.ch/user/r/raortega/prog/step3c/startEachset.pl 362 7 8" 277.210000 17.280000 0 0 -1 0 0 927804'
                ' 87722 0 0 0 -1 0 0 0 0 0 -1 "" "default" 0 1 "" "" 0 310424 339112 "" "" ""')
        
        line1_values = {"JobName": "699195", 
                        "LocalUserID":"raortega", 
                        "LocalUserGroup": None, 
                        "WallDuration":544, 
                        "CpuDuration": 294,
                        "StartTime": datetime.datetime.utcfromtimestamp(1089406862),
                        "StopTime": datetime.datetime.utcfromtimestamp(1089407406),
                        "MemoryReal":310424,
                        "MemoryVirtual": 339112,
                        "NodeCount": 1,
                        "Processors": 1
                        }
        
        # MPI information
        line2 = ('"JOB_FINISH" "7.06" 1302184020 436491 10001 33816691 16 1302184001 0 0 1302184004 "viglen" "normal" '
                 '" span[ptile=8] cu[maxcus=1]" "" "" "comp000" "benchmarks/IMB_3.0/bin/bsub" "" "IMB.%J.%I.out" '
                 '"IMB.%J.%I.err" "1302184001.436491" 0 16 "comp042" "comp042" "comp042" "comp042" "comp042" "comp042" '
                 '"comp042" "comp042" "comp043" "comp043" "comp043" "comp043" "comp043" "comp043" "comp043" "comp043" 32'
                 ' 60.0 "imb_sr[1-90]" "#!/bin/bash; #BSUB -n 16;#BSUB -R \'span[ptile=8]\';#BSUB -R \'cu[maxcus=1]\';#BSUB '
                 '-x;#BSUB -J imb_sr[1-90];####BSUB -m ""comp000 comp001"";#BSUB -o IMB.%J.%I.out;#BSUB -e IMB.%J.%I.err; '
                 '# Output some env vars;echo ""LSB_HOSTS: $LSB_HOSTS"";echo ""LSB_MCPU_HOSTS: $LSB_MCPU_HOSTS"";echo '
                 '""LSB_DJOB_HOSTFILE: $LSB_DJOB_HOSTFILE"";echo ""LSB_DJOB_HOSTFILE (cat):""; cat $LSB_DJOB_HOSTFILE; '
                 'HOSTLIST=`cat $LSB_DJOB_HOSTFILE | uniq | tr ""\n"" "" ""`; . /etc/profile; module add MPI/PMPI;cd '
                 '/home/test/viglen/benchmarks/IMB_3.0/bin/ ;#mpirun -np $LSB_DJOB_NUMPROC ./imb-pmpi -msglen ./IMB_msglen '
                 '-map 2x8 -npmin 16 sendrecv;#mpirun -d -prot -np $LSB_DJOB_NUMPROC -hostlist ""comp000 comp001"" '
                 './imb-pmpi -msglen ./IMB_msglen -map 2x8 -npmin 16 sendrecv;mpirun -d -prot -np $LSB_DJOB_NUMPROC '
                 '-hostlist ""$HOSTLIST"" ./imb-pmpi -msglen ./IMB_msglen -map 2x8 -npmin 16 sendrecv" 0.472928 1.112830 '
                 '0 0 -1 0 0 149746 0 0 0 0 -1 0 0 0 1907 1746 -1 "" "default" 65280 16 "" "" 23 2 25 "" "" "" "" 0 "" 0 ""'
                 ' -1 "/viglen" "" "default" "" -1 "" "" 6160  "" 1302184004 "" "" 0')

        line2_values = {"JobName": "436491", 
                        "LocalUserID":"viglen", 
                        "LocalUserGroup": None, 
                        "WallDuration":16, 
                        "CpuDuration": 2,
                        "StartTime": datetime.datetime.utcfromtimestamp(1302184004),
                        "StopTime": datetime.datetime.utcfromtimestamp(1302184020),
                        "MemoryReal":2,
                        "MemoryVirtual": 25,
                        "NodeCount": 2,
                        "Processors": 16
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
        
        
    def test_invalid_expr(self):
        # two fields are not separated by space
        line = ('"JOB_FINISH" "5.1" 1089407406 699195 283 33554482 1 1089290023 0 0 1089406862 '
                '"raortega" "8nm" "" "" "" "lxplus015" "prog/step3c" "" "/afs/cern.ch/user/r/raortega/log/bstep3c-362.txt" '
                '"/afs/cern.ch/user/r/raortega/log/berr-step3c-362.txt""1089290023.699195" 0 1 "tbed0079" 64 3.3 "" '
                '"/afs/cern.ch/user/r/raortega/prog/step3c/startEachset.pl362 7 8" 277.210000 17.280000 0 0 -1 0 0 927804'
                ' 87722 0 0 0 -1 0 0 0 0 0 -1 "" "default" 0 1 "" "" 0 310424 339112 "" "" ""')
        
        self.assertRaises(IndexError, self.parser.parse, line)
    
    def test_invalid_version(self):
        # unsupported version
        line = ('"JOB_FINISH" "9.1" 1089407406 699195 283 33554482 1 1089290023 0 0 1089406862 '
                '"raortega" "8nm" "" "" "" "lxplus015" "prog/step3c" "" "/afs/cern.ch/user/r/raortega/log/bstep3c-362.txt" '
                '"/afs/cern.ch/user/r/raortega/log/berr-step3c-362.txt" "1089290023.699195" 0 1 "tbed0079" 64 3.3 "" '
                '"/afs/cern.ch/user/r/raortega/prog/step3c/startEachset.pl362 7 8" 277.210000 17.280000 0 0 -1 0 0 927804'
                ' 87722 0 0 0 -1 0 0 0 0 0 -1 "" "default" 0 1 "" "" 0 310424 339112 "" "" ""')
        
        self.assertRaises(KeyError, self.parser.parse, line)