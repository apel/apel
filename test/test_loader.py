import dirq
import mock
import os
import shutil
import tempfile
import unittest
import logging
from mock import call

import apel.db.loader

schema = {"body": "string", "signer": "string",
          "empaid": "string?", "error": "string?"}


class LoaderTest(unittest.TestCase):

    def setUp(self):
        # Create temporary directory for message queues and pidfiles
        self.dir_path = tempfile.mkdtemp()

        # Mock out the database as we're not testing that here
        # Note that as it's a class it needs instantiating
        self.mock_db = mock.patch('apel.db.ApelDb', autospec=True,
                                  spec_set=True).start()()

    def test_startup_fail(self):
        """Check that startup fails due to extant pidfile."""
        handle, extant_pid = tempfile.mkstemp()
        os.close(handle)
        loader = apel.db.loader.Loader(self.dir_path, False, 'mysql', 'host',
                                       1234, 'db', 'user', 'pwd', extant_pid)
        self.assertRaises(apel.db.loader.LoaderException, loader.startup)
        os.remove(extant_pid)

    def test_startup_shutdown(self):
        """Check that pidfile is created on startup and removed on shutdown."""
        pidfile = os.path.join(self.dir_path, 'pidfile')
        loader = apel.db.loader.Loader(self.dir_path, False, 'mysql', 'host',
                                       1234, 'db', 'user', 'pwd', pidfile)

        loader.startup()
        self.assertTrue(os.path.exists(pidfile))

        loader.shutdown()
        self.assertFalse(os.path.exists(pidfile))

    def test_load_all_empty(self):
        """Check that load_records is called with an empty list."""
        logger = logging.getLogger('loader')
        pidfile = os.path.join(self.dir_path, 'pidfile')

        in_q = dirq.queue.Queue(os.path.join(self.dir_path, 'incoming'),
                                schema=schema)
        in_q.add({"body": "bad message", "signer": "test signer", "empaid": "",
                  "error": ""})
        in_q.add({"body": "APEL-summary-job-message: v0.3",
                  "signer": "test signer", "empaid": "", "error": ""})

        self.loader = apel.db.loader.Loader(self.dir_path, True, 'mysql',
                                            'host', 1234, 'db', 'user', 'pwd',
                                            pidfile)

        with mock.patch.object(logger, 'info') as mock_log:
            self.loader.load_all_msgs()
            self.mock_db.load_records.assert_called_once_with([],
                                                          source='test signer')
            # Test that logging is called correctly when there are no records
            mock_log.assert_has_calls([call('Message contains 0 records')])

    def test_load_all(self):
        """Check that load_records is called and message is logged correctly."""
        logger = logging.getLogger('loader')
        pidfile = os.path.join(self.dir_path, 'pidfile')

        in_q = dirq.queue.Queue(os.path.join(self.dir_path, 'incoming'),
                                schema=schema)

        in_q.add({"body": """APEL-summary-job-message: v0.2
                    Site: RAL-LCG2
                    Month: 3
                    Year: 2010
                    GlobalUserName: /C=whatever/D=someDN
                    VO: atlas
                    VOGroup: /atlas
                    VORole: Role=production
                    WallDuration: 234256
                    CpuDuration: 2345
                    NumberOfJobs: 100
                    %%
                    Site: RAL-LCG2
                    Month: 4
                    Year: 2010
                    GlobalUserName: /C=whatever/D=someDN
                    VO: atlas
                    VOGroup: /atlas
                    VORole: Role=production
                    WallDuration: 234256
                    CpuDuration: 2345
                    NumberOfJobs: 100
                    %%""",
                  "signer": "test signer", "empaid": "", "error": ""})

        self.loader = apel.db.loader.Loader(self.dir_path, True, 'mysql',
                                            'host', 1234, 'db', 'user', 'pwd',
                                            pidfile)

        with mock.patch.object(logger, 'info') as mock_log:
            self.loader.load_all_msgs()
            self.mock_db.load_records.assert_called_once()
            mock_log.assert_has_calls(
                        [call('Message contains %i %s records', 2, 'Summary')])

    def test_load_all_single_record(self):
        """Check that load_records is called and message is logged correctly for a single record."""
        logger = logging.getLogger('loader')
        pidfile = os.path.join(self.dir_path, 'pidfile')

        in_q = dirq.queue.Queue(os.path.join(self.dir_path, 'incoming'),
                                schema=schema)

        in_q.add({"body": """APEL-summary-job-message: v0.2
                    Site: RAL-LCG2
                    Month: 3
                    Year: 2010
                    GlobalUserName: /C=whatever/D=someDN
                    VO: atlas
                    VOGroup: /atlas
                    VORole: Role=production
                    WallDuration: 234256
                    CpuDuration: 2345
                    NumberOfJobs: 100
                    %%""",
                  "signer": "test signer", "empaid": "", "error": ""})

        self.loader = apel.db.loader.Loader(self.dir_path, True, 'mysql',
                                            'host', 1234, 'db', 'user', 'pwd',
                                            pidfile)

        with mock.patch.object(logger, 'info') as mock_log:
            self.loader.load_all_msgs()
            self.mock_db.load_records.assert_called_once()
            mock_log.assert_has_calls(
                        [call('Message contains 1 %s record', 'Summary')])

    def test_load_all_storage_type(self):
        """Check that load_records calls and logs with storage records.

        This checks that load_records is called and the message is logged
        correctly when the record type is storage."""
        logger = logging.getLogger('loader')
        pidfile = os.path.join(self.dir_path, 'pidfile')

        in_q = dirq.queue.Queue(os.path.join(self.dir_path, 'incoming'),
                                schema=schema)
        body = """<?xml version="1.0" ?>
        <sr:StorageUsageRecords
            xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">
            <sr:StorageUsageRecord>
            <sr:RecordIdentity sr:createTime="2019-08-06T06:46:11"
                        sr:recordId=" rad_tape_20190219T054505Z"/>
            <sr:StorageSystem>srm.grid.somewhere</sr:StorageSystem>
            <sr:Site>MATRIX</sr:Site><sr:StorageMedia>tape</sr:StorageMedia>
            <sr:SubjectIdentity><sr:Group>projects</sr:Group>
            <sr:GroupAttribute sr:attributeType="subgroup">rad</sr:GroupAttribute>
            </sr:SubjectIdentity>
            <sr:StartTime>2019-02-18T05:45:03Z</sr:StartTime>
            <sr:EndTime>2019-02-19T05:45:05Z</sr:EndTime>
            <sr:ResourceCapacityUsed>9127543637338</sr:ResourceCapacityUsed>
            </sr:StorageUsageRecord>
        </sr:StorageUsageRecords> """

        in_q.add({"body": body,
                  "signer": "test signer", "empaid": "", "error": ""})

        self.loader = apel.db.loader.Loader(self.dir_path, True, 'mysql',
                                            'host', 1234, 'db', 'user', 'pwd',
                                            pidfile)

        with mock.patch.object(logger, 'info') as mock_log:
            self.loader.load_all_msgs()
            self.mock_db.load_records.assert_called_once()
            mock_log.assert_has_calls(
                        [call('Message contains 1 %s record', 'Storage')])

    def tearDown(self):
        shutil.rmtree(self.dir_path)
        mock.patch.stopall()

if __name__ == '__main__':
    unittest.main()
