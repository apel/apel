-- This script contains multiple comment blocks that can update
-- APEL version 1.6.1 databases of the following types to the next version:
--  - Cloud Accounting Database

-- UPDATE SCRIPT FOR CLOUD SCHEMA

-- If you have a Cloud Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This section will:
-- - Change records with a NULL CpuCount so that they have a CpuCount of 0,
--   to prevent problems at summarising time.

UPDATE CloudRecords SET
    CpuCount=0
    WHERE CpuCount is NULL;

