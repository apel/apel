-- ------------------------------------------------------------------------------
-- CloudRecords

CREATE TABLE CloudRecords ( 
  UpdateTime TIMESTAMP, 

  VMUUID VARCHAR(255) NOT NULL, 
  SiteID INT NOT NULL,                -- Foreign key

  MachineName VARCHAR(255), 

  LocalUserId VARCHAR(255),
  LocalGroupId VARCHAR(255),

  GlobalUserNameID INT NOT NULL,      -- Foreign key
  FQAN VARCHAR(255),
  VOID INT NOT NULL,                  -- Foreign key
  VOGroupID INT NOT NULL,             -- Foreign key
  VORoleID INT NOT NULL,              -- Foreign key

  Status VARCHAR(255),

  StartTime DATETIME NOT NULL, 
  EndTime DATETIME, 
  SuspendDuration INT NOT NULL, 

  WallDuration INT NOT NULL, 
  CpuDuration INT, 
  CpuCount INT, 

  NetworkType VARCHAR(255),
  NetworkInbound INT, 
  NetworkOutbound INT, 
  Memory INT, 
  Disk INT, 

  StorageRecordId VARCHAR(255),
  ImageId VARCHAR(255),
  CloudType VARCHAR(255),

  PublisherDNID INT NOT NULL,	    -- Foreign key

  PRIMARY KEY (VMUUID, StartTime, SuspendDuration, WallDuration),

  INDEX (UpdateTime),
  INDEX (GlobalUserNameID),
  INDEX (SiteID),
  INDEX (ImageID)

);


DROP PROCEDURE IF EXISTS ReplaceCloudRecord;
DELIMITER //
CREATE PROCEDURE ReplaceCloudRecord(
  VMUUID VARCHAR(255), site VARCHAR(255), 
  machineName VARCHAR(255), 
  localUserId VARCHAR(255),
  localGroupId VARCHAR(255), globalUserName VARCHAR(255), 
  fqan VARCHAR(255), vo VARCHAR(255), 
  voGroup VARCHAR(255), voRole VARCHAR(255), status VARCHAR(255),
  startTime DATETIME, endTime DATETIME, 
  suspendDuration INT,
  wallDuration INT, cpuDuration INT, 
  cpuCount INT, networkType VARCHAR(255),  networkInbound INT, 
  networkOutbound INT, memory INT, 
  disk INT, storageRecordId VARCHAR(255),
  imageId VARCHAR(255), cloudType VARCHAR(255),
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO CloudRecords(VMUUID, SiteID, MachineName, LocalUserId, LocalGroupId,
        GlobalUserNameID, FQAN, VOID, VOGroupID, VORoleID, Status, StartTime, EndTime, SuspendDuration,
        WallDuration, CpuDuration, CpuCount, NetworkType, NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType, PublisherDNID)
      VALUES (
        VMUUID, SiteLookup(site), machineName, localUserId, localGroupId, DNLookup(globalUserName), 
        fqan, VOLookup(vo),
        VOGroupLookup(voGroup), VORoleLookup(voRole), status, startTime, endTime, IFNULL(suspendDuration, 0), 
	IF((wallDuration IS NULL) AND (status = "completed"), endTime - startTime, wallDuration), cpuDuration, cpuCount, networkType, networkInbound, networkOutbound, memory,
        disk, storageRecordId, imageId, cloudType, DNLookup(publisherDN)
        );
END //
DELIMITER ;


-- ------------------------------------------------------------------------------
-- CloudSummaries

DROP TABLE IF EXISTS CloudSummaries;
CREATE TABLE CloudSummaries (
  UpdateTime TIMESTAMP,

  SiteID INT NOT NULL, -- Foreign key

  Month INT NOT NULL,
  Year INT NOT NULL,

  GlobalUserNameID INT NOT NULL, -- Foreign key
  VOID INT NOT NULL, -- Foreign key
  VOGroupID INT NOT NULL, -- Foreign key
  VORoleID INT NOT NULL, -- Foreign key

  Status VARCHAR(255),
  CloudType VARCHAR(255),
  ImageId VARCHAR(255),

  EarliestStartTime DATETIME,
  LatestStartTime DATETIME,
  WallDuration BIGINT,
  CpuDuration BIGINT,

  NetworkInbound BIGINT,
  NetworkOutbound BIGINT,
  Memory BIGINT,
  Disk BIGINT,
 
  NumberOfVMs INT,
  
  PublisherDNID VARCHAR(255),

  PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId)

);

DROP PROCEDURE IF EXISTS ReplaceCloudSummaryRecord;
DELIMITER //
CREATE PROCEDURE ReplaceCloudSummaryRecord(
  site VARCHAR(255), month INT, year INT, globalUserName VARCHAR(255), 
  vo VARCHAR(255), voGroup VARCHAR(255), voRole VARCHAR(255), status VARCHAR(255),
  cloudType VARCHAR(255), imageId VARCHAR(255), 
  earliestStartTime DATETIME, latestStartTime DATETIME, 
  wallDuration BIGINT, cpuDuration BIGINT, 
  networkInbound BIGINT, networkOutbound BIGINT, memory BIGINT, 
  disk BIGINT, numberOfVMs BIGINT,
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO CloudSummaries(SiteID, Month, Year, GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId, EarliestStartTime, LatestStartTime, 
        WallDuration, CpuDuration, NetworkInbound, NetworkOutbound, Memory, Disk, NumberOfVMs,  PublisherDNID)
      VALUES (
        SiteLookup(site), month, year, DNLookup(globalUserName), VOLookup(vo),
        VOGroupLookup(voGroup), VORoleLookup(voRole), status, cloudType, imageId, earliestStartTime, latestStartTime, 
        wallDuration, cpuDuration, networkInbound, networkOutbound, memory,
        disk, numberOfVMs, DNLookup(publisherDN)
        );
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS SummariseVMs;
DELIMITER //
CREATE PROCEDURE SummariseVMs()
BEGIN
CREATE TEMPORARY TABLE TCloudRecordsWithMeasurementTime
(INDEX index_measurementtime USING BTREE (MeasurementTime))
SELECT *, TIMESTAMPADD(SECOND, (IFNULL(SuspendDuration, 0) + WallDuration), StartTime) as MeasurementTime FROM CloudRecords;

CREATE TEMPORARY TABLE TGreatestMeasurementTimePerMonth
(INDEX index_greatestmeasurementtime USING BTREE (MaxMT))
select 
	Year(MeasurementTime) as Year, 
	Month(MeasurementTime) as Month, 
	VMUUID, 
	max(MeasurementTime) as MaxMT 
	from TCloudRecordsWithMeasurementTime 
	group by 
		Year(MeasurementTime), 
		Month(MeasurementTime), 
		VMUUID
;
DROP TABLE IF EXISTS LastCloudRecordPerMonth;
CREATE TABLE LastCloudRecordPerMonth
(INDEX index_vmuuidyearmonth USING BTREE (VMUUID, Year, Month))
SELECT 
	a.*, 
	Year(a.MeasurementTime) as Year, 
	Month(a.MeasurementTime) as Month 
	from TCloudRecordsWithMeasurementTime as a 
	left join 
	TGreatestMeasurementTimePerMonth as b 
	on (
		Year(a.MeasurementTime) = b.Year and 
		Month(a.MeasurementTime) = b.Month and
	        a.VMUUID = b.VMUUID
	)       
	where a.MeasurementTime = b.MaxMT
	
	ORDER BY a.VMUUID, Year(a.MeasurementTime), Month(a.MeasurementTime)
;

-- Based on discussion here: http://stackoverflow.com/questions/13196190/mysql-subtracting-value-from-previous-row-group-by

CREATE TEMPORARY TABLE TVMUsagePerMonth
(INDEX index_VMUsagePerMonth USING BTREE (VMUUID, Month, Year))
SELECT
	ThisRecord.VMUUID as VMUUID,
	ThisRecord.SiteID as SiteID,
	ThisRecord.Month as Month,
	ThisRecord.Year as Year,
	ThisRecord.GlobalUserNameID as GlobalUserNameID,
	ThisRecord.VOID as VOID,
	ThisRecord.VOGroupID as VOGroupID,
	ThisRecord.VORoleID as VORoleID,
	ThisRecord.Status as Status,
	ThisRecord.CloudType as CloudType,
	ThisRecord.ImageId as ImageId,
	ThisRecord.StartTime as StartTime,
	COALESCE(ThisRecord.WallDuration - IFNULL(PrevRecord.WallDuration, 0.00)) AS ComputedWallDuration,
	COALESCE(ThisRecord.CpuDuration - IFNULL(PrevRecord.CpuDuration, 0.00)) AS ComputedCpuDuration,
	COALESCE(ThisRecord.NetworkInbound - IFNULL(PrevRecord.NetworkInbound, 0.00)) AS ComputedNetworkInbound,
	COALESCE(ThisRecord.NetworkOutbound - IFNULL(PrevRecord.NetworkOutbound, 0.00)) AS ComputedNetworkOutbound,
	-- Will Memory change during the course of the VM lifetime? If so, do we report a maximum, or
	-- average, or something else?
	-- If it doesn't change:
	ThisRecord.Memory,
	ThisRecord.Disk -- As above: constant or changing?
FROM	LastCloudRecordPerMonth as ThisRecord
LEFT JOIN LastCloudRecordPerMonth as PrevRecord
ON 	(ThisRecord.VMUUID = PrevRecord.VMUUID and
	PrevRecord.MeasurementTime = (SELECT max(MeasurementTime)
					FROM LastCloudRecordPerMonth
					WHERE VMUUID = ThisRecord.VMUUID
					AND MeasurementTime < ThisRecord.MeasurementTime)
	);

    REPLACE INTO CloudSummaries(SiteID, Month, Year, GlobalUserNameID, VOID,
		VOGroupID, VORoleID, Status, CloudType, ImageId, EarliestStartTime, LatestStartTime, WallDuration, CpuDuration, NetworkInbound,
			NetworkOutbound, Memory, Disk, NumberOfVMs, PublisherDNID)
    SELECT SiteID,
    Month, Year,
    GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId,
    MIN(StartTime),
    MAX(StartTime),
    SUM(ComputedWallDuration),
    SUM(ComputedCpuDuration),
    SUM(ComputedNetworkInbound),
    SUM(ComputedNetworkOutbound),
    SUM(Memory),
    SUM(Disk),
    COUNT(*),
    'summariser'
    FROM TVMUsagePerMonth
    GROUP BY SiteID, Month, Year, GlobalUserNameID, VOID, VOGroupID, VORoleID, Status, CloudType, ImageId
    ORDER BY NULL;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- LastUpdated
DROP TABLE IF EXISTS LastUpdated;
CREATE TABLE LastUpdated (
  UpdateTime TIMESTAMP NOT NULL,
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
-- DNs

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
    SELECT UpdateTime, VMUUID, site.name SiteName, MachineName, 
           LocalUserId, LocalGroupId, userdn.name GlobalUserName, FQAN, vo.name VO, 
           vogroup.name VOGroup, vorole.name VORole,
           Status, StartTime, EndTime,
           SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, DNs userdn, VOs vo, VOGroups vogroup, VORoles vorole WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id
        AND VOGroupID = vogroup.id
        AND VORoleID = vorole.id;

-- -----------------------------------------------------------------------------
-- View on CloudRecords
CREATE VIEW VAnonCloudRecords AS
    SELECT UpdateTime, VMUUID, site.name SiteName, MachineName,
           LocalUserId, LocalGroupId, GlobalUserNameID, FQAN, vo.name VO,  Status, StartTime, EndTime,
           SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, DNs userdn, VOs vo WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id;
        
-- -----------------------------------------------------------------------------
-- View on CloudSummaries
CREATE VIEW VCloudSummaries AS
    SELECT UpdateTime, site.name SiteName, Month, Year,
           userdn.name GlobalUserName, vo.name VO, 
           vogroup.name VOGroup, vorole.name VORole,
           Status, CloudType, ImageId, EarliestStartTime, LatestStartTime,
           WallDuration, CpuDuration, NetworkInbound, NetworkOutbound, Memory, Disk, 
           NumberOfVMs
    FROM CloudSummaries, Sites site, DNs userdn, VOs vo, VOGroups vogroup, VORoles vorole WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id
        AND VOGroupID = vogroup.id
        AND VORoleID = vorole.id;

