-- This script contains a SQL block that can rollback
-- APEL version 2.3.0 databases of the following types to 2.2.1:
--  - Server Grid Accounting Database

-- ROLLBACK SCRIPT FOR SERVER SCHEMA


-- Modifying primary key needs to be done explicitly before dropping the column.
ALTER TABLE NormalisedSummaries
  DROP PRIMARY KEY,
  ADD PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID,
                   SubmitHostId, NodeCount, Processors);

ALTER TABLE NormalisedSummaries
  DROP ServiceLevelType;


DROP PROCEDURE IF EXISTS ReplaceNormalisedSummary;
DELIMITER //
CREATE PROCEDURE ReplaceNormalisedSummary(
  site VARCHAR(255),  month INT,  year INT,
  globalUserName VARCHAR(255), vo VARCHAR(255), voGroup VARCHAR(255), voRole VARCHAR(255),
  submitHost VARCHAR(255), infrastructure VARCHAR(50),
  nodeCount INT, processors INT, earliestEndTime DATETIME, latestEndTime DATETIME, wallDuration BIGINT, cpuDuration BIGINT,
  normalisedWallDuration BIGINT, normalisedCpuDuration BIGINT, numberOfJobs INT, publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO NormalisedSummaries(SiteID, Month, Year, GlobalUserNameID, VOID,
        VOGroupID, VORoleID, SubmitHostId, Infrastructure,
        NodeCount, Processors, EarliestEndTime, LatestEndTime, WallDuration,
        CpuDuration, NormalisedWallDuration, NormalisedCpuDuration,
        NumberOfJobs, PublisherDNID)
      VALUES (
        SiteLookup(site), month, year, DNLookup(globalUserName), VOLookup(vo),
        VOGroupLookup(voGroup), VORoleLookup(voRole), SubmitHostLookup(submitHost),
        infrastructure, nodeCount, processors, earliestEndTime,
        latestEndTime, wallDuration, cpuDuration, normalisedWallDuration, normalisedCpuDuration,
        numberOfJobs, DNLookup(publisherDN));
END //
DELIMITER ;


ALTER TABLE HybridSuperSummaries
  MODIFY ServiceLevelType VARCHAR(50) NOT NULL DEFAULT '';


DROP PROCEDURE IF EXISTS CopyNormalisedSummaries;

DELIMITER //
CREATE PROCEDURE CopyNormalisedSummaries()
BEGIN
  REPLACE INTO HybridSuperSummaries(SiteID, Month, Year, GlobalUserNameID, VOID,
    VOGroupID, VORoleID, SubmitHostID, Infrastructure, NodeCount, Processors,
    EarliestEndTime, LatestEndTime, WallDuration, CpuDuration,
    NormalisedWallDuration, NormalisedCpuDuration, NumberOfJobs)
  SELECT SiteID,
        Month,
        Year,
        GlobalUserNameID,
        VOID,
        VOGroupID,
        VORoleID,
        SubmitHostID,
        Infrastructure,
        NodeCount,
        Processors,
        EarliestEndTime,
        LatestEndTime,
        WallDuration,
        CpuDuration,
        NormalisedWallDuration,
        NormalisedCpuDuration,
        NumberOfJobs
  FROM NormalisedSummaries;
END //
DELIMITER ;


DROP VIEW IF EXISTS VNormalisedSummaries;
CREATE VIEW VNormalisedSummaries AS
    SELECT
        UpdateTime,
        site.name Site,
        Month,
        Year,
        userdn.name GlobalUserName,
        vos.name VO,
        vogroup.name VOGroup,
        vorole.name VORole,
        submithost.name SubmitHost,
        Infrastructure,
        NodeCount,
        Processors,
        EarliestEndTime,
        LatestEndTime,
        WallDuration,
        CpuDuration,
        NormalisedWallDuration,
        NormalisedCpuDuration,
        NumberOfJobs
    FROM NormalisedSummaries,
         Sites site,
         DNs userdn,
         VORoles vorole,
         VOs vos,
         VOGroups vogroup,
         SubmitHosts submithost
    WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id
        AND VORoleID = vorole.id
        AND VOID = vos.id
        AND VOGroupID = vogroup.id
        AND SubmitHostID = submithost.id;


DROP VIEW IF EXISTS VNormalisedSuperSummaries;

CREATE VIEW VNormalisedSuperSummaries AS
  SELECT UpdateTime,
         site.name Site,
         Month,
         Year,
         userdn.name GlobalUserName,
         vos.name VO,
         vogroup.name VOGroup,
         vorole.name VORole,
         submithost.name SubmitHost,
         Infrastructure,
         NodeCount,
         Processors,
         MIN(EarliestEndTime) AS EarliestEndTime,
         MAX(LatestEndTime) AS LatestEndTime,
         SUM(WallDuration) AS WallDuration,
         SUM(CpuDuration) AS CpuDuration,
         SUM(NormalisedWallDuration) AS NormalisedWallDuration,
         SUM(NormalisedCpuDuration) AS NormalisedCpuDuration,
         SUM(NumberOfJobs) AS NumberOfJobs
  FROM HybridSuperSummaries,
       Sites AS site,
       DNs AS userdn,
       VORoles AS vorole,
       VOs AS vos,
       VOGroups AS vogroup,
       SubmitHosts AS submithost
  WHERE SiteID = site.id
    AND GlobalUserNameID = userdn.id
    AND VORoleID = vorole.id
    AND VOID = vos.id
    AND VOGroupID = vogroup.id
    AND SubmitHostID = submithost.id
  GROUP BY SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID,
           SubmitHostId, Infrastructure, NodeCount, Processors;
