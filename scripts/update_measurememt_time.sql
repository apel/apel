ALTER TABLE CloudRecords
  ADD RecordCreateTime DATETIME NOT NULL AFTER UpdateTime,
  ADD MeasurementTime DATETIME NOT NULL AFTER EndTime,
  ADD MeasurementMonth INT NOT NULL AFTER MeasurementTime,
  ADD MeasurementYear INT NOT NULL AFTER MeasurementMonth;

Update CloudRecords SET
  MeasurementTime = IFNULL(TIMESTAMPADD(SECOND, (IFNULL(SuspendDuration, 0) + IFNULL(WallDuration, 0)), StartTime), '00-00-00 00:00:00'),
  RecordCreateTime = IFNULL(TIMESTAMPADD(SECOND, (IFNULL(SuspendDuration, 0) + IFNULL(WallDuration, 0)), StartTime), '00-00-00 00:00:00');

Update CloudRecords SET
  MeasurementMonth = Month(MeasurementTime),
  MeasurementYear = Year(MeasurementTime);

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
    DECLARE measurementTimeCalculated DATETIME;
    DECLARE recordCreateTimeNotNull DATETIME;

    IF(status='completed') THEN
        -- in this case, the recordCreateTime and measurementTime could
        -- be wildly different as the VM has ended.

        -- if we werent supplied a record create time
        -- for a completed VM we have decided to use the end time
        SET recordCreateTimeNotNull = IF(recordCreateTime IS NULL or recordCreateTime='0000-00-00 00:00:00', endTime, recordCreateTime);

        -- Use the end time as the measurement time
        SET measurementTimeCalculated = endTime;

    ELSE
        -- In the case of a running VM, the measurement time will
        -- equal the record create time
        IF(recordCreateTime IS NULL or recordCreateTime='0000-00-00 00:00:00') THEN
            -- Calculate the time of measurement so we can use it later to determine which
            -- accounting period this incoming record belongs too.
            SET measurementTimeCalculated = TIMESTAMPADD(SECOND, (IFNULL(suspendDuration, 0) + IFNULL(wallDuration, 0)), startTime);
            -- We recieve and currently accept messages without a start time
            -- which causes the mesaurementTimeCalculated to be NULL
            -- which causes a loader reject on a previously accepted message
            -- so for now, set it to the zero time stamp as is what happens currently
            SET measurementTimeCalculated = IFNULL(measurementTimeCalculated, '00-00-00 00:00:00');
            SET recordCreateTimeNotNull = measurementTimeCalculated;
        ELSE
             -- Use the supplied record create time as the measurement time
            SET measurementTimeCalculated = recordCreateTime;
            SET recordCreateTimeNotNull = recordCreateTime;
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
        suspendDuration, wallDuration, cpuDuration, cpuCount,
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
        CloudRecords.SuspendDuration = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, suspendDuration, CloudRecords.SuspendDuration),
        CloudRecords.WallDuration = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, wallDuration, CloudRecords.WallDuration),
        CloudRecords.CpuDuration = IF(measurementTimeCalculated > CloudRecords.MeasurementTime, cpuDuration, CloudRecords.CpuDuration),
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

ALTER TABLE CloudRecords DROP PRIMARY KEY, ADD PRIMARY KEY(VMUUID, MeasurementMonth, MeasurementYear);

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

DROP VIEW IF EXISTS VCloudRecords;
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
