-- This script contains multiple comment blocks that can update
-- APEL version 1.7.0 databases of the following types to 1.8.2:
--  - Cloud Accounting Database

/*
-- UPDATE SCRIPT FOR CLOUD SCHEMA

-- If you have a Cloud Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This section will:
-- - To make republishing easier, replace the ReplaceCloudRecord procedure
--   such that it will now keep the most recently recieved record, not the one
--   with the latest MeasurementTime.

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
    DECLARE endTimeNotNull DATETIME;

    IF(status='completed') THEN
        -- in this case, the recordCreateTime and measurementTime could
        -- be wildly different as the VM has ended.

        -- if we werent supplied a record create time
        -- for a completed VM we have decided to use the end time
        -- We have to check the EndTime is not null because we can't guarantee this as we
        -- previously loaded completed messages with no EndTime.
        SET endTimeNotNull = IFNULL(endTime, '0000-00-00 00:00:00');
        SET recordCreateTimeNotNull = IF(recordCreateTime IS NULL or recordCreateTime='0000-00-00 00:00:00', endTimeNotNull, recordCreateTime);

        -- Use the end time as the measurement time
        SET measurementTimeCalculated = endTimeNotNull;

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

    REPLACE INTO CloudRecords(RecordCreateTime, VMUUID, SiteID, CloudComputeServiceID, MachineName,
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
    ;
END //
DELIMITER ;
*/
