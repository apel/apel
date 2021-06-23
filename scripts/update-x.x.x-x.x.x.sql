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

DROP TABLE IF EXISTS CloudSummaries;
CREATE TABLE CloudSummaries (
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  SiteID INT NOT NULL, -- Foreign key
  CloudComputeServiceID INT NOT NULL, -- Foreign key

  Month INT NOT NULL,
  Year INT NOT NULL,

  GlobalUserNameID INT NOT NULL, -- Foreign key
  VOID INT NOT NULL, -- Foreign key
  VOGroupID INT NOT NULL, -- Foreign key
  VORoleID INT NOT NULL, -- Foreign key

  Status VARCHAR(255) NOT NULL,
  CloudType VARCHAR(255) NOT NULL,
  ImageId VARCHAR(255) NOT NULL,

  EarliestStartTime DATETIME,
  LatestStartTime DATETIME,
  WallDuration BIGINT,
  CpuDuration BIGINT,
  CpuCount INT NOT NULL,

  NetworkInbound BIGINT,
  NetworkOutbound BIGINT,
  -- PublicIPCount BIGINT,
  Memory BIGINT,
  Disk BIGINT,

  BenchmarkType VARCHAR(50) NOT NULL,
  Benchmark DECIMAL(10,3) NOT NULL,

  NumberOfVMs INT,

  PublisherDNID VARCHAR(255),

  PRIMARY KEY (SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID,
    VOID, VOGroupID, VORoleID, Status, ImageId, CpuCount,
    BenchmarkType, Benchmark)

);

*/
