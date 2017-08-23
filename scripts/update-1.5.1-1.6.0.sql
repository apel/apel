-- This script is a single comment block that applies to
-- APEL Version 1.5.1, Cloud Database.

-- If you have a Cloud Database and wish to
-- upgrade to APEL Version 1.6.0, remove the block comment
-- symbols /* and */ and run this script
   
/*
-- Create / Update Tables

-- Update CloudRecords

-- Existing rows get set to the following:

-- CloudComputeServiceID - set afterwards
-- PublicIPCount - null (NULL)
-- BenchmarkType - empty VARCHAR ("")
-- Benchmark - decimal zero (0.00)

ALTER TABLE CloudRecords
  ADD CloudComputeServiceID INT NOT NULL AFTER SiteID,
  ADD PublicIPCount INT AFTER NetworkOutbound,
  ADD BenchmarkType VARCHAR(50) NOT NULL AFTER Disk,
  ADD Benchmark DECIMAL(10,3) NOT NULL AFTER BenchmarkType;


-- Update CloudSummaries

-- Existing rows get same values as for CloudRecords
-- PublicIPCount is not currently used in summaries

ALTER TABLE CloudSummaries
  ADD CloudComputeServiceID INT NOT NULL AFTER SiteID,
  ADD CpuCount INT AFTER CpuDuration,
  -- ADD PublicIPCount BIGINT AFTER NetworkOutbound,
  ADD BenchmarkType VARCHAR(50) NOT NULL AFTER Disk,
  ADD Benchmark DECIMAL(10,3) NOT NULL AFTER BenchmarkType;


-- Create CloudComputeServices lookup table
CREATE TABLE CloudComputeServices (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    INDEX(name)
);

-- Insert row for "None" which can be used as a default value
INSERT INTO CloudComputeServices (id, name) VALUES(1, "None");

-- Update the existing rows in the Cloud tables with a default value
UPDATE CloudRecords SET CloudComputeServiceID=1;

UPDATE CloudSummaries SET CloudComputeServiceID=1;


-- Create Views
-- View on CloudRecords
DROP VIEW IF EXISTS VCloudRecords;
CREATE VIEW VCloudRecords AS
    SELECT UpdateTime, VMUUID, site.name SiteName, cloudComputeService.name CloudComputeService, MachineName, 
           LocalUserId, LocalGroupId, userdn.name GlobalUserName, FQAN, vo.name VO, 
           vogroup.name VOGroup, vorole.name VORole,
           Status, StartTime, EndTime,
           SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, PublicIPCount, Memory, Disk, BenchmarkType, Benchmark, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, CloudComputeServices cloudComputeService, DNs userdn, VOs vo, VOGroups vogroup, VORoles vorole WHERE
        SiteID = site.id
        AND CloudComputeServiceID = cloudComputeService.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id
        AND VOGroupID = vogroup.id
        AND VORoleID = vorole.id;

-- View on CloudRecords
DROP VIEW IF EXISTS VAnonCloudRecords;
CREATE VIEW VAnonCloudRecords AS
    SELECT UpdateTime, VMUUID, site.name SiteName, cloudComputeService.name CloudComputeService,
           MachineName, LocalUserId, LocalGroupId, GlobalUserNameID, FQAN, vo.name VO,  Status, 
           StartTime, EndTime, SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, PublicIPCount, Memory, Disk, BenchmarkType, Benchmark,
           StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, CloudComputeServices cloudComputeService, DNs userdn, VOs vo WHERE
        SiteID = site.id
        AND CloudComputeServiceID = cloudComputeService.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id;

-- View on CloudSummaries
DROP VIEW IF EXISTS VCloudSummaries;
CREATE VIEW VCloudSummaries AS
    SELECT UpdateTime, site.name SiteName, cloudComputeService.name CloudComputeService, Month, Year,
           userdn.name GlobalUserName, vo.name VO, vogroup.name VOGroup, vorole.name VORole, Status,
           CloudType, ImageId, EarliestStartTime, LatestStartTime, WallDuration, CpuDuration,
           CpuCount, NetworkInbound, NetworkOutbound, Memory, Disk, BenchmarkType, Benchmark,  
           NumberOfVMs
    FROM CloudSummaries, Sites site, CloudComputeServices cloudComputeService, DNs userdn, VOs vo, VOGroups vogroup, VORoles vorole WHERE
        SiteID = site.id
        AND CloudComputeServiceID = cloudComputeService.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id
        AND VOGroupID = vogroup.id
        AND VORoleID = vorole.id;


-- Create / Replace Functions / Procedures
-- Create CloudComputeServiceLookup
DROP FUNCTION IF EXISTS CloudComputeServiceLookup;
DELIMITER //
CREATE FUNCTION CloudComputeServiceLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM CloudComputeServices WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO CloudComputeServices(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- Replace ReplaceCloudRecords
DROP PROCEDURE IF EXISTS ReplaceCloudRecord;
DELIMITER //
CREATE PROCEDURE ReplaceCloudRecord(
  VMUUID VARCHAR(255), site VARCHAR(255), cloudComputeService VARCHAR(255),
  machineName VARCHAR(255),
  localUserId VARCHAR(255),
  localGroupId VARCHAR(255), globalUserName VARCHAR(255), 
  fqan VARCHAR(255), vo VARCHAR(255),
  voGroup VARCHAR(255), voRole VARCHAR(255), status VARCHAR(255),
  startTime DATETIME, endTime DATETIME,
  suspendDuration INT,
  wallDuration INT, cpuDuration INT,
  cpuCount INT, networkType VARCHAR(255),  networkInbound INT,
  networkOutbound INT, publicIPCount INT, memory INT,
  disk INT, benchmarkType VARCHAR(50), benchmark DECIMAL(10,3), storageRecordId VARCHAR(255),
  imageId VARCHAR(255), cloudType VARCHAR(255),
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO CloudRecords(VMUUID, SiteID, CloudComputeServiceID, MachineName, LocalUserId, LocalGroupId,
        GlobalUserNameID, FQAN, VOID, VOGroupID, VORoleID, Status, StartTime, EndTime, SuspendDuration,
        WallDuration, CpuDuration, CpuCount, NetworkType, NetworkInbound, NetworkOutbound, PublicIPCount,
        Memory, Disk, BenchmarkType, Benchmark, StorageRecordId, ImageId, CloudType, PublisherDNID)
      VALUES (
        VMUUID, SiteLookup(site), CloudComputeServiceLookup(cloudComputeService), machineName,
        localUserId, localGroupId, DNLookup(globalUserName), fqan, VOLookup(vo), VOGroupLookup(voGroup),
        VORoleLookup(voRole), status, startTime, endTime, suspendDuration, 
        wallDuration, 
        cpuDuration, cpuCount, networkType, networkInbound, networkOutbound, publicIPCount, memory,
        disk, benchmarkType, benchmark, storageRecordId, imageId, cloudType, DNLookup(publisherDN)
        );
END //
DELIMITER ;

-- Replace ReplaceCloudSummaryRecords
DROP PROCEDURE IF EXISTS ReplaceCloudSummaryRecord;
DELIMITER //
CREATE PROCEDURE ReplaceCloudSummaryRecord(
  site VARCHAR(255), cloudComputeService VARCHAR(255), month INT, year INT, globalUserName VARCHAR(255), 
  vo VARCHAR(255), voGroup VARCHAR(255), voRole VARCHAR(255), status VARCHAR(255),
  cloudType VARCHAR(255), imageId VARCHAR(255), 
  earliestStartTime DATETIME, latestStartTime DATETIME, 
  wallDuration BIGINT, cpuDuration BIGINT, cpuCount INT,
  networkInbound BIGINT, networkOutbound BIGINT, memory BIGINT,
  disk BIGINT, benchmarkType VARCHAR(50), benchmark DECIMAL(10,3), numberOfVMs BIGINT,
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO CloudSummaries(SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID, VOID,
        VOGroupID, VORoleID, Status, CloudType, ImageId, EarliestStartTime, LatestStartTime, 
        WallDuration, CpuDuration, CpuCount, NetworkInbound, NetworkOutbound, Memory, Disk,
        BenchmarkType, Benchmark, NumberOfVMs,  PublisherDNID)
      VALUES (
        SiteLookup(site), CloudComputeServiceLookup(cloudComputeService), month, year,
        DNLookup(globalUserName), VOLookup(vo), VOGroupLookup(voGroup), VORoleLookup(voRole),
        status, cloudType, imageId, earliestStartTime, latestStartTime, wallDuration,
        cpuDuration, cpuCount, networkInbound, networkOutbound, memory, disk, benchmarkType,
        benchmark, numberOfVMs, DNLookup(publisherDN)
        );
END //
DELIMITER ;

-- Replace SummariesVMs
DROP PROCEDURE IF EXISTS SummariseVMs;
DELIMITER //
CREATE PROCEDURE SummariseVMs()
BEGIN
    REPLACE INTO CloudSummaries(SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID, VOID,
        VOGroupID, VORoleID, Status, CloudType, ImageId, EarliestStartTime, LatestStartTime,
        WallDuration, CpuDuration, CpuCount, NetworkInbound, NetworkOutbound, Memory, Disk,
        BenchmarkType, Benchmark, NumberOfVMs, PublisherDNID)
    SELECT SiteID,
        CloudComputeServiceID,
        MONTH(StartTime) AS Month, YEAR(StartTime) AS Year,
        GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId,
        MIN(StartTime),
        MAX(StartTime),
        SUM(WallDuration),
        SUM(CpuDuration),
        CpuCount,
        SUM(NetworkInbound),
        SUM(NetworkOutbound),
        SUM(Memory),
        SUM(Disk),
        BenchmarkType,
        Benchmark,
        COUNT(*),
        'summariser'
    FROM CloudRecords
    GROUP BY SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID, VOID, VOGroupID, VORoleID,
        Status, CloudType, ImageId, CpuCount, BenchmarkType, Benchmark
    ORDER BY NULL;
END //
DELIMITER ;
/*
