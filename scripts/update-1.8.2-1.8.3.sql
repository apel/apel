-- This script contains multiple comment blocks that can update
-- APEL version 1.6.2 databases of the following types to 1.7.0:
--  - Cloud Accounting Database

-- UPDATE SCRIPT FOR CLOUD SCHEMA

-- If you have a Cloud Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This section will:
-- - Add new database fields for RecordCreateTime
--   and MeasurementTime (where MeasurementTime is an approximation
--   of the actual record's create time) to allow for proper
--   accounting of long running VMs
-- - Updates the view on the CloudRecords table showing the new fields
-- - Defines a new ReplaceCloudRecord and SummariseVMs
--   procedure for the same purpose
-- - Updates the view on the CloudRecords table showing the new fields

-- Set the schema version identifier. See also server.sql file
-- [It would be cleaner if this could be SOURCEed from server.sql
--  or a shared file.]
SET @schema_version = '1.9.1';

CREATE TABLE SchemaVersionHistory (
  VersionNumber VARCHAR(8) NOT NULL PRIMARY KEY,
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO SchemaVersionHistory (VersionNumber) VALUES (@schema_version);
