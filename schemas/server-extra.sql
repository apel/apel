-- Extra views and partitioning for the central APEL server.
-- This schema does not need to be loaded by regional servers.
-- -----------------------------------------------------------------------------

-- Partitioning for JobRecords to aid query performance and monthly deletions

ALTER TABLE JobRecords
PARTITION BY RANGE (TO_DAYS(EndTime)) (
PARTITION p2012_12 VALUES LESS THAN (TO_DAYS('2013-01-01')),
PARTITION p2013_01 VALUES LESS THAN (TO_DAYS('2013-02-01')),
PARTITION p2013_02 VALUES LESS THAN (TO_DAYS('2013-03-01')),
PARTITION p2013_03 VALUES LESS THAN (TO_DAYS('2013-04-01')),
PARTITION p2013_04 VALUES LESS THAN (TO_DAYS('2013-05-01')),
PARTITION p2013_05 VALUES LESS THAN (TO_DAYS('2013-06-01')),
PARTITION p2013_06 VALUES LESS THAN (TO_DAYS('2013-07-01')),
PARTITION p2013_07 VALUES LESS THAN (TO_DAYS('2013-08-01')),
PARTITION p2013_08 VALUES LESS THAN (TO_DAYS('2013-09-01')),
PARTITION p2013_09 VALUES LESS THAN (TO_DAYS('2013-10-01')),
PARTITION p2013_10 VALUES LESS THAN (TO_DAYS('2013-11-01')),
PARTITION p2013_11 VALUES LESS THAN (TO_DAYS('2013-12-01')),
PARTITION p2013_12 VALUES LESS THAN (TO_DAYS('2014-01-01')),
PARTITION p2014_01 VALUES LESS THAN (TO_DAYS('2014-02-01')),
PARTITION p2014_02 VALUES LESS THAN (TO_DAYS('2014-03-01')),
PARTITION p2014_03 VALUES LESS THAN (TO_DAYS('2014-04-01')),
PARTITION p2014_04 VALUES LESS THAN (TO_DAYS('2014-05-01')),
PARTITION p2014_05 VALUES LESS THAN (TO_DAYS('2014-06-01')),
PARTITION p2014_06 VALUES LESS THAN (TO_DAYS('2014-07-01')),
PARTITION p2014_07 VALUES LESS THAN (TO_DAYS('2014-08-01')),
PARTITION p2014_08 VALUES LESS THAN (TO_DAYS('2014-09-01')),
PARTITION p2014_09 VALUES LESS THAN (TO_DAYS('2014-10-01')),
PARTITION p2014_10 VALUES LESS THAN (TO_DAYS('2014-11-01')),
PARTITION p2014_11 VALUES LESS THAN (TO_DAYS('2014-12-01')),
PARTITION p2014_12 VALUES LESS THAN (TO_DAYS('2015-01-01')),
PARTITION p2015_01 VALUES LESS THAN (TO_DAYS('2015-02-01')),
PARTITION p2015_02 VALUES LESS THAN (TO_DAYS('2015-03-01')),
PARTITION p2015_03 VALUES LESS THAN (TO_DAYS('2015-04-01')),
PARTITION p2015_04 VALUES LESS THAN (TO_DAYS('2015-05-01')),
PARTITION p2015_05 VALUES LESS THAN (TO_DAYS('2015-06-01')),
PARTITION p2015_06 VALUES LESS THAN (TO_DAYS('2015-07-01')),
PARTITION p2015_07 VALUES LESS THAN (TO_DAYS('2015-08-01')),
PARTITION p2015_08 VALUES LESS THAN (TO_DAYS('2015-09-01')),
PARTITION p2015_09 VALUES LESS THAN (TO_DAYS('2015-10-01')),
PARTITION p2015_10 VALUES LESS THAN (TO_DAYS('2015-11-01')),
PARTITION p2015_11 VALUES LESS THAN (TO_DAYS('2015-12-01')),
PARTITION p2015_12 VALUES LESS THAN (TO_DAYS('2016-01-01')),
PARTITION p2016_01 VALUES LESS THAN (TO_DAYS('2016-02-01')),
PARTITION p2016_02 VALUES LESS THAN (TO_DAYS('2016-03-01')),
PARTITION p2016_03 VALUES LESS THAN (TO_DAYS('2016-04-01')),
PARTITION p2016_04 VALUES LESS THAN (TO_DAYS('2016-05-01')),
PARTITION p2016_05 VALUES LESS THAN (TO_DAYS('2016-06-01')),
PARTITION p2016_06 VALUES LESS THAN (TO_DAYS('2016-07-01')),
PARTITION p2016_07 VALUES LESS THAN (TO_DAYS('2016-08-01')),
PARTITION p2016_08 VALUES LESS THAN (TO_DAYS('2016-09-01')),
PARTITION p2016_09 VALUES LESS THAN (TO_DAYS('2016-10-01')),
PARTITION p2016_10 VALUES LESS THAN (TO_DAYS('2016-11-01')),
PARTITION p2016_11 VALUES LESS THAN (TO_DAYS('2016-12-01')),
PARTITION p2016_12 VALUES LESS THAN (TO_DAYS('2017-01-01')),
PARTITION pDefault VALUES LESS THAN MAXVALUE
);

-- -----------------------------------------------------------------------------

DROP VIEW IF EXISTS VSumCPU;

CREATE VIEW VSumCPU AS
    SELECT
        Sites.name AS ExecutingSite,
        VOs.name AS LCGUserVO,
        CAST(SUM(NumberOfJobs) AS UNSIGNED) AS Njobs,
        ROUND((SUM(CpuDuration) / 3600), 0) AS SumCPU,
        -- Divide by 4 to convert to SI2K for compatibility with current system
        ROUND(SUM(NormalisedCpuDuration / 4 / 3600), 0) AS NormSumCPU,
        ROUND((SUM(WallDuration) / 3600), 0) AS SumWCT,
        ROUND(SUM(NormalisedWallDuration / 4 / 3600), 0) AS NormSumWCT,
        Month,
        Year,
        CAST(MIN(EarliestEndTime) AS DATE) AS RecordStart,
        CAST(MAX(LatestEndTime) AS DATE) AS RecordEnd
    FROM
        HybridSuperSummaries,
        Sites,
        VOs
    WHERE
        NumberOfJobs > 0
        AND SiteID = Sites.id
        AND VOID = VOs.id
    GROUP BY
        Sites.name,
        VOs.name,
        Month,
        Year;


DROP VIEW IF EXISTS VUserCPU;

CREATE VIEW VUserCPU AS
    SELECT
        Sites.name AS ExecutingSite,
        VOs.name AS LCGUserVO,
        DNs.name AS UserDN,
        VOGroups.name AS PrimaryGroup,
        VORoles.name AS PrimaryRole,
        CAST(SUM(NumberOfJobs) AS UNSIGNED) AS Njobs,
        ROUND((SUM(CpuDuration) / 3600),0) AS SumCPU,
        -- Divide by 4 to convert to SI2K for compatibility with current system
        ROUND(SUM((NormalisedCpuDuration) / 4 / 3600),0) AS NormSumCPU,
        ROUND((SUM(WallDuration) / 3600),0) AS SumWCT,
        ROUND(SUM((NormalisedWallDuration) / 4 / 3600),0) AS NormSumWCT,
        Month,
        Year,
        CAST(MIN(EarliestEndTime) AS DATE) AS RecordStart,
        CAST(MAX(LatestEndTime) AS DATE) AS RecordEnd
    FROM
        HybridSuperSummaries,
        Sites,
        VOs,
        DNs,
        VOGroups,
        VORoles
    WHERE
        NumberOfJobs > 0
        AND SiteID = Sites.id
        AND VOID = VOs.id
        AND GlobalUserNameID = DNs.id
        AND VOGroupID = VOGroups.id
        AND VORoleID = VORoles.id
    GROUP BY
        Sites.name,
        VOs.name,
        DNs.name,
        VOGroups.name,
        VORoles.name,
        Month,
        Year;

-- -----------------------------------------------------------------------------

DROP VIEW IF EXISTS VSpecIntHistory;

CREATE VIEW VSpecIntHistory AS
    SELECT site.name AS ExecutingSite,
           CAST(ROUND(IF((ServiceLevelType = 'HEPSPEC'), (ServiceLevel * 250), ServiceLevel), 0) AS UNSIGNED) AS SpecInt2000,
           CAST(SUM(NumberOfJobs) AS UNSIGNED) AS Njobs,
           Month,
           Year,
           CAST(MIN(EarliestEndTime) AS DATE) AS RecordStart,
           CAST(MAX(LatestEndTime) AS DATE) AS RecordEnd
    FROM HybridSuperSummaries
    JOIN Sites AS site ON SiteID = site.id
    -- Exclude sites that send normalised summaries where service level is not set
    WHERE ServiceLevelType <> ''
    GROUP BY SiteID,
             SpecInt2000,
             Year,
             Month;


DROP VIEW IF EXISTS VHepSpecHistory;

CREATE VIEW VHepSpecHistory AS
  SELECT site.name AS Site,
         IF((ServiceLevelType = 'HEPSPEC'), ServiceLevel, (ServiceLevel / 250)) AS HepSpec06,
         SUM(NumberOfJobs) AS NumberOfJobs,
         Year,
         Month,
         CAST(MIN(EarliestEndTime) AS DATE) AS EarliestEndDate,
         CAST(MAX(LatestEndTime) AS DATE) AS LatestEndDate
  FROM HybridSuperSummaries
  JOIN Sites AS site ON SiteID = site.id
  -- Exclude sites that send normalised summaries where service level is not set
  WHERE ServiceLevelType <> ''
  GROUP BY SiteID,
           HepSpec06,
           Year,
           Month;

-- -----------------------------------------------------------------------------

DROP VIEW IF EXISTS VLcgRecordsSync_v2;

CREATE VIEW VLcgRecordsSync_v2 AS
  SELECT CONCAT(site.name,'-',SyncRecords.Year,'-',SyncRecords.Month) AS RecordIdentity,
         site.name AS ExecutingSite,
         SUM(SyncRecords.NumberOfJobs) AS Njobs,
         NULL AS Ndays,
         NULL AS RecordStart,
         NULL AS RecordEnd,
         CAST(SyncRecords.UpdateTime AS DATE) AS MeasurementDate,
         CAST(SyncRecords.UpdateTime AS TIME) AS MeasurementTime
  FROM SyncRecords
  JOIN Sites AS site
  WHERE SyncRecords.SiteID = site.id
  GROUP BY 1;
