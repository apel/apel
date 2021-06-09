-- This schema adds the tables necessary for GPU accounting as a
-- separate record as part of the wider Cloud Accounting system.

use clientdb

DROP TABLE IF EXISTS GPURecords;
CREATE TABLE GPURecords (
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  MeasurementTime DATETIME NOT NULL,
  MeasurementMonth INT NOT NULL,
  MeasurementYear INT NOT NULL,

  AssociatedRecordType VARCHAR(255) NOT NULL,
  AssociatedRecord VARCHAR(255) NOT NULL, -- [?] Becomes VMUUID for "Cloud" record type

  -- LocalUserId VARCHAR(255) NOT NULL,   -- [ ] Struck out in document
  -- LocalGroupId VARCHAR(255) NOT NULL,

                                    -- [?] Uncertainty on exactly how to apply.
  GlobalUserName VARCHAR(255),      -- [?] GlobalUserNameID, Foreign key? **
  FQAN VARCHAR(255) NOT NULL,       -- [?] ** See definition of associated record type
  SiteName VARCHAR(255) NOT NULL,   -- [?] ** See definition of associated record type
  Count DECIMAL NOT NULL,
  Cores INT,
  ActiveDuration INT,
  AvailableDuration INT,
  BenchmarkType VARCHAR(255),       -- [?] VARCHAR(50)
  Benchmark DECIMAL,                -- [?] DECIMAL(10,3)
  Type VARCHAR(255) NOT NULL,       -- [?] Accelerator Type, GPU, FPGA, MIC
  Model VARCHAR(255),               -- [?] Accelerator Model
  PublisherDNID INT NOT NULL,       -- [?] Foreign key

  -- PRIMARY KEY (),                -- [?] VMUUID, MeasurementMonth, MeasurementYear

  INDEX (UpdateTime),
  INDEX (GlobalUserName),
  INDEX (SiteName)

);

DROP PROCEDURE IF EXISTS ReplaceGPURecord;
DELIMITER //
CREATE PROCEDURE ReplaceGPURecord(
  measurementTime DATETIME,
  measurementMonth INT,
  measurementYear INT,
  associatedRecordType VARCHAR(255),
  associatedRecord VARCHAR(255),
  globalUserName VARCHAR(255),
  fqan VARCHAR(255),
  siteName VARCHAR(255),
  count INT,
  cores INT,
  activeDuration INT,
  availableDuration INT,
  benchmarkType VARCHAR(255),
  benchmark DECIMAL,
  type VARCHAR(255),
  model VARCHAR(255),
  publisherDN VARCHAR(255)
)
BEGIN
REPLACE INTO GPURecords(
  MeasurementTime,
  MeasurementMonth,
  MeasurementYear,
  AssociatedRecordType,
  AssociatedRecord,
  GlobalUserName,
  FQAN,
  SiteName,
  Count,
  Cores,
  ActiveDuration,
  AvailableDuration,
  BenchmarkType,
  Benchmark,
  Type,
  Model,
  PublisherDNID
)
VALUES(
  measurementTime,
  measurementMonth,
  measurementYear,
  associatedRecordType,
  associatedRecord,
  globalUserName,               -- [?] DNLookup(globalUserName) -> GlobalUsernameID
  fqan,
  siteName,
  count,
  cores,
  activeDuration,
  availableDuration,
  benchmarkType,
  benchmark,
  type,
  model,
  DNLookup(publisherDN)
);
END //
DELIMITER ;
