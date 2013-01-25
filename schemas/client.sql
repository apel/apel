  
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
  NodeCount INT UNSIGNED, 
  Processors INT UNSIGNED, 
  
  MemoryReal BIGINT UNSIGNED,
  MemoryVirtual BIGINT UNSIGNED,
  
  StartTime DATETIME NOT NULL, 
  EndTime DATETIME NOT NULL, 
  EndYear INT,                        -- Used for indexing
  EndMonth INT,	                      -- Used for indexing

  InfrastructureDescription VARCHAR(100),
  InfrastructureType VARCHAR(20),

  ServiceLevelType VARCHAR(50) NOT NULL,
  ServiceLevel DECIMAL(10,3) NOT NULL,

  PublisherDNID INT NOT NULL,        -- Foreign key

  PRIMARY KEY (MachineNameID, LocalJobID, EndTime),
  
  -- index for SummariseJobs() procedure. 
  -- Try to reuse this index as much as you can
  INDEX SummaryIdx (SiteID, VOID, GlobalUserNameID, VOGroupID, VORoleID, 
        EndYear, EndMonth, InfrastructureType, SubmitHostID, ServiceLevelType, ServiceLevel, 
	    NodeCount, Processors, EndTime, WallDuration, CpuDuration)

);


-- ------------------------------------------------------------------------------
-- EventRecords
DROP TABLE IF EXISTS EventRecords;
CREATE TABLE EventRecords (
  SiteID          INT             NOT NULL, -- foreign key
  JobName         VARCHAR(60)     NOT NULL,
  LocalUserID     VARCHAR(20),
  LocalUserGroup  VARCHAR(20),
  WallDuration    INT,
  CpuDuration     INT,
  StartTime       DATETIME        NOT NULL,
  EndTime         DATETIME        NOT NULL,
  Infrastructure  VARCHAR(100),
  MachineNameID   INT             NOT NULL, -- foreign key
  QueueID         INT             NOT NULL, -- foreign key
  MemoryReal      BIGINT,
  MemoryVirtual   BIGINT,
  Processors      INT,
  NodeCount       INT,
  Status          INT,                      -- 0 for unprocessed, 1 for local job, 2 for grid job
  
  PRIMARY KEY(MachineNameID, JobName, EndTime),
  INDEX EventJoinIdx (SiteID, JobName)
);

DROP PROCEDURE IF EXISTS InsertEventRecord;
DELIMITER //
CREATE PROCEDURE InsertEventRecord(
  site       VARCHAR(255),
  jobName        VARCHAR(60),
  localUserId    VARCHAR(20),
  localUserGroup VARCHAR(20),
  wallDuration   INT,
  cpuDuration    INT,
  startTime      DATETIME,
  endTime        DATETIME,
  infrastructure VARCHAR(100),
  machineName    VARCHAR(255),
  queue          VARCHAR(100),
  memoryReal     BIGINT,
  memoryVirtual  BIGINT,
  processors     INT,
  nodeCount      INT)
BEGIN
        INSERT IGNORE INTO EventRecords(SiteID, JobName, LocalUserID, LocalUserGroup, WallDuration,
                                  CpuDuration, StartTime, EndTime, Infrastructure, MachineNameID, QueueID, MemoryReal, MemoryVirtual, Processors, NodeCount, Status)
        VALUES (SiteLookup(site), jobName, localUserId, localUserGroup, wallDuration, cpuDuration, 
          startTime, endTime, infrastructure, MachineNameLookup(machineName), QueueLookup(queue), memoryReal, memoryVirtual, processors, nodeCount, 0);
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- BlahdRecords
DROP TABLE IF EXISTS BlahdRecords;
CREATE TABLE BlahdRecords (
  TimeStamp                   DATETIME     NOT NULL DEFAULT "0000-00-00 00:00:00",
  GlobalUserNameID            INT          NOT NULL, -- foreign key
  FQAN                        VARCHAR(255) DEFAULT NULL,
  VOID                        INT          NOT NULL, -- foreign key
  VOGroupID                   INT          NOT NULL, -- foreign key
  VORoleID                    INT          NOT NULL, -- foreign key
  CEID                        INT          NOT NULL, -- foreign key
  GlobalJobId                 VARCHAR(255) DEFAULT NULL,
  LrmsId                      VARCHAR(255) DEFAULT NULL,
  SiteID                      INT          NOT NULL, -- foreign key
  ValidFrom                   DATETIME     DEFAULT NULL,
  ValidUntil                  DATETIME     DEFAULT NULL,
  Processed                   INT          DEFAULT NULL,

  PRIMARY KEY(TimeStamp, SiteId, LrmsId, CEID),
  INDEX BlahdJoinIdx (ValidFrom, ValidUntil, SiteID, LrmsId)
);

DROP PROCEDURE IF EXISTS InsertBlahdRecord;
DELIMITER //
CREATE PROCEDURE InsertBlahdRecord(
  timeStamp                   DATETIME,
  globalUserName              VARCHAR(255),
  fullyQualifiedAttributeName VARCHAR(255),
  vo                          VARCHAR(255),
  VOGroup                     VARCHAR(255),
  VORole                      VARCHAR(255),
  ce                          VARCHAR(255),
  globalJobId                 VARCHAR(255),
  lrmsId                      VARCHAR(255),
  site                        VARCHAR(50) ,
  validFrom                   DATETIME,
  validUntil                  DATETIME, 
  processed                   INT)
BEGIN
  INSERT IGNORE INTO BlahdRecords (TimeStamp , GlobalUserNameID, FQAN, VOID, VOGroupID, 
                             VORoleID, CEID, GlobalJobId, LrmsId, SiteID, ValidFrom, ValidUntil,
                             Processed)
  VALUES (timeStamp, DNLookup(globalUserName), fullyQualifiedAttributeName, VOLookup(vo), VOGroupLookup(VOGroup), 
          VORoleLookup(VORole), SubmitHostLookup(ce), globalJobId, lrmsId, SiteLookup(site), 
          validFrom, validUntil, processed);
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- SpecRecords
DROP TABLE IF EXISTS SpecRecords;
CREATE TABLE SpecRecords(
  SiteID        INT NOT NULL,
  CEID              INT NOT NULL,
  StartTime         DATETIME,
  StopTime          DATETIME,
  ServiceLevelType  VARCHAR(50) NOT NULL,
  ServiceLevel      DECIMAL(10,3),
  
  PRIMARY KEY(SiteID, CEID, StartTime, ServiceLevelType)
);

DROP FUNCTION IF EXISTS SpecLookup;
DELIMITER //
CREATE FUNCTION SpecLookup(
  _site             VARCHAR(255),
  _ceID              VARCHAR(255),
  _serviceLevelType  VARCHAR(50),
  _lookupTime        DATETIME) RETURNS DECIMAL(10,3) READS SQL DATA
BEGIN
    DECLARE result	 DECIMAL(10,3);
    SELECT ServiceLevel 
    FROM SpecRecords
    WHERE 
        StartTime < _lookupTime
    AND
        StopTime is NULL
    AND
        CEID = SubmitHostLookup(_ceID)
    AND
        SiteID = SiteLookup(_site)
    AND
        ServiceLevelType = _serviceLevelType
    INTO result;
    RETURN result;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS SpecUpdate;
DELIMITER //
CREATE PROCEDURE SpecUpdate (
  _site          VARCHAR(255),
  _ce                VARCHAR(255),
  _serviceLevelType  VARCHAR(50),
  _startTime         DATETIME,
  _new_value         DECIMAL(10,3))
BEGIN
    UPDATE SpecRecords
    SET StopTime = now()
    WHERE
        SiteID = SiteLookup(_site)
    AND
        CEID = SubmitHostLookup(_ce)
    AND
        ServiceLevelType = _serviceLevelType
    AND
        StopTime is NULL;
    
    INSERT INTO SpecRecords (SiteID, CEID, StartTime, StopTime, ServiceLevelType, ServiceLevel)
    VALUES (SiteLookup(_site), SubmitHostLookup(_ce), _startTime, NULL, _serviceLevelType, _new_value);
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- Procedure for converting EventRecords + BlahdRecords into JobRecords
DROP PROCEDURE IF EXISTS JoinJobRecords;
DELIMITER //
CREATE PROCEDURE JoinJobRecords()
BEGIN
    DECLARE procstart DATETIME;
    DECLARE apeldn INT;
    
    SET procstart = NOW();
    SET apeldn = DNLookup("apelclient");

    REPLACE INTO JobRecords (
      UpdateTime,
      SiteID,                -- Foreign key
      SubmitHostID,          -- Foreign key
      MachineNameID,         -- Foreign key
      QueueID,               -- Foreign key
      LocalJobId,
      LocalUserId, 
      GlobalUserNameID,      -- Foreign key
      FQAN,
      VOID,                  -- Foreign key
      VOGroupID,             -- Foreign key
      VORoleID,              -- Foreign key
      WallDuration, 
      CpuDuration, 
      Processors, 
      NodeCount, 
      StartTime, 
      EndTime, 
      InfrastructureDescription,
      InfrastructureType,
      MemoryReal,
      MemoryVirtual,
      ServiceLevelType,
      ServiceLevel,
      PublisherDNID,
      EndYear,
      EndMonth)
-- as long as we are not joining records from external databases we can do it with
-- raw IDs
    SELECT         
        procstart,                                         -- JobRecord.UpdateTime
        EventRecords.SiteID as SiteID,                     -- JobRecord.Site
        BlahdRecords.CEID as SubmitHostID,                 -- JobRecord.SubmitHost
        EventRecords.MachineNameID as MachineNameID,       -- JobRecord.MachineName
        EventRecords.QueueID as QueueID,                   -- JobRecord.Queue
        EventRecords.JobName as LocalJobId,                -- JobRecord.LocalJobId
        EventRecords.LocalUserID as LocalUserId,           -- JobRecord.LocalUserId
        BlahdRecords.GlobalUserNameID as GlobalUserNameID, -- JobRecord.GlobalUserName 
        BlahdRecords.FQAN as FQAN,    
        BlahdRecords.VOID as VOID,                         -- JobRecord.VOID        
        BlahdRecords.VOGroupID as VOGroupID,               -- JobRecord.VOGroup        
        BlahdRecords.VORoleID as VORoleID,                 -- JobRecord.VORole
        EventRecords.WallDuration as WallDuration,         -- JobRecord.WallDuration
        EventRecords.CpuDuration as CpuDuration,           -- JobRecord.CpuDuration        
        EventRecords.Processors as Processors,             -- JobRecord.Processors
        EventRecords.NodeCount as NodeCount,               -- JobRecord.NodeCount
        EventRecords.StartTime as StartTime,               -- JobRecord.StartTime
        EventRecords.EndTime as EndTime,                   -- JobRecord.EndTime
        EventRecords.Infrastructure as InfrastructureDescription,     -- JobRecord.Infrastructure
        "grid",                               	       	   -- JobRecord.InfrastructureType
        EventRecords.MemoryReal as MemoryReal,             -- JobRecord.MemoryReal
        EventRecords.MemoryVirtual as MemoryVirtual,       -- JobRecord.MemoryVirtual
        SpecRecords.ServiceLevelType as ServiceLevelType,  
        SpecRecords.ServiceLevel as ServiceLevel,          
        apeldn,                            -- JobRecords.PublisherDN
        YEAR(EventRecords.EndTime),
        MONTH(EventRecords.EndTime)
    FROM SpecRecords 
    INNER JOIN EventRecords ON ((SpecRecords.StopTime > EventRecords.EndTime
                             OR 
                             SpecRecords.StopTime IS NULL)
                             AND
                             SpecRecords.StartTime <= EventRecords.EndTime)
                             AND SpecRecords.SiteID = EventRecords.SiteID
    INNER JOIN BlahdRecords ON BlahdRecords.ValidFrom <= EventRecords.EndTime AND
                             BlahdRecords.ValidUntil > EventRecords.EndTime AND
                             EventRecords.SiteID = BlahdRecords.SiteID AND EventRecords.JobName = BlahdRecords.LrmsId
                             AND SpecRecords.SiteID = BlahdRecords.SiteID AND SpecRecords.CEID = BlahdRecords.CEID
    WHERE
        EventRecords.Status != 2;  -- all events which are not already grid jobs
        
    UPDATE EventRecords, JobRecords
    SET Status = 2 
    WHERE EventRecords.MachineNameID = JobRecords.MachineNameID
        AND EventRecords.JobName = JobRecords.LocalJobId 
        AND EventRecords.EndTime = JobRecords.EndTime 
        AND JobRecords.UpdateTime >= procstart;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS LocalJobs;
DELIMITER //
CREATE PROCEDURE LocalJobs()
BEGIN
    DECLARE procstart DATETIME;
    DECLARE submithostid INT;
    DECLARE vogroupid INT;
    DECLARE voroleid INT;
    DECLARE dnnoneid INT;
    DECLARE dnlocalid INT;
	
    SET procstart = NOW();
    SET submithostid = SubmitHostLookup("None");
    SET vogroupid = VOGroupLookup("None");
    SET voroleid = VORoleLookup("None");
    SET dnnoneid = DNLookup("None");
    SET dnlocalid = DNLookup("local");
	
    REPLACE INTO JobRecords (
      UpdateTime,
      SiteID,                -- Foreign key
      SubmitHostID,          -- Foreign key
      MachineNameID,         -- Foreign key
      QueueID,               -- Foreign key
      LocalJobId,
      LocalUserId,
      GlobalUserNameID,      -- Foreign key
      FQAN,
      VOID,                  -- Foreign key
      VOGroupID,             -- Foreign key
      VORoleID,              -- Foreign key
      WallDuration,
      CpuDuration,
      Processors,
      NodeCount,
      StartTime,
      EndTime,
      InfrastructureDescription,
      InfrastructureType,
      MemoryReal,
      MemoryVirtual,
      ServiceLevelType,
      ServiceLevel,
      PublisherDNID,
      EndYear,
      EndMonth)
    SELECT 
        procstart,
        EventRecords.SiteID,
        submithostid,                                   -- JobRecords.SubmitHostID
        MachineNameID,                                  -- JobRecords.MachineName
        QueueID,                                        -- JobRecords.Queue
        JobName,                                        -- JobRecords.LocalJobId
        LocalUserId,                                    -- JobRecords.LocalUserId
        dnnoneid,                                       -- JobRecords.GlobalUserName 
        NULL,                                           -- JobRecords.FQAN
        VOLookup(IFNULL(EventRecords.LocalUserGroup, "None")),   -- JobRecords.VOID
        vogroupid,                                      -- JobRecords.VOGroup        
        voroleid,                                       -- JobRecords.VORole
        WallDuration,                                   -- JobRecords.WallDuration
        CpuDuration,                                    -- JobRecords.CpuDuration        
        Processors,                                     -- JobRecords.Processors
        NodeCount,                                      -- JobRecords.NodeCount
        EventRecords.StartTime,                         -- JobRecords.StartTime
        EventRecords.EndTime,                           -- JobRecords.EndTime
        Infrastructure,
        "local",
        MemoryReal,                                     -- JobRecords.MemoryReal
        MemoryVirtual,                                  -- JobRecords.MemoryVirtual
        SpecRecords.ServiceLevelType,
        SpecRecords.ServiceLevel,
        dnlocalid,                                      -- JobRecords.PublisherDN
        YEAR(EventRecords.EndTime),
        MONTH(EventRecords.EndTime)
	FROM SpecRecords 
    INNER JOIN EventRecords ON ((SpecRecords.StopTime > EventRecords.EndTime
                             OR 
                             SpecRecords.StopTime IS NULL)
                             AND
                             SpecRecords.StartTime <= EventRecords.EndTime)
                             AND SpecRecords.SiteID = EventRecords.SiteID
    INNER JOIN MachineNames ON EventRecords.MachineNameID = MachineNames.id
    INNER JOIN SubmitHosts ON SpecRecords.CEID = SubmitHosts.id 
                             AND SubmitHosts.name = MachineNames.name
    WHERE Status = 0; 
    
    UPDATE EventRecords, JobRecords
    SET Status = 1 
    WHERE EventRecords.MachineNameID = JobRecords.MachineNameID
        AND EventRecords.JobName = JobRecords.LocalJobId 
        AND EventRecords.EndTime = JobRecords.EndTime 
        AND JobRecords.UpdateTime >= procstart;
        
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

DROP PROCEDURE IF EXISTS SummariseJobs;
DELIMITER //
CREATE PROCEDURE SummariseJobs()
BEGIN
    REPLACE INTO SuperSummaries(SiteID, Month, Year, GlobalUserNameID, VOID, 
        VOGroupID, VORoleID, SubmitHostID, InfrastructureType, ServiceLevelType, ServiceLevel, 
        NodeCount, Processors, EarliestEndTime, 
        LatestEndTime, WallDuration, CpuDuration, NumberOfJobs)
    SELECT SiteID, 
    EndMonth AS Month, EndYear AS Year, 
        GlobalUserNameID, VOID, VOGroupID, VORoleID, SubmitHostID, InfrastructureType, 
        ServiceLevelType, ServiceLevel, NodeCount, Processors,
    MIN(EndTime) AS EarliestEndTime, 
    MAX(EndTime) AS LatestEndTime,
    SUM(WallDuration) AS SumWCT, 
    SUM(CpuDuration) AS SumCPU, 
    COUNT(*) AS Njobs
    FROM JobRecords 
    GROUP BY SiteID, VOID, GlobalUserNameID, VOGroupID, VORoleID, EndYear, EndMonth, InfrastructureType, 
             SubmitHostID, ServiceLevelType, ServiceLevel, NodeCount, Processors;
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
-- ProcessedFiles
DROP TABLE IF EXISTS ProcessedFiles;
CREATE TABLE ProcessedFiles (
  HostName    VARCHAR(255),
  FileName    VARCHAR(255),
  Hash        VARCHAR(64),
  StopLine    INT,
  Parsed      INT,
  PRIMARY KEY (HostName,Hash)
  );

DROP PROCEDURE IF EXISTS CleanProcessedFiles;
DELIMITER // 
CREATE PROCEDURE CleanProcessedFiles(
  hostName    VARCHAR(255))
BEGIN
  DELETE FROM ProcessedFiles where HostName like hostName;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS InsertProcessedFile;
DELIMITER // 
CREATE PROCEDURE InsertProcessedFile(
  hostName VARCHAR(255),
  fileName VARCHAR(255),
  hash     VARCHAR(64),
  stopLine INT,
  parsed   INT)
BEGIN
  REPLACE INTO ProcessedFiles(HostName, FileName, Hash, StopLine, Parsed)
  VALUES (hostName, fileName, hash, stopLine, parsed);
END //
DELIMITER ;

-- Sync records view
DROP VIEW IF EXISTS VSyncRecords;
CREATE VIEW VSyncRecords as 
    SELECT     
        site.name as Site, host.name as SubmitHost, sum(NumberOfJobs) as NumberOfJobs, Month, Year
    FROM SuperSummaries, Sites site, SubmitHosts host
    WHERE site.id = SuperSummaries.SiteID
    AND host.id = SuperSummaries.SubmitHostID
    GROUP BY Site, SubmitHost, Month, Year;

-- -----------------------------------------------------------------------------
-- View on SpecRecords
DROP VIEW IF EXISTS VSpecRecords;
CREATE VIEW VSpecRecords AS
    SELECT site.name as Site, host.name as CE, StartTime, StopTime, ServiceLevelType, ServiceLevel
    FROM
        Sites site, SubmitHosts host, SpecRecords
    WHERE
        site.id = SpecRecords.SiteID AND
        host.id = SpecRecords.CEID;

-- -----------------------------------------------------------------------------
-- View on SuperSummaries
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
    FROM SuperSummaries, 
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
-- View on ProcessedFiles
DROP VIEW IF EXISTS VProcessedFiles;
CREATE VIEW VProcessedFiles AS
    SELECT HostName, FileName, Hash, StopLine, Parsed FROM ProcessedFiles;

