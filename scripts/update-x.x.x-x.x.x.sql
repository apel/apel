-- This script contains multiple comment blocks that can update
-- APEL version x.x.x databases of the following types to x.x.x:
--  - Cloud Accounting Database

/*
-- UPDATE SCRIPT FOR CLOUD SUMMARY SCHEMA

-- If you have a Cloud Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This section will:
-- - Remove CloudType from the CloudSummaries primary key. This
--   ensures new summaries overwrite old summaries after updates
--   to CASO version name.

ALTER TABLE CloudSummaries 
  DROP PRIMARY KEY,
  ADD PRIMARY KEY (
    SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID,
    VOID, VOGroupID, VORoleID, Status, ImageId, CloudType, CpuCount,
    BenchmarkType, Benchmark
  );

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
                                      AND MeasurementTime < ThisRecord.MeasurementTime
                                      -- This prevents negative summaries being caused
                                      -- by 'completed' records without an EndTime.
                                      -- Now, such Records are not included in this
                                      -- LEFT JOIN statement
                                      AND PrevRecord.MeasurementMonth<>0
                                      AND PrevRecord.MeasurementYear<>0)
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
          VOGroupID, VORoleID, Status, ImageId, CloudType, CpuCount,
          BenchmarkType, Benchmark
      ORDER BY NULL;
END //
DELIMITER ;

*/

