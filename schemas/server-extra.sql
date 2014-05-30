-- Extra views on NormalisedSuperSummaries for the central APEL server.
-- This schema does not need to be loaded by regional servers.

-- TODO Check if need conversion to hours (divide by 3600).

DROP VIEW IF EXISTS VSumCPU;

CREATE VIEW VSumCPU AS
    SELECT
        Sites.name AS ExecutingSite,
        VOs.name AS LCGUserVO,
        CAST(SUM(NumberOfJobs) AS UNSIGNED) AS Njobs,
        ROUND((SUM(CpuDuration) / 3600), 0) AS SumCPU,
        ROUND(SUM(NormalisedCpuDuration / 3600), 0) AS NormSumCPU,
        ROUND((SUM(WallDuration) / 3600), 0) AS SumWCT,
        ROUND(SUM(NormalisedWallDuration / 3600), 0) AS NormSumWCT,
        Month,
        Year,
        CAST(MIN(EarliestEndTime) AS DATE) AS RecordStart,
        CAST(MAX(LatestEndTime) AS DATE) AS RecordEnd
    FROM
        NormalisedSuperSummaries,
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
        ROUND(SUM((NormalisedCpuDuration) / 3600),0) AS NormSumCPU,
        ROUND((SUM(WallDuration) / 3600),0) AS SumWCT,
        ROUND(SUM((NormalisedWallDuration) / 3600),0) AS NormSumWCT,
        Month,
        Year,
        CAST(MIN(EarliestEndTime) AS DATE) AS RecordStart,
        CAST(MAX(LatestEndTime) AS DATE) AS RecordEnd
    FROM
        NormalisedSuperSummaries,
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


DROP VIEW IF EXISTS VSpecIntHistory;

CREATE VIEW VSpecIntHistory AS
    SELECT
        site.name AS ExecutingSite,
        CAST(ROUND(NormalisedWallDuration / WallDuration * 250, 0) AS UNSIGNED) AS SpecInt2000,
        CAST(SUM(NumberOfJobs) AS UNSIGNED) AS Njobs,
        Month,
        Year,
        CAST(MIN(EarliestEndTime) AS DATE) AS RecordStart,
        CAST(MAX(LatestEndTime) AS DATE) AS RecordEnd
    FROM
        NormalisedSuperSummaries JOIN Sites AS site ON SiteID = site.id
    GROUP BY
        SiteID,
        SpecInt2000,
        Year,
        Month;


DROP VIEW IF EXISTS VHepSpecHistory;

CREATE VIEW VHepSpecHistory AS
    SELECT
        site.name AS Site,
        CAST(ROUND(NormalisedWallDuration / WallDuration, 0) AS UNSIGNED) AS HepSpec06,
        SUM(NumberOfJobs) AS NumberOfJobs,
        Year,
        Month,
        CAST(MIN(EarliestEndTime) AS DATE) AS EarliestEndDate,
        CAST(MAX(LatestEndTime) AS DATE) AS LatestEndDate
    FROM
        NormalisedSuperSummaries JOIN Sites AS site ON SiteID = site.id
    GROUP BY
        SiteID,
        HepSpec06,
        Year,
        Month;
