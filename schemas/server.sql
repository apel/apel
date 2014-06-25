
-- ------------------------------------------------------------------------------
-- JobRecords
DROP TABLE IF EXISTS JobRecords;
CREATE TABLE JobRecords ( 
  UpdateTime TIMESTAMP, 

  SiteID INT NOT NULL,                -- Foreign key
  SubmitHostID INT NOT NULL,          -- Foreign key
  MachineNameID INT NOT NULL,         -- Foreign key
  QueueID INT NOT NULL,               -- Foreign key

  LocalJobId VARCHAR(255) NOT NULL, 
  LocalUserId VARCHAR(255), 

  GlobalUserNameID INT NOT NULL,      -- Foreign key
  FQAN VARCHAR(255) DEFAULT NULL,
  VOID INT NOT NULL,                  -- Foreign key
  VOGroupID INT NOT NULL,             -- Foreign key
  VORoleID INT NOT NULL,              -- Foreign key

  WallDuration BIGINT UNSIGNED, 
  CpuDuration BIGINT UNSIGNED,
  NodeCount INT UNSIGNED NOT NULL DEFAULT 0,  
  Processors INT UNSIGNED NOT NULL DEFAULT 0, 
  
  MemoryReal BIGINT UNSIGNED,
  MemoryVirtual BIGINT UNSIGNED,

  StartTime DATETIME NOT NULL, 
  EndTime DATETIME NOT NULL, 
  EndYear INT,
  EndMonth INT,
  
  InfrastructureDescription VARCHAR(100),
  InfrastructureType VARCHAR(20),

  ServiceLevelType VARCHAR(50) NOT NULL,
  ServiceLevel DECIMAL(10,3) NOT NULL,

  PublisherDNID INT NOT NULL,        -- Foreign key

  PRIMARY KEY (SiteID, LocalJobId, EndTime),
  
  -- index for SummariseJobs() procedure. 
  -- Try to reuse this index as much as you can
  INDEX SummaryIdx (SiteID, VOID, GlobalUserNameID, VOGroupID, VORoleID, 
        EndYear, EndMonth, InfrastructureType, SubmitHostID, ServiceLevelType, ServiceLevel, 
        NodeCount, Processors, EndTime, WallDuration, CpuDuration),

  -- special index for retrieving data for UAS system
  INDEX UASIdx (VOID, UpdateTime)
);
 
 
DROP PROCEDURE IF EXISTS ReplaceJobRecord;
DELIMITER //
CREATE PROCEDURE ReplaceJobRecord(
  site VARCHAR(255), submitHost VARCHAR(255), machineName VARCHAR(255), 
  queue VARCHAR(100), localJobId VARCHAR(255),
  localUserId VARCHAR(255), globalUserName VARCHAR(255),
  fullyQualifiedAttributeName VARCHAR(255),
  vo VARCHAR(255), 
  voGroup VARCHAR(255), voRole VARCHAR(255), 
  wallDuration INT, cpuDuration INT, processors INT, nodeCount INT,
  startTime DATETIME, endTime DATETIME, infrastructureDescription VARCHAR(100), infrastructureType VARCHAR(20),
  memoryReal INT, memoryVirtual INT,
  serviceLevelType VARCHAR(50), serviceLevel DECIMAL(10,3),
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO JobRecords(SiteID, SubmitHostID, MachineNameID, QueueID,
	    LocalJobId, LocalUserId, GlobalUserNameID, FQAN,
        VOID, VOGroupID, VORoleID, WallDuration, CpuDuration, Processors, NodeCount, 
        StartTime, EndTime, EndYear, EndMonth, InfrastructureDescription, InfrastructureType, MemoryReal, MemoryVirtual, ServiceLevelType,
        ServiceLevel, PublisherDNID)
    VALUES (
        SiteLookup(site), SubmitHostLookup(submitHost), MachineNameLookup(machineName), 
        QueueLookup(queue), localJobId, localUserId,
        DNLookup(globalUserName), fullyQualifiedAttributeName, VOLookup(vo),
        VOGroupLookup(voGroup), VORoleLookup(voRole), wallDuration, cpuDuration,
        IFNULL(processors, 0), IFNULL(nodeCount, 0), startTime, endTime, 
        YEAR(endTime), MONTH(endTime), infrastructureDescription, infrastructureType, memoryReal,
        memoryVirtual, serviceLevelType, serviceLevel, DNLookup(publisherDN)
        );
END //
DELIMITER ;


-- -----------------------------------------------------------------------------
-- Summaries
DROP TABLE IF EXISTS Summaries;
CREATE TABLE Summaries (
  UpdateTime TIMESTAMP,
  SiteID INT NOT NULL,                  -- Foreign key
  Month INT NOT NULL,
  Year INT NOT NULL,
  GlobalUserNameID INT NOT NULL,        -- Foreign key
  VOID INT NOT NULL,                    -- Foreign key
  VOGroupID INT NOT NULL,               -- Foreign key
  VORoleID INT NOT NULL,                -- Foreign key
  SubmitHostId INT NOT NULL,
  InfrastructureType VARCHAR(20),
  ServiceLevelType VARCHAR(50) NOT NULL,
  ServiceLevel DECIMAL(10,3) NOT NULL,
  NodeCount INT NOT NULL,
  Processors INT NOT NULL,
  EarliestEndTime DATETIME,
  LatestEndTime DATETIME,
  WallDuration BIGINT UNSIGNED NOT NULL,
  CpuDuration BIGINT UNSIGNED NOT NULL,
  NumberOfJobs BIGINT UNSIGNED NOT NULL,
  PublisherDNID INT NOT NULL,

  PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID, 
               SubmitHostId, ServiceLevelType, ServiceLevel, NodeCount, Processors)
);


DROP PROCEDURE IF EXISTS ReplaceSummary;
DELIMITER //
CREATE PROCEDURE ReplaceSummary(
  site VARCHAR(255),  month INT,  year INT, 
  globalUserName VARCHAR(255), vo VARCHAR(255), voGroup VARCHAR(255), voRole VARCHAR(255), 
  submitHost VARCHAR(255), infrastructureType VARCHAR(50), serviceLevelType VARCHAR(50), serviceLevel DECIMAL(10,3),
  nodeCount INT, processors INT, earliestEndTime DATETIME, latestEndTime DATETIME, wallDuration INT, cpuDuration INT, 
   numberOfJobs INT, publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO Summaries(SiteID, Month, Year, GlobalUserNameID, VOID, 
        VOGroupID, VORoleID, SubmitHostId, InfrastructureType, ServiceLevelType, ServiceLevel,
        NodeCount, Processors, EarliestEndTime, LatestEndTime, WallDuration,
        CpuDuration, NumberOfJobs, PublisherDNID)
      VALUES (
        SiteLookup(site), month, year, DNLookup(globalUserName), VOLookup(vo), 
        VOGroupLookup(voGroup), VORoleLookup(voRole), SubmitHostLookup(submitHost),
        infrastructureType, serviceLevelType, serviceLevel, nodeCount, processors, earliestEndTime, 
        latestEndTime, wallDuration, cpuDuration, numberOfJobs, DNLookup(publisherDN));
END //
DELIMITER ;


-- -----------------------------------------------------------------------------
-- NormalisedSummaries
DROP TABLE IF EXISTS NormalisedSummaries;
CREATE TABLE NormalisedSummaries (
  UpdateTime TIMESTAMP,
  SiteID INT NOT NULL,                  -- Foreign key
  Month INT NOT NULL,
  Year INT NOT NULL,
  GlobalUserNameID INT NOT NULL,        -- Foreign key
  VOID INT NOT NULL,                    -- Foreign key
  VOGroupID INT NOT NULL,               -- Foreign key
  VORoleID INT NOT NULL,                -- Foreign key
  SubmitHostId INT NOT NULL,
  Infrastructure VARCHAR(20),
  NodeCount INT NOT NULL,
  Processors INT NOT NULL,
  EarliestEndTime DATETIME,
  LatestEndTime DATETIME,
  WallDuration BIGINT UNSIGNED NOT NULL,
  CpuDuration BIGINT UNSIGNED NOT NULL,
  NormalisedWallDuration BIGINT UNSIGNED NOT NULL,
  NormalisedCpuDuration BIGINT UNSIGNED NOT NULL,
  NumberOfJobs BIGINT UNSIGNED NOT NULL,
  PublisherDNID INT NOT NULL,

  PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID, 
               SubmitHostId, NodeCount, Processors)
);


DROP PROCEDURE IF EXISTS ReplaceNormalisedSummary;
DELIMITER //
CREATE PROCEDURE ReplaceNormalisedSummary(
  site VARCHAR(255),  month INT,  year INT, 
  globalUserName VARCHAR(255), vo VARCHAR(255), voGroup VARCHAR(255), voRole VARCHAR(255), 
  submitHost VARCHAR(255), infrastructure VARCHAR(50), 
  nodeCount INT, processors INT, earliestEndTime DATETIME, latestEndTime DATETIME, wallDuration INT, cpuDuration INT, 
  normalisedWallDuration INT, normalisedCpuDuration INT, numberOfJobs INT, publisherDN VARCHAR(255))
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


-- -----------------------------------------------------------------------------
-- SuperSummaries
DROP TABLE IF EXISTS SuperSummaries;
CREATE TABLE SuperSummaries (
  UpdateTime TIMESTAMP,
  SiteID INT NOT NULL,                  -- Foreign key
  Month INT NOT NULL,
  Year INT NOT NULL,
  GlobalUserNameID INT NOT NULL,        -- Foreign key
  VOID INT NOT NULL,                    -- Foreign key
  VOGroupID INT NOT NULL,               -- Foreign key
  VORoleID INT NOT NULL,                -- Foreign key
  SubmitHostId INT NOT NULL,
  InfrastructureType VARCHAR(20),
  ServiceLevelType VARCHAR(50) NOT NULL,
  ServiceLevel DECIMAL(10,3) NOT NULL,
  NodeCount INT NOT NULL,
  Processors INT NOT NULL,
  EarliestEndTime DATETIME,
  LatestEndTime DATETIME,
  WallDuration BIGINT UNSIGNED NOT NULL,
  CpuDuration BIGINT UNSIGNED NOT NULL,
  NumberOfJobs BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID, 
               SubmitHostId, InfrastructureType, ServiceLevelType, ServiceLevel,
               NodeCount, Processors)
);

-- -----------------------------------------------------------------------------
-- HybridSuperSummaries
-- These contain normalised durations as well as the original service levels

DROP TABLE IF EXISTS HybridSuperSummaries;

CREATE TABLE HybridSuperSummaries (
  UpdateTime TIMESTAMP,
  SiteID INT NOT NULL,                  -- ID for lookup table
  Month INT NOT NULL,
  Year INT NOT NULL,
  GlobalUserNameID INT NOT NULL,        -- ID for lookup table
  VOID INT NOT NULL,                    -- ID for lookup table
  VOGroupID INT NOT NULL,               -- ID for lookup table
  VORoleID INT NOT NULL,                -- ID for lookup table
  SubmitHostId INT NOT NULL,            -- ID for lookup table
  Infrastructure VARCHAR(20),
  ServiceLevelType VARCHAR(50),
  ServiceLevel DECIMAL(10,3),
  NodeCount INT NOT NULL,
  Processors INT NOT NULL,
  EarliestEndTime DATETIME,
  LatestEndTime DATETIME,
  WallDuration BIGINT UNSIGNED NOT NULL,
  CpuDuration BIGINT UNSIGNED NOT NULL,
  NormalisedWallDuration BIGINT UNSIGNED NOT NULL,
  NormalisedCpuDuration BIGINT UNSIGNED NOT NULL,
  NumberOfJobs BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID,
               SubmitHostId, Infrastructure, ServiceLevelType, ServiceLevel,
               NodeCount, Processors)
);


DROP PROCEDURE IF EXISTS SummariseJobs;

DELIMITER //
CREATE PROCEDURE SummariseJobs()
BEGIN
  REPLACE INTO HybridSuperSummaries(SiteID, Month, Year, GlobalUserNameID, VOID,
    VOGroupID, VORoleID, SubmitHostID, Infrastructure, ServiceLevelType,
    ServiceLevel, NodeCount, Processors, EarliestEndTime, LatestEndTime,
    WallDuration, CpuDuration, NormalisedWallDuration, NormalisedCpuDuration,
    NumberOfJobs)
  SELECT SiteID,
         EndMonth AS Month,
         EndYear AS Year,
         GlobalUserNameID,
         VOID,
         VOGroupID,
         VORoleID,
         SubmitHostID,
         InfrastructureType,
         ServiceLevelType,
         ServiceLevel,
         NodeCount,
         Processors,
         MIN(EndTime) AS EarliestEndTime,
         MAX(EndTime) AS LatestEndTime,
         SUM(WallDuration) AS SumWCT,
         SUM(CpuDuration) AS SumCPU,
         ROUND(SUM(IF(WallDuration > 0, WallDuration, 0) * IF(ServiceLevelType = "HEPSPEC", ServiceLevel, ServiceLevel / 250))) AS NormSumWCT,
         ROUND(SUM(IF(CpuDuration > 0, CpuDuration, 0) * IF(ServiceLevelType = "HEPSPEC", ServiceLevel, ServiceLevel / 250))) AS NormSumCPU,
         COUNT(*) AS Njobs
  FROM JobRecords
  GROUP BY SiteID, VOID, GlobalUserNameID, VOGroupID, VORoleID, EndYear,
           EndMonth, InfrastructureType, SubmitHostID, ServiceLevelType,
           ServiceLevel, NodeCount, Processors;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS NormaliseSummaries;

DELIMITER //
CREATE PROCEDURE NormaliseSummaries()
BEGIN
  REPLACE INTO HybridSuperSummaries(SiteID, Month, Year, GlobalUserNameID, VOID,
    VOGroupID, VORoleID, SubmitHostID, Infrastructure, ServiceLevelType,
    ServiceLevel, NodeCount, Processors, EarliestEndTime, LatestEndTime,
    WallDuration, CpuDuration, NormalisedWallDuration, NormalisedCpuDuration,
    NumberOfJobs)
  SELECT SiteID,
         Month,
         Year,
         GlobalUserNameID,
         VOID,
         VOGroupID,
         VORoleID,
         SubmitHostID,
         InfrastructureType,
         ServiceLevelType,
         ServiceLevel,
         NodeCount,
         Processors,
         EarliestEndTime,
         LatestEndTime,
         WallDuration,
         CpuDuration,
         ROUND(IF(WallDuration > 0, WallDuration, 0) * IF(ServiceLevelType = "HEPSPEC", ServiceLevel, ServiceLevel / 250)) AS NormSumWCT,
         ROUND(IF(CpuDuration > 0, CpuDuration, 0) * IF(ServiceLevelType = "HEPSPEC", ServiceLevel, ServiceLevel / 250)) AS NormSumCPU,
         NumberOfJobs
  FROM Summaries;
END //
DELIMITER ;


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


-- -----------------------------------------------------------------------------
-- SyncRecords
DROP TABLE IF EXISTS SyncRecords;
CREATE TABLE SyncRecords (
  UpdateTime TIMESTAMP, 
  SiteID INT NOT NULL,                  -- Foreign key
  SubmitHostID INT NOT NULL,            -- Foreign key
  NumberOfJobs INT NOT NULL,
  Month INT NOT NULL,
  Year INT NOT NULL,
  PublisherDNID INT NOT NULL,            -- Foreign key

  PRIMARY KEY (SiteID, SubmitHostID, Month, Year),

  INDEX(UpdateTime),
  INDEX(SiteID),
  INDEX(Month),
  INDEX(Year)

);


DROP PROCEDURE IF EXISTS ReplaceSyncRecord;
DELIMITER //
CREATE PROCEDURE ReplaceSyncRecord(
  site VARCHAR(255),  submitHost VARCHAR(255), njobs INT, month INT,  year INT, publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO SyncRecords(SiteID, SubmitHostID, NumberOfJobs, Month, Year, PublisherDNID)
      VALUES (
        SiteLookup(site), SubmitHostLookup(submitHost), njobs, month, year, DNLookup(publisherDN)
        );
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
DROP TABLE IF EXISTS Sites;
CREATE TABLE Sites (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,

    INDEX(name)
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
DROP TABLE IF EXISTS DNs;
CREATE TABLE DNs (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,

  INDEX(name)
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
-- SubmitHosts
DROP TABLE IF EXISTS SubmitHosts;
CREATE TABLE SubmitHosts (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
    
  INDEX(name)
) ;


DROP FUNCTION IF EXISTS SubmitHostLookup;
DELIMITER //
CREATE FUNCTION SubmitHostLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM SubmitHosts WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO SubmitHosts(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- MachineNames
DROP TABLE IF EXISTS MachineNames;
CREATE TABLE MachineNames (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,

  INDEX(name)
) ;

DROP FUNCTION IF EXISTS MachineNameLookup;
DELIMITER //
CREATE FUNCTION MachineNameLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM MachineNames WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO MachineNames(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- Queues
DROP TABLE IF EXISTS Queues;
CREATE TABLE Queues (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  
  INDEX(name)
) ;

DROP FUNCTION IF EXISTS QueueLookup;
DELIMITER //
CREATE FUNCTION QueueLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM Queues WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO Queues(name) VALUES (lookup);
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
-- View on Summaries
DROP VIEW IF EXISTS VSummaries;
CREATE VIEW VSummaries AS
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
        InfrastructureType,
        ServiceLevelType, 
        ServiceLevel,  
        NodeCount,
        Processors,
        EarliestEndTime, 
        LatestEndTime, 
        WallDuration, 
        CpuDuration, 
        NumberOfJobs
    FROM Summaries, 
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


-- -----------------------------------------------------------------------------
-- View on NormalisedSummaries
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


-- -----------------------------------------------------------------------------
-- View on HybridSuperSummaries
-- This view excludes the normalised duration fields.

DROP VIEW IF EXISTS VSuperSummaries;

CREATE VIEW VSuperSummaries AS
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
        Infrastructure AS InfrastructureType,
        ServiceLevelType, 
        ServiceLevel,  
        NodeCount,
        Processors,
        EarliestEndTime, 
        LatestEndTime, 
        WallDuration, 
        CpuDuration, 
        NumberOfJobs
    FROM HybridSuperSummaries, 
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


-- -----------------------------------------------------------------------------
-- View on HybridSuperSummaries
-- This view excludes the ServiceLevelType and ServiceLevel fields.

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
         EarliestEndTime,
         LatestEndTime,
         SUM(WallDuration),
         SUM(CpuDuration),
         SUM(NormalisedWallDuration),
         SUM(NormalisedCpuDuration),
         NumberOfJobs
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


-- -----------------------------------------------------------------------------
-- View on HybridSuperSummaries
-- useful form of data from HybridSuperSummaries

-- TODO Check relevance of this view
DROP VIEW IF EXISTS VUserSummaries;
CREATE VIEW VUserSummaries AS
    SELECT 
        Year,
        Month,
        site.name Site,
        vo.name VO,
        dn.name GlobalUserName,
        vogroup.name VOGroup,
        vorole.name VORole,
        SUM(WallDuration) AS TotalWallDuration,
        SUM(CpuDuration) AS TotalCpuDuration,
        ROUND(SUM(NormalisedWallDuration) / 3600, 2) AS NormalisedWallDuration,
        ROUND(SUM(NormalisedCpuDuration) / 3600, 2) AS NormalisedCpuDuration,
        SUM(NumberOfJobs) AS TotalNumberOfJobs,
        MIN(EarliestEndTime) as EarliestEndTime,
        MAX(LatestEndTime) as LatestEndTime
    FROM HybridSuperSummaries summary 
    INNER JOIN Sites site ON site.id=summary.SiteID
    INNER JOIN VOs vo ON summary.VOID = vo.id
    INNER JOIN DNs dn ON summary.GlobalUserNameID = dn.id
    INNER JOIN VOGroups vogroup ON summary.VOGroupID = vogroup.id
    INNER JOIN VORoles vorole ON summary.VORoleID = vorole.id
    GROUP BY
        summary.SiteID,
        summary.VOID,
        summary.GlobalUserNameID,
        summary.VOGroupID,
        summary.VORoleID,
        summary.Year,
        summary.Month;


-- -----------------------------------------------------------------------------
-- View on JobRecords
DROP VIEW IF EXISTS VJobRecords;
CREATE VIEW VJobRecords AS
    SELECT UpdateTime, site.name Site, subhost.name SubmitHost, machine.name MachineName,
           queue.name Queue, LocalJobId, LocalUserId,
           userdn.name GlobalUserName, FQAN, vos.name VO, vogroup.name VOGroup, vorole.name VORole, 
           WallDuration, CpuDuration, Processors, NodeCount, StartTime, EndTime, InfrastructureDescription, InfrastructureType,
           MemoryReal, MemoryVirtual, ServiceLevelType, ServiceLevel
    FROM JobRecords, Sites site, SubmitHosts subhost, MachineNames machine, 
    	 Queues queue, DNs userdn, VORoles vorole, VOs vos, VOGroups vogroup  
   	WHERE
        SiteID = site.id
        AND SubmitHostID = subhost.id
	    AND MachineNameID = machine.id
	    AND QueueID = queue.id
        AND GlobalUserNameID = userdn.id
        AND VORoleID = vorole.id
        AND VOID = vos.id
        AND VOGroupID = vogroup.id;


-- -----------------------------------------------------------------------------
-- View on SyncRecords
DROP VIEW IF EXISTS VSyncRecords;
CREATE VIEW VSyncRecords AS
    SELECT UpdateTime, site.name Site, subhost.name SubmitHost, NumberOfJobs, Month, Year
    FROM SyncRecords, Sites site, SubmitHosts subhost WHERE
        SiteID = site.id
	AND SubmitHostID = subhost.id;
