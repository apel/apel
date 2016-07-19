-- The first thing we can do is replace the SummariseVMs procedure

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

-- Are start times guranteed to be there? let's assume so for now
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
