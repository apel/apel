-- This schema adds the tables necessary for GPU accounting as a
-- separate record as part of the wider Cloud Accounting system.

use clientdb

DROP TABLE IF EXISTS GPURecords;
CREATE TABLE GPURecords (
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  MeasurementMonth INT NOT NULL,
  MeasurementYear INT NOT NULL,

  AssociatedRecordType VARCHAR(255) NOT NULL,
  AssociatedRecord VARCHAR(255) NOT NULL,

  GlobalUserName VARCHAR(255),      
  FQAN VARCHAR(255) NOT NULL,       
  SiteName VARCHAR(255) NOT NULL,   
  Count DECIMAL(10,3) NOT NULL,
  Cores INT,
  ActiveDuration INT,
  AvailableDuration INT,
  BenchmarkType VARCHAR(255),       
  Benchmark DECIMAL(10,3),                
  Type VARCHAR(255) NOT NULL,       
  Model VARCHAR(255),               
  PublisherDNID INT NOT NULL,

  PRIMARY KEY (AssociatedRecord, MeasurementMonth, MeasurementYear)   

  -- INDEX (UpdateTime),
  -- INDEX (GlobalUserName),
  -- INDEX (SiteName)

);

DROP PROCEDURE IF EXISTS ReplaceGPURecord;
DELIMITER //
CREATE PROCEDURE ReplaceGPURecord(
  measurementMonth INT,
  measurementYear INT,
  associatedRecordType VARCHAR(255),
  associatedRecord VARCHAR(255),
  globalUserName VARCHAR(255),
  fqan VARCHAR(255),
  siteName VARCHAR(255),
  count DECIMAL(10,3),
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
  measurementMonth,
  measurementYear,
  associatedRecordType,
  associatedRecord,
  globalUserName,
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

-- -- Sum GPU time by month
-- --
-- -- [?] Care about latest record, or assume that all records 
-- --     in the month are unique?
-- -- 
-- -- select
-- -- siteName, globalUserName, associatedRecordType, 
-- -- [?] associatedRecord?, measurementMonth, measurementYear,
-- -- count, cores, benchmarkType, benchmark, type, model
-- -- sum(activeduration)
-- -- sum(availableduration)
-- -- count(*)
-- 
-- -- Group by
-- -- sitename, globalusername, associatedrecordtype, month, year, 
-- -- count, cores, type, model, benchmark, benchmarktype
-- 
--DROP TABLE IF EXISTS GPUSummaries;
--CREATE TABLE GPUSummaries (
--    Month INT NOT NULL, 
--    Year INT NOT NULL,
--    AssociatedRecordType VARCHAR(255) NOT NULL,
--    GlobalUserName VARCHAR(255), 
--    SiteName VARCHAR(255) NOT NULL, 
--    -- [?] FQAN VARCHAR(255) NOT NULL,
--    Count DECIMAL(10,3) NOT NULL,
--    Cores INT,
--    AvailableDuration INT NOT NULL,
--    ActiveDuration INT,
--    BenchmarkType VARCHAR(255),
--    Benchmark DECIMAL(10,3),
--    Type VARCHAR(255) NOT NULL,
--    Model VARCHAR(255),
--    NumberOfRecords INT NOT NULL,
--    PublisherDN VARCHAR(255) NOT NULL
--    PRIMARY KEY (Month, Year, GlobalUserName, 
--                AssociatedRecordType, SiteName, 
--                Count, Cores)
--                -- BenchmarkType, Benchmark)
--);
--
--
--DROP PROCEDURE IF EXISTS SummariseGPUs;
--DELIMITER //
--CREATE PROCEDURE SummariseGPUs()
--
--BEGIN
--    REPLACE INTO GPUSummaries(Month, Year, AssociatedRecordType,
--        GlobalUserName, SiteName, 
--        -- [?] FQAN,
--        Cores, Count, Type, Model, AvailableDuration, ActiveDuration, 
--        BenchmarkType, Benchmark, NumberOfRecords, PublisherDN)
--    SELECT 
--      MeasurementMonth, MeasurementYear,
--      AssociatedRecordType,
--      GlobalUserName,
--      SiteName,
--      Count,
--      Cores,
--      SUM(AvailableDuration),
--      SUM(ActiveDuration),
--      BenchmarkType,
--      -- Benchmark,    -- [?] Potentially mismatching Benchmark values
--      AVG(Benchmark),
--      Type,
--      Model,
--      COUNT(*),
--      'summariser'
--      FROM GPURecords
--      GROUP BY 
--          MeasurementMonth, MeasurementYear, 
--          AssociatedRecordType,
--          GlobalUserNameID, SiteName, 
--          Count, Cores, Type, Model,
--          BenchmarkType, Benchmark
--      ORDER BY NULL; -- [?]
--END //
--DELIMITER ;
--