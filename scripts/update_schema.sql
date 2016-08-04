-- Create / Update Tables
-- Add CloudComputeServiceID, old rows get a NULL CloudComputeServiceID
ALTER TABLE CloudRecords ADD CloudComputeServiceID INT;
ALTER TABLE CloudSummaries ADD CloudComputeServiceID INT;

-- Add PublicIPCount, old rows get a NULL PublicIPCount
ALTER TABLE CloudRecords ADD PublicIPCount INT;
ALTER TABLE CloudSummaries ADD PublicIPCount BIGINT;

-- Add BenchmarkType, old rows get an empty VARCHAR
ALTER TABLE CloudRecords ADD BenchmarkType VARCHAR(50) NOT NULL;
ALTER TABLE CloudSummaries ADD BenchmarkType VARCHAR(50) NOT NULL;

-- Add Benchmark, old rows get 0.00
ALTER TABLE CloudRecords ADD Benchmark DECIMAL(10,3) NOT NULL;
ALTER TABLE CloudSummaries ADD Benchmark DECIMAL(10,3) NOT NULL;

-- Update any NULL StartTime to 0
UPDATE CloudRecords SET StartTime=0 WHERE StartTime is NULL;
-- Set StartTime to be NOT NULL
ALTER TABLE CloudRecords MODIFY StartTime DATETIME NOT NULL;

-- Update any NULL SuspendDuration to 0
UPDATE CloudRecords SET SuspendDuration=0 WHERE SuspendDuration is NULL;
-- Set SuspendDuration to be NOT NULL
ALTER TABLE CloudRecords MODIFY SuspendDuration INT NOT NULL;

-- Update and NULL WallDuration to 0
UPDATE CloudRecords SET WallDuration=0 WHERE WallDuration is NULL;
-- Set WallDuration to be NOT NULL
ALTER TABLE CloudRecords MODIFY WallDuration INT NOT NULL;

-- Replace the primary key
ALTER TABLE CloudRecords DROP PRIMARY KEY, ADD PRIMARY KEY(VMUUID, StartTime, SuspendDuration, WallDuration);

-- Create CloudComputeService
CREATE TABLE CloudComputeServices (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    INDEX(name)
);

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
           NetworkInbound, NetworkOutbound, PublicIPCount, Memory, Disk, BenchmarkType, Benchmark,  
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
        VORoleLookup(voRole), status, startTime, endTime, IFNULL(suspendDuration, 0), 
        IF((wallDuration IS NULL) AND (status = "completed"), endTime - startTime, wallDuration),
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
  wallDuration BIGINT, cpuDuration BIGINT, 
  networkInbound BIGINT, networkOutbound BIGINT, publicIPCount BIGINT, memory BIGINT, 
  disk BIGINT, benchmarkType VARCHAR(50), benchmark DECIMAL(10,3), numberOfVMs BIGINT,
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO CloudSummaries(SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID, VOID,
        VOGroupID, VORoleID, Status, CloudType, ImageId, EarliestStartTime, LatestStartTime, 
        WallDuration, CpuDuration, NetworkInbound, NetworkOutbound, PublicIPCount, Memory, Disk,
        BenchmarkType, Benchmark, NumberOfVMs,  PublisherDNID)
      VALUES (
        SiteLookup(site), CloudComputeServiceLookup(cloudComputeService), month, year,
        DNLookup(globalUserName), VOLookup(vo), VOGroupLookup(voGroup), VORoleLookup(voRole),
        status, cloudType, imageId, earliestStartTime, latestStartTime, wallDuration,
        cpuDuration, networkInbound, networkOutbound, publicIPCount, memory, disk, benchmarkType,
        benchmark, numberOfVMs, DNLookup(publisherDN)
        );
END //
DELIMITER ;

-- Replace SummariesVMs
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
        VOGroupID, VORoleID, Status, CloudType, ImageId, EarliestStartTime, LatestStartTime,
        WallDuration, CpuDuration, NetworkInbound, NetworkOutbound, Memory, Disk,
        NumberOfVMs, PublisherDNID)
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
    GROUP BY SiteID, Month, Year, GlobalUserNameID, VOID, VOGroupID, VORoleID,
        Status, CloudType, ImageId
    ORDER BY NULL;
END //
DELIMITER ;
