-- This script contains multiple comment blocks that can update
-- APEL version x.x.x databases of the following types to x.x.x:
--  - Cloud Accounting Database

/*
-- UPDATE SCRIPT FOR CLOUD SUMMARY SCHEMA

-- If you have a Cloud Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This section will:
-- - Remove CloudType from the CloudSummaries primary key. This
--   ensures new summaries overwrite old summaries after updates
--   to CASO version name.

ALTER TABLE CloudSummaries 
  DROP PRIMARY KEY,
  ADD PRIMARY KEY (
    SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID,
    VOID, VOGroupID, VORoleID, Status, ImageId, CpuCount,
    BenchmarkType, Benchmark
  );

*/

