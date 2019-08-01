-- This script contains multiple comment blocks that can update
-- APEL version 1.5.1 databases of the following types to 1.6.0:
--  - Cloud Accounting Database
--  - Storage Accounting Database

-- To update, find the relevent comment block below and remove
-- its block comment symbols /* and */ then run this script.



/*
-- UPDATE SCRIPT FOR CLOUD SCHEMA

-- If you have a Cloud Accounting Database and wish to
-- upgrade to APEL Version 1.6.0, remove the block comment
-- symbols around this section and then run this script.

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
*/


/*
-- UPDATE SCRIPT FOR STORAGE SCHEMA

-- If you have a Storage Accounting Database and wish to
-- upgrade to APEL version 1.6.0, remove the block comment
-- symbols around this section and then run this script.

-- This script adds tables SubGroups and Roles, and two matching Lookup tables.
-- It then adds defualt values to first two tables, expands the StarRecords
-- table with two matching ID columns, then sets those to default values. Lastly
-- the ReplaceStarRecord is updated to include the new fields.


DROP TABLE IF EXISTS SubGroups;
CREATE TABLE SubGroups (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  INDEX (name)
);

DROP FUNCTION IF EXISTS SubGroupLookup;
DELIMITER //
CREATE FUNCTION SubGroupLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
  DECLARE result INTEGER;
  SELECT id FROM SubGroups WHERE name=lookup INTO result;
  IF result IS NULL THEN
    INSERT INTO SubGroups(name) VALUES (lookup);
    SET result=LAST_INSERT_ID();
  END IF;
RETURN result;
END //
DELIMITER ;


DROP TABLE IF EXISTS Roles;
CREATE TABLE Roles (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  INDEX (name)
);

DROP FUNCTION IF EXISTS RoleLookup;
DELIMITER //
CREATE FUNCTION RoleLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
  DECLARE result INTEGER;
  SELECT id FROM Roles WHERE name=lookup INTO result;
  IF result IS NULL THEN
    INSERT INTO Roles(name) VALUES (lookup);
    SET result=LAST_INSERT_ID();
  END IF;
RETURN result;
END //
DELIMITER ;


INSERT INTO SubGroups VALUES(1,'None');
INSERT INTO Roles VALUES(1,'None');


ALTER TABLE StarRecords
  ADD COLUMN SubGroupID INT NOT NULL AFTER GroupID,
  ADD COLUMN RoleID INT NOT NULL AFTER SubGroupID;

Update StarRecords SET SubGroupID=1;
Update StarRecords SET RoleID=1;


DROP PROCEDURE IF EXISTS ReplaceStarRecord;
DELIMITER //
CREATE PROCEDURE ReplaceStarRecord(
  recordId                  VARCHAR(255),
  createTime                DATETIME,
  storageSystem             VARCHAR(255),
  site                      VARCHAR(255),
  storageShare              VARCHAR(255),
  storageMedia              VARCHAR(255),
  storageClass              VARCHAR(255),
  fileCount                 INTEGER,
  directoryPath             VARCHAR(255),
  localUser                 VARCHAR(255),
  localGroup                VARCHAR(255),
  userIdentity              VARCHAR(255),
  groupName                 VARCHAR(255),
  subGroupName              VARCHAR(255),
  roleName                  VARCHAR(255),
  startTime                 DATETIME,
  endTime                   DATETIME,
  resourceCapacityUsed      BIGINT,
  logicalCapacityUsed       BIGINT,
  resourceCapacityAllocated BIGINT
)
BEGIN
  REPLACE INTO StarRecords(
    RecordId,
    CreateTime,
    StorageSystemID,
    SiteID,
    StorageShareID,
    StorageMediaID,
    StorageClassID,
    FileCount,
    DirectoryPath,
    LocalUser,
    LocalGroup,
    UserIdentityID,
    GroupID,
    SubGroupID,
    RoleID,
    StartTime,
    EndTime,
    ResourceCapacityUsed,
    LogicalCapacityUsed,
    ResourceCapacityAllocated)
  VALUES (
    recordId,
    createTime,
    StorageSystemLookup(storageSystem),
    SiteLookup(site),
    StorageShareLookup(storageShare),
    StorageMediaLookup(storageMedia),
    StorageClassLookup(storageClass),
    fileCount,
    directoryPath,
    localUser,
    localGroup,
    UserIdentityLookup(userIdentity),
    GroupLookup(groupName),
    SubGroupLookup(subGroupName),
    RoleLookup(roleName),
    startTime,
    endTime,
    resourceCapacityUsed,
    logicalCapacityUsed,
    resourceCapacityAllocated
);
END //
DELIMITER ;
*/
