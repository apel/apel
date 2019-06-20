"""This file contains tests expected behaviour around republishing."""

import datetime
import os
from subprocess import call, Popen, PIPE
import unittest

import apel.db.apeldb
import apel.db.loader.record_factory
import apel.db.records


class TestRepublish(unittest.TestCase):
    """This class contains tests for expected behaviour around republishing."""

    def setUp(self):
        """Set up a database and load schema files."""

        # Set up a database.
        query = ("DROP DATABASE IF EXISTS apel_unittest;"
                 "CREATE DATABASE apel_unittest;")

        call(["mysql", "-u", "root", "-e", query])

        # Build a list of schema files for later loading.
        # For now, only add the cloud schema file.
        schema_path_list = []
        schema_path_list.append(
            os.path.abspath(
                os.path.join("..", "schemas", "cloud.sql")
            )
        )

        # Load each schema in turn.
        for schema_path in schema_path_list:
            with open(schema_path) as schema_file:
                call(
                    ["mysql", "-u", "root", "apel_unittest"],
                    stdin=schema_file
                )

    def test_cloud_republish(self):
        """Test the newest cloud record per month/VM is the one saved."""
        database = apel.db.apeldb.ApelDb(
            "mysql", "localhost", 3306, "root", "", "apel_unittest"
        )

        # The following StartTimes and WallDurations have been crafted so that
        # the two records (record1 and record2) generated produce
        # MeasurementTimes in the database of same month. The second
        # WallDuration has been crafted to be less than the first, to test the
        # case of a republish reducing the usage reported.
        vm_start_time = 1559818218
        first_wall_duration = 1582
        second_wall_duration = 158

        record1 = apel.db.records.cloud.CloudRecord()
        record1._record_content = {
            "VMUUID": "1559818218-Site1-VM12345",
            "SiteName": "Site1",
            "Status": "started",
            "StartTime": datetime.datetime.fromtimestamp(vm_start_time),
            "WallDuration": first_wall_duration,
        }

        record2 = apel.db.records.cloud.CloudRecord()
        record2._record_content = {
            "VMUUID": "1559818218-Site1-VM12345",
            "SiteName": "Site1",
            "Status": "started",
            "StartTime": datetime.datetime.fromtimestamp(vm_start_time),
            "WallDuration": second_wall_duration,
        }

        record_list = [record1]
        database.load_records(record_list, source="testDN")

        record_list = [record2]
        database.load_records(record_list, source="testDN")

        # Expected result based on the records above is a MeasurementTime equal
        # to the StartTime plus the WallDuration reported in the second record.
        expected_measurement_time = datetime.datetime.fromtimestamp(
            vm_start_time + second_wall_duration
        )

        # Now check the database to see which record has been saved.
        query = ("SELECT MeasurementTime FROM VCloudRecords;")
        mysql_process = Popen(
            ["mysql", "-N", "-u", "root", "apel_unittest", "-e", query],
            stdin=PIPE, stdout=PIPE, stderr=PIPE
        )
        mysql_process.wait()

        # Extract the actual result from the MySQL query.
        saved_measurement_time = datetime.datetime.strptime(
            mysql_process.communicate()[0], "%Y-%m-%d %H:%M:%S\n"
        )

        self.assertEqual(saved_measurement_time, expected_measurement_time)


if __name__ == "__main__":
    unittest.main()
