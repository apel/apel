-- Extra views and partitioning for the central APEL server.
-- This schema does not need to be loaded by regional servers.
-- -----------------------------------------------------------------------------

-- Partitioning for JobRecords to aid query performance and monthly deletions

-- More partitions can be added by "reorganizing" the pDefault parition. E.g.:
/*
ALTER TABLE JobRecords REORGANIZE PARTITION pDefault INTO (
    PARTITION p2024_01 VALUES LESS THAN (TO_DAYS('2024-02-01')),
    PARTITION p2024_02 VALUES LESS THAN (TO_DAYS('2024-03-01')),
    PARTITION p2024_03 VALUES LESS THAN (TO_DAYS('2024-04-01')),
    PARTITION pDefault VALUES LESS THAN MAXVALUE
);
*/

ALTER TABLE JobRecords
PARTITION BY RANGE (TO_DAYS(EndTime)) (
PARTITION p2023_01 VALUES LESS THAN (TO_DAYS('2023-02-01')),
PARTITION p2023_02 VALUES LESS THAN (TO_DAYS('2023-03-01')),
PARTITION p2023_03 VALUES LESS THAN (TO_DAYS('2023-04-01')),
PARTITION p2023_04 VALUES LESS THAN (TO_DAYS('2023-05-01')),
PARTITION p2023_05 VALUES LESS THAN (TO_DAYS('2023-06-01')),
PARTITION p2023_06 VALUES LESS THAN (TO_DAYS('2023-07-01')),
PARTITION p2023_07 VALUES LESS THAN (TO_DAYS('2023-08-01')),
PARTITION p2023_08 VALUES LESS THAN (TO_DAYS('2023-09-01')),
PARTITION p2023_09 VALUES LESS THAN (TO_DAYS('2023-10-01')),
PARTITION p2023_10 VALUES LESS THAN (TO_DAYS('2023-11-01')),
PARTITION p2023_11 VALUES LESS THAN (TO_DAYS('2023-12-01')),
PARTITION p2023_12 VALUES LESS THAN (TO_DAYS('2024-01-01')),
PARTITION p2024_01 VALUES LESS THAN (TO_DAYS('2024-02-01')),
PARTITION p2024_02 VALUES LESS THAN (TO_DAYS('2024-03-01')),
PARTITION p2024_03 VALUES LESS THAN (TO_DAYS('2024-04-01')),
PARTITION p2024_04 VALUES LESS THAN (TO_DAYS('2024-05-01')),
PARTITION p2024_05 VALUES LESS THAN (TO_DAYS('2024-06-01')),
PARTITION p2024_06 VALUES LESS THAN (TO_DAYS('2024-07-01')),
PARTITION p2024_07 VALUES LESS THAN (TO_DAYS('2024-08-01')),
PARTITION p2024_08 VALUES LESS THAN (TO_DAYS('2024-09-01')),
PARTITION p2024_09 VALUES LESS THAN (TO_DAYS('2024-10-01')),
PARTITION p2024_10 VALUES LESS THAN (TO_DAYS('2024-11-01')),
PARTITION p2024_11 VALUES LESS THAN (TO_DAYS('2024-12-01')),
PARTITION p2024_12 VALUES LESS THAN (TO_DAYS('2025-01-01')),
PARTITION p2025_01 VALUES LESS THAN (TO_DAYS('2025-02-01')),
PARTITION p2025_02 VALUES LESS THAN (TO_DAYS('2025-03-01')),
PARTITION p2025_03 VALUES LESS THAN (TO_DAYS('2025-04-01')),
PARTITION p2025_04 VALUES LESS THAN (TO_DAYS('2025-05-01')),
PARTITION p2025_05 VALUES LESS THAN (TO_DAYS('2025-06-01')),
PARTITION p2025_06 VALUES LESS THAN (TO_DAYS('2025-07-01')),
PARTITION p2025_07 VALUES LESS THAN (TO_DAYS('2025-08-01')),
PARTITION p2025_08 VALUES LESS THAN (TO_DAYS('2025-09-01')),
PARTITION p2025_09 VALUES LESS THAN (TO_DAYS('2025-10-01')),
PARTITION p2025_10 VALUES LESS THAN (TO_DAYS('2025-11-01')),
PARTITION p2025_11 VALUES LESS THAN (TO_DAYS('2025-12-01')),
PARTITION p2025_12 VALUES LESS THAN (TO_DAYS('2026-01-01')),
PARTITION p2026_01 VALUES LESS THAN (TO_DAYS('2026-02-01')),
PARTITION p2026_02 VALUES LESS THAN (TO_DAYS('2026-03-01')),
PARTITION p2026_03 VALUES LESS THAN (TO_DAYS('2026-04-01')),
PARTITION p2026_04 VALUES LESS THAN (TO_DAYS('2026-05-01')),
PARTITION p2026_05 VALUES LESS THAN (TO_DAYS('2026-06-01')),
PARTITION p2026_06 VALUES LESS THAN (TO_DAYS('2026-07-01')),
PARTITION p2026_07 VALUES LESS THAN (TO_DAYS('2026-08-01')),
PARTITION p2026_08 VALUES LESS THAN (TO_DAYS('2026-09-01')),
PARTITION p2026_09 VALUES LESS THAN (TO_DAYS('2026-10-01')),
PARTITION p2026_10 VALUES LESS THAN (TO_DAYS('2026-11-01')),
PARTITION p2026_11 VALUES LESS THAN (TO_DAYS('2026-12-01')),
PARTITION p2026_12 VALUES LESS THAN (TO_DAYS('2027-01-01')),
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
