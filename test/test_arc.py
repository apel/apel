import StringIO
import unittest

from apel.db.records.job import JobRecord
from apel.parsers.arc import ARCParser


class ARCParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = ARCParser('testSite', 'testHost', True)

    def test_parse_file(self):
        """
        Test that the parser returns a JobRecord and the right number of lines.
        """
        arcfile = StringIO.StringIO(complete)

        record, lines = self.parser.parse_arc_file(arcfile)
        self.assertEqual(type(record), JobRecord)
        self.assertEqual(lines, 29)

        arcfile.close()

    def test_parse_empty_file(self):
        """
        Test that the parser returns None and 0 for an empty file.
        """
        empty_file = StringIO.StringIO("")

        record, lines = self.parser.parse_arc_file(empty_file)
        self.assertEqual(record, None)
        self.assertEqual(lines, 0)

        empty_file.close()

    def test_invalid_file(self):
        """
        Test that the parser raises an exception for an invalid file.
        """
        invalid_file = StringIO.StringIO("valid=line\ninvalid line")

        self.assertRaises(ValueError, self.parser.parse_arc_file, invalid_file)

        invalid_file.close()

    def test_parse_incomplete_job(self):
        """
        Test that the parser returns None and >0 for an incomplete job.
        """
        incomplete_job = StringIO.StringIO(incomplete)

        record, lines = self.parser.parse_arc_file(incomplete_job)
        self.assertEqual(record, None)
        self.assertNotEqual(lines, 0)

        incomplete_job.close()


complete = r"""loggerurl=APEL:http://mq.cro-ngi.hr:6162
accounting_options=urbatch:1000,archiving:/var/run/arc/urs,topic:/queue/global.accounting.cpu.central,gocdb_name:RAL-LCG2,use_ssl:true,Network:PROD,benchmark_type:Si2k,benchmark_value:1006.00
key_path=/etc/grid-security/hostkey.pem
certificate_path=/etc/grid-security/hostcert.pem
ca_certificates_dir=/etc/grid-security/certificates
description=&("savestate" = "yes" )("action" = "request" )("hostname" = "glidein.grid.iu.edu" )("executable" = "glidein_startup.sh" )("arguments" = "-v" "std" "-name" "gfactory_instance" "-entry" "CMS_T1_UK_RAL_arc_ce01" "-clientname" "CMSG-v1_0.t1prod" "-schedd" "schedd_glideins8@glidein.grid.iu.edu" "-proxy" "None" "-factory" "OSGGOC" "-web" "http://glidein.grid.iu.edu/factory/stage" "-sign" "95f5ff67925c4976de866257cbec03c2ef8cf735" "-signentry" "583d7f81aa05e0ee7c48e1c361aeea98b0d14307" "-signtype" "sha1" "-descript" "description.f5djRC.cfg" "-descriptentry" "description.f5djRC.cfg" "-dir" "TMPDIR" "-param_GLIDEIN_Client" "CMSG-v1_0.t1prod" "-submitcredid" "190564" "-slotslayout" "fixed" "-clientweb" "http://vocms080.cern.ch/vofrontend/stage" "-clientsign" "baf78ef8937facc5c909a88c12424ef391c92cf8" "-clientsigntype" "sha1" "-clientdescript" "description.f5bd1b.cfg" "-clientgroup" "t1prod" "-clientwebgroup" "http://vocms080.cern.ch/vofrontend/stage/group_t1prod" "-clientsigngroup" "fa57085cac8f9ef9b4b392164b55425d6e98755a" "-clientdescriptgroup" "description.f4kerW.cfg" "-param_CONDOR_VERSION" "8.dot,3.dot,2" "-param_GLIDEIN_Glexec_Use" "OPTIONAL" "-param_GLIDEIN_Job_Max_Time" "34800" "-param_GLIDECLIENT_ReqNode" "glidein.dot,grid.dot,iu.dot,edu" "-param_CONDOR_OS" "default" "-param_MIN_DISK_GBS" "1" "-param_GLIDEIN_Max_Idle" "2400" "-param_GLIDEIN_Monitoring_Enabled" "False" "-param_CONDOR_ARCH" "default" "-param_UPDATE_COLLECTOR_WITH_TCP" "True" "-param_USE_MATCH_AUTH" "True" "-param_GLIDEIN_Report_Failed" "NEVER" "-param_GLIDEIN_Collector" "vocms099.dot,cern.dot,ch.colon,9620.minus,10000.semicolon,vocms097.dot,cern.dot,ch.colon,9620.minus,10000" "-cluster" "2662132" "-subcluster" "9" )("executables" = "glidein_startup.sh" )("inputfiles" = (".gahp_complete" "" ) ("glidein_startup.sh" "" ) )("stdout" = "_condor_stdout.schedd_glideins8_glidein.grid.iu.edu_2662132.9_1432020406" )("stderr" = "_condor_stderr.schedd_glideins8_glidein.grid.iu.edu_2662132.9_1432020406" )("outputfiles" = ("_condor_stdout.schedd_glideins8_glidein.grid.iu.edu_2662132.9_1432020406" "" ) ("_condor_stderr.schedd_glideins8_glidein.grid.iu.edu_2662132.9_1432020406" "" ) )("memory" = "3050" )("runtimeenvironment" = "ENV/GLITE" )
localuser=pcms024
submissiontime=20150519072708Z
ngjobid=WcyNDmp6qEmnCIXDjqiBL5XqABFKDmABFKDmdaGKDmJBFKDm2hQmpn
usersn=/DC=ch/DC=cern/OU=computers/CN=cmspilot02/vocms080.cern.ch
headnode=gsiftp://arc-ce01.gridpp.rl.ac.uk:2811/jobs
lrms=condor
queue=grid3000M
localid=3710625.arc-ce01.gridpp.rl.ac.uk
globalid=gsiftp://arc-ce01.gridpp.rl.ac.uk:2811/jobs/WcyNDmp6qEmnCIXDjqiBL5XqABFKDmABFKDmdaGKDmJBFKDm2hQmpn
clienthost=129.79.53.27:54085
usercert=-----BEGIN CERTIFICATE-----\ ___SNIP___ \-----END CERTIFICATE-----\
requestedmemory=3050
processors=1
usedwalltime=47192
usedusercputime=38047
usedkernelcputime=2783
usedmemory=1000000
exitcode=0
nodename=slot1@lcg1526.gridpp.rl.ac.uk
nodecount=1
usedcputime=40830
endtime=20150519133100Z
status=completed
"""

incomplete = r"""loggerurl=APEL:http://mq.cro-ngi.hr:6162
accounting_options=urbatch:1000,archiving:/var/run/arc/urs,topic:/queue/global.accounting.cpu.central,gocdb_name:RAL-LCG2,use_ssl:true,Network:PROD,benchmark_type:Si2k,benchmark_value:1006.00
key_path=/etc/grid-security/hostkey.pem
certificate_path=/etc/grid-security/hostcert.pem
ca_certificates_dir=/etc/grid-security/certificates
description=&("savestate" = "yes" )("action" = "request" )("hostname" = "aipanda062.cern.ch" )("executable" = "runpilot3-wrapper.sh" )("arguments" = "-s" "ANALY_RAL_SL6" "-h" "ANALY_RAL_SL6" "-p" "25443" "-w" "https://pandaserver.cern.ch" "-u" "user" )("executables" = "runpilot3-wrapper.sh" )("inputfiles" = (".gahp_complete" "" ) ("runpilot3-wrapper.sh" "" ) )("stdout" = "_condor_stdout.aipanda062.cern.ch_5943946.21_1432043893" )("stderr" = "_condor_stderr.aipanda062.cern.ch_5943946.21_1432043893" )("outputfiles" = ("_condor_stdout.aipanda062.cern.ch_5943946.21_1432043893" "" ) ("_condor_stderr.aipanda062.cern.ch_5943946.21_1432043893" "" ) )("queue" = "grid3000M" )("runtimeenvironment" = "APPS/HEP/ATLAS-SITE-LCG" )("runtimeenvironment" = "ENV/PROXY" )("jobname" = "arc_pilot" )("memory" = "3000" )("walltime" = "345600" )("environment" = ("APFFID" "aipanda062-glexecdev" ) ("PANDA_JSID" "aipanda062-glexecdev" ) ("APFCID" "5943946.21" ) ("GTAG" "http://aipanda062.cern.ch/pilots/2015-05-19/ANALY_RAL_SL6-5495-dev/5943946.21.out" ) ("APFMON" "http://apfmon.lancs.ac.uk/api" ) ("FACTORYQUEUE" "ANALY_RAL_SL6-5495-dev" ) ("FACTORYUSER" "apf" ) ("RUCIO_ACCOUNT" "pilot" ) )
localuser=tatls015
submissiontime=20150519135824Z
ngjobid=0JENDmUDxEmnCIXDjqiBL5XqABFKDmABFKDm5fVKDmMBFKDmT9YYQm
usersn=/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=atlpilo1/CN=614260/CN=Robot: ATLAS Pilot1
headnode=gsiftp://arc-ce01.gridpp.rl.ac.uk:2811/jobs
lrms=condor
queue=grid3000M
jobname=arc_pilot
globalid=gsiftp://arc-ce01.gridpp.rl.ac.uk:2811/jobs/0JENDmUDxEmnCIXDjqiBL5XqABFKDmABFKDm5fVKDmMBFKDmT9YYQm
clienthost=128.142.200.45:56669
requestedmemory=3000
requestedwalltime=345600
"""


if __name__ == '__main__':
    unittest.main()
