-- ------------------------------------------------------------------------------
-- CloudRecords

CREATE TABLE CloudRecords ( 
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 

  RecordCreateTime DATETIME NOT NULL,

  VMUUID VARCHAR(255) NOT NULL, 
  SiteID INT NOT NULL,                -- Foreign key
  CloudComputeServiceID INT NOT NULL, -- Foreign key

  MachineName VARCHAR(255), 

  LocalUserId VARCHAR(255),
  LocalGroupId VARCHAR(255),

  GlobalUserNameID INT NOT NULL,      -- Foreign key
  FQAN VARCHAR(255),
  VOID INT NOT NULL,                  -- Foreign key
  VOGroupID INT NOT NULL,             -- Foreign key
  VORoleID INT NOT NULL,              -- Foreign key

  Status VARCHAR(255),

  StartTime DATETIME, 
  EndTime DATETIME, 
  MeasurementTime DATETIME NOT NULL,
  MeasurementMonth INT NOT NULL,
  MeasurementYear INT NOT NULL,

  SuspendDuration INT, 
  WallDuration INT, 
  CpuDuration INT, 
  CpuCount INT, 

  NetworkType VARCHAR(255),
  NetworkInbound INT, 
  NetworkOutbound INT, 
  PublicIPCount INT,
  Memory INT, 
  Disk INT, 

  BenchmarkType VARCHAR(50) NOT NULL,
  Benchmark DECIMAL(10,3) NOT NULL,

  StorageRecordId VARCHAR(255),
  ImageId VARCHAR(255),
  CloudType VARCHAR(255),

  PublisherDNID INT NOT NULL,	    -- Foreign key

  -- Measurement(Month, Year) allows for usage to be assigned
  -- to accounting periods at load time
  PRIMARY KEY (VMUUID, MeasurementMonth, MeasurementYear),

  INDEX (UpdateTime),
  INDEX (GlobalUserNameID),
  INDEX (SiteID),
  INDEX (ImageID)

);


DROP PROCEDURE IF EXISTS ReplaceCloudRecord;
DELIMITER //
CREATE PROCEDURE ReplaceCloudRecord(
  recordCreateTime DATETIME,VMUUID VARCHAR(255), site VARCHAR(255), cloudComputeService VARCHAR(255),
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
    DECLARE suspendDurationNotNull INT;
    DECLARE cpuDurationNotNull INT;
    DECLARE wallDurationNotNull INT;
    DECLARE measurementTimeCalculated DATETIME;
    DECLARE recordCreateTimeNotNull DATETIME;

    IF(status='completed') THEN
        -- in this case, the recordCreateTime and measurementTime could
        -- be wildly different as the VM has ended.

        -- if we werent supplied a record create time
        -- for a completed VM we have decided to use the end time
        SET recordCreateTimeNotNull = IFNULL(recordCreateTime, endTime);

        -- Use the end time as the measurement time
        SET measurementTimeCalculated = endTime;
        
    ELSE
        -- In the case of a running VM, the measurement time will
        -- equal the record create time
        IF(recordCreateTime IS NOT NULL) THEN
            -- Use the supplied record create time as the measurement time
            SET measurementTimeCalculated = recordCreateTime;
            SET recordCreateTimeNotNull = recordCreateTime;
        ELSE
            -- Calculate the measurement time :(

            -- If the incoming suspendDuration is NULL, we can't compute a MeasurementTime
            -- so set a resonable value in that case
            -- DECLARE suspendDurationNotNull INT;
            SET suspendDurationNotNull = IFNULL(suspendDuration, 0);

            -- If the incoming wallDuartion is NULL we can't compute a MeasurementTime.
            -- Based off LRVMv1, we use cpuDurationNotNull, which from above is guaranteed
            -- to be a resonable value
            SET wallDurationNotNull = IFNULL(wallDuration,cpuDurationNotNull);

            -- Calculated the time of measurement so we can use it later to determine which
            -- accounting period this incoming record belongs too.
            SET measurementTimeCalculated = TIMESTAMPADD(SECOND, (suspendDurationNotNull + wallDurationNotNull), StartTime);
            -- We recieve and currently accept messages without a start time
            -- which causes the mesaurementTimeCalculated to be NULL
            -- which causes a loader reject on a previously accepted message
            -- so for now, set it to the zero time stamp as is what happens currently
            SET measurementTimeCalculated = IFNULL(measurementTimeCalculated, '00-00-00 00:00:00');
            SET recordCreateTimeNotNull = measurementTimeCalculated;

        END IF;
    END IF;

    INSERT INTO CloudRecords(RecordCreateTime, VMUUID, SiteID, CloudComputeServiceID, MachineName,
        LocalUserId, LocalGroupId, GlobalUserNameID, FQAN, VOID, VOGroupID,
        VORoleID, Status, StartTime, EndTime, MeasurementTime, MeasurementMonth,
        MeasurementYear, SuspendDuration, WallDuration, CpuDuration, CpuCount,
        NetworkType, NetworkInbound, NetworkOutbound, PublicIPCount, Memory, Disk,
        BenchmarkType, Benchmark, StorageRecordId, ImageId, CloudType, PublisherDNID)
      VALUES (
        recordCreateTimeNotNull, VMUUID, SiteLookup(site), CloudComputeServiceLookup(cloudComputeService), machineName,
        localUserId, localGroupId, DNLookup(globalUserName), fqan, VOLookup(vo), VOGroupLookup(voGroup),
        VORoleLookup(voRole), status, startTime, endTime, measurementTimeCalculated, Month(measurementTimeCalculated), Year(measurementTimeCalculated),
        suspendDurationNotNull, wallDurationNotNull, cpuDurationNotNull, cpuCount,
        networkType, networkInbound, networkOutbound, publicIPCount, memory, disk,
        benchmarkType, benchmark, storageRecordId, imageId, cloudType, DNLookup(publisherDN))
      ON DUPLICATE KEY UPDATE
        -- Then the incoming record belong in a accounting period which we
        -- already have some data (for this VM/Site)
        -- If the incoming measurementTime is greater than the currently stored one
        -- update all columns with the new values.
        -- It's possible these updates do not occur in an "all or nothing" fashion
        -- as per https://thewebfellas.com/blog/conditional-duplicate-key-updates-with-mysql
        -- so measurementTime is the last thing to be updated.
        -- There is no nicer way to do the 'ON DUPLICATE KEY UPDATE'
        -- other than field by field, and we can't get around making the greater than
        -- comparison everytime as we can only reference the current value in the
        -- 'ON DUPLICATE KEY UPDATE' block
        CloudRecords.RecordCreateTime = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, recordCreateTimeNotNull, CloudRecords.RecordCreateTime),
        CloudRecords.SiteID = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, SiteLookup(site), CloudRecords.SiteID),
        CloudRecords.CloudComputeServiceID = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, CloudComputeServiceLookup(cloudComputeService), CloudRecords.CloudComputeServiceID),
        CloudRecords.MachineName = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, machineName, CloudRecords.MachineName),
        CloudRecords.LocalUserId = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, localUserId, CloudRecords.LocalUserId),
        CloudRecords.LocalGroupId = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, localGroupId, CloudRecords.LocalGroupId),
        CloudRecords.GlobalUserNameID = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, DNLookup(globalUserName), CloudRecords.GlobalUserNameID),
        CloudRecords.FQAN = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, fqan, CloudRecords.FQAN),
        CloudRecords.VOID = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, VOLookup(vo), CloudRecords.VOID),
        CloudRecords.VOGroupID = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, VOGroupLookup(voGroup), CloudRecords.VOGroupID),
        CloudRecords.VORoleID = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, VORoleLookup(voRole), CloudRecords.VORoleID),
        CloudRecords.Status = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, status, CloudRecords.Status),
        CloudRecords.StartTime = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, startTime, CloudRecords.StartTime),
        CloudRecords.EndTime = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, endTime, CloudRecords.EndTime),
        CloudRecords.SuspendDuration = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, suspendDurationNotNull, CloudRecords.SuspendDuration),
        CloudRecords.WallDuration = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, wallDurationNotNull, CloudRecords.WallDuration),
        CloudRecords.CpuDuration = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, cpuDurationNotNull, CloudRecords.CpuDuration),
        CloudRecords.CpuCount = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, cpuCount, CloudRecords.CpuCount),
        CloudRecords.NetworkType = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, networkType, CloudRecords.NetworkType),
        CloudRecords.NetworkInbound = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, networkInbound, CloudRecords.NetworkInbound),
        CloudRecords.NetworkOutbound = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, networkOutbound, CloudRecords.NetworkOutbound),
        CloudRecords.PublicIPCount = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, publicIPCount, CloudRecords.PublicIPCount),
        CloudRecords.Memory = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, memory, CloudRecords.Memory),
        CloudRecords.Disk = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, disk, CloudRecords.Disk),
        CloudRecords.BenchmarkType = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, benchmarkType, CloudRecords.BenchmarkType),
        CloudRecords.Benchmark = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, Benchmark, CloudRecords.Benchmark),
        CloudRecords.StorageRecordId = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, storageRecordId, CloudRecords.StorageRecordId),
        CloudRecords.ImageId = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, imageId, CloudRecords.ImageId),
        CloudRecords.CloudType = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, cloudType, CloudRecords.CloudType),
        CloudRecords.PublisherDNID = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, DNLookup(publisherDN), CloudRecords.PublisherDNID),

        CloudRecords.MeasurementMonth = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, Month(measurementTimeCalculated), CloudRecords.MeasurementMonth),
        CloudRecords.MeasurementYear = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, Year(measurementTimeCalculated), CloudRecords.MeasurementYear),

        CloudRecords.MeasurementTime = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, measurementTimeCalculated, CloudRecords.MeasurementTime)
    ;
END //
DELIMITER ;


-- ------------------------------------------------------------------------------
-- CloudSummaries

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
    VOID, VOGroupID, VORoleID, Status, CloudType, ImageId, CpuCount,
    BenchmarkType, Benchmark)

);

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
    REPLACE INTO CloudSummaries(SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId, EarliestStartTime, LatestStartTime, 
        WallDuration, CpuDuration, CpuCount, NetworkInbound, NetworkOutbound, Memory, Disk, BenchmarkType, Benchmark, NumberOfVMs,  PublisherDNID)
      VALUES (
        SiteLookup(site), CloudComputeServiceLookup(cloudComputeService), month, year, DNLookup(globalUserName), VOLookup(vo),
        VOGroupLookup(voGroup), VORoleLookup(voRole), status, cloudType, imageId, earliestStartTime, latestStartTime, 
        wallDuration, cpuDuration, cpuCount, networkInbound, networkOutbound, memory,
        disk, benchmarkType, benchmark, numberOfVMs, DNLookup(publisherDN)
        );
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS SummariseVMs;
DELIMITER //
CREATE PROCEDURE SummariseVMs()
BEGIN

  -- Based on discussion here:
  -- http://stackoverflow.com/questions/13196190/mysql-subtracting-value-from-previous-row-group-by
  CREATE TEMPORARY TABLE TVMUsagePerMonth
    (INDEX index_VMUsagePerMonth USING BTREE (VMUUID, Month, Year))
    SELECT
      ThisRecord.RecordCreateTime as RecordCreateTime,
      ThisRecord.VMUUID as VMUUID,
      ThisRecord.SiteID as SiteID,
      ThisRecord.CloudComputeServiceID as CloudComputeServiceID,
      ThisRecord.MeasurementMonth as Month,
      ThisRecord.MeasurementYear as Year,
      ThisRecord.GlobalUserNameID as GlobalUserNameID,
      ThisRecord.VOID as VOID,
      ThisRecord.VOGroupID as VOGroupID,
      ThisRecord.VORoleID as VORoleID,
      ThisRecord.Status as Status,
      ThisRecord.CloudType as CloudType,
      ThisRecord.ImageId as ImageId,
      ThisRecord.StartTime as StartTime,
      COALESCE(ThisRecord.WallDuration - IFNULL(PrevRecord.WallDuration, 0)) AS ComputedWallDuration,
      COALESCE(ThisRecord.CpuDuration - IFNULL(PrevRecord.CpuDuration, 0)) AS ComputedCpuDuration,
      ThisRecord.CpuCount as CpuCount,
      COALESCE(ThisRecord.NetworkInbound - IFNULL(PrevRecord.NetworkInbound, 0)) AS ComputedNetworkInbound,
      COALESCE(ThisRecord.NetworkOutbound - IFNULL(PrevRecord.NetworkOutbound, 0)) AS ComputedNetworkOutbound,
      -- Will Memory change during the course of the VM lifetime? If so, do we report a maximum, or
      -- average, or something else?
      -- If it doesn't change:
      ThisRecord.Memory,
      ThisRecord.Disk, -- As above: constant or changing?
      ThisRecord.BenchmarkType as BenchmarkType,
      ThisRecord.Benchmark as Benchmark

    FROM CloudRecords as ThisRecord
    LEFT JOIN CloudRecords as PrevRecord
    ON (ThisRecord.VMUUID = PrevRecord.VMUUID and
	PrevRecord.MeasurementTime = (SELECT max(MeasurementTime)
                                      FROM CloudRecords
                                      WHERE VMUUID = ThisRecord.VMUUID
                                      AND MeasurementTime < ThisRecord.MeasurementTime)
);

    REPLACE INTO CloudSummaries(SiteID, CloudComputeServiceID, Month, Year,
        GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId,
        EarliestStartTime, LatestStartTime, WallDuration, CpuDuration, CpuCount,
        NetworkInbound, NetworkOutbound, Memory, Disk,
        BenchmarkType, Benchmark, NumberOfVMs, PublisherDNID)
    SELECT SiteID,
      CloudComputeServiceID,
      Month, Year,
      GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId,
      MIN(StartTime),
      MAX(StartTime),
      SUM(ComputedWallDuration),
      SUM(ComputedCpuDuration),
      CpuCount,
      SUM(ComputedNetworkInbound),
      SUM(ComputedNetworkOutbound), 
      SUM(Memory),
      SUM(Disk),
      BenchmarkType,
      Benchmark,
      COUNT(*),
      'summariser'
      FROM TVMUsagePerMonth
      GROUP BY SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID, VOID,
          VOGroupID, VORoleID, Status, CloudType, ImageId, CpuCount,
          BenchmarkType, Benchmark
      ORDER BY NULL;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- LastUpdated
DROP TABLE IF EXISTS LastUpdated;
CREATE TABLE LastUpdated (
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  Type VARCHAR(255) PRIMARY KEY
);

DROP PROCEDURE IF EXISTS UpdateTimestamp;
DELIMITER //
CREATE PROCEDURE UpdateTimestamp(type VARCHAR(255)) 
  BEGIN
   REPLACE INTO LastUpdated (Type) VALUES (type);
  END //

DELIMITER ;    


-- -----------------------------------------------------------------------------
-- Sites
DROP TABLE IF EXISTS Sites;
CREATE TABLE Sites (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
 ,  name VARCHAR(255) NOT NULL

 , INDEX(name)

) ;

DROP FUNCTION IF EXISTS SiteLookup;
DELIMITER //
CREATE FUNCTION SiteLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM Sites WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO Sites(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;


-- -----------------------------------------------------------------------------
-- CloudComputeService
DROP TABLE IF EXISTS CloudComputeServices;
CREATE TABLE CloudComputeServices (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
 ,  name VARCHAR(255) NOT NULL

 , INDEX(name)

) ;

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


-- -----------------------------------------------------------------------------
-- DNs
DROP TABLE IF EXISTS DNs;
CREATE TABLE DNs (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
 ,  name VARCHAR(255) NOT NULL

 ,  INDEX(name)

) ;

DROP FUNCTION IF EXISTS DNLookup;
DELIMITER //
CREATE FUNCTION DNLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM DNs WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO DNs(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- VOs
DROP TABLE IF EXISTS VOs;
CREATE TABLE VOs (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
    
  INDEX(name)
) ;


DROP FUNCTION IF EXISTS VOLookup;
DELIMITER //
CREATE FUNCTION VOLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM VOs WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO VOs(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;


-- -----------------------------------------------------------------------------
-- VORoles
DROP TABLE IF EXISTS VORoles;
CREATE TABLE VORoles (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
    
  INDEX(name)
) ;


DROP FUNCTION IF EXISTS VORoleLookup;
DELIMITER //
CREATE FUNCTION VORoleLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM VORoles WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO VORoles(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;


-- -----------------------------------------------------------------------------
-- VOGroups
DROP TABLE IF EXISTS VOGroups;
CREATE TABLE VOGroups (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  
  INDEX(name)
) ;


DROP FUNCTION IF EXISTS VOGroupLookup;
DELIMITER //
CREATE FUNCTION VOGroupLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM VOGroups WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO VOGroups(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- View on CloudRecords
CREATE VIEW VCloudRecords AS
    SELECT UpdateTime, RecordCreateTime, VMUUID, site.name SiteName, cloudComputeService.name CloudComputeService, MachineName, 
           LocalUserId, LocalGroupId, userdn.name GlobalUserName, FQAN, vo.name VO, 
           vogroup.name VOGroup, vorole.name VORole,
           Status, StartTime, EndTime, MeasurementTime, MeasurementMonth, MeasurementYear,
           SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, PublicIPCount, Memory, Disk, BenchmarkType, Benchmark, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, CloudComputeServices cloudComputeService, DNs userdn, VOs vo, VOGroups vogroup, VORoles vorole WHERE
        SiteID = site.id
        AND CloudComputeServiceID = cloudComputeService.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id
        AND VOGroupID = vogroup.id
        AND VORoleID = vorole.id;

-- -----------------------------------------------------------------------------
-- View on CloudRecords
CREATE VIEW VAnonCloudRecords AS
    SELECT UpdateTime, VMUUID, site.name SiteName, cloudComputeService.name CloudComputeService, MachineName,
           LocalUserId, LocalGroupId, GlobalUserNameID, FQAN, vo.name VO,  Status, StartTime, EndTime,
           SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, PublicIPCount, Memory, Disk, BenchmarkType, Benchmark, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, CloudComputeServices cloudComputeService, DNs userdn, VOs vo WHERE
        SiteID = site.id
        AND CloudComputeServiceID = cloudComputeService.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id;
        
-- -----------------------------------------------------------------------------
-- View on CloudSummaries
CREATE VIEW VCloudSummaries AS
    SELECT UpdateTime, site.name SiteName, cloudComputeService.name CloudComputeService, Month, Year,
           userdn.name GlobalUserName, vo.name VO, 
           vogroup.name VOGroup, vorole.name VORole,
           Status, CloudType, ImageId, EarliestStartTime, LatestStartTime,
           WallDuration, CpuDuration, CpuCount, NetworkInbound, NetworkOutbound, Memory, Disk, BenchmarkType, Benchmark,  
           NumberOfVMs
    FROM CloudSummaries, Sites site, CloudComputeServices cloudComputeService, DNs userdn, VOs vo, VOGroups vogroup, VORoles vorole WHERE
        SiteID = site.id
        AND CloudComputeServiceID = cloudComputeService.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id
        AND VOGroupID = vogroup.id
        AND VORoleID = vorole.id;

