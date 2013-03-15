-- ------------------------------------------------------------------------------
-- CloudRecords

CREATE TABLE CloudRecords ( 
  UpdateTime TIMESTAMP, 

  VMUUID VARCHAR(255) NOT NULL, 
  SiteID INT NOT NULL,                -- Foreign key

  MachineName VARCHAR(255), 

  LocalUserId VARCHAR(255),
  LocalGroupId VARCHAR(255),

  GlobalUserNameID INT NOT NULL,      -- Foreign key
  FQAN VARCHAR(255),
  VOID INT NOT NULL,                  -- Foreign key
  VOGroupID INT NOT NULL,             -- Foreign key
  VORoleID INT NOT NULL,              -- Foreign key

  Status VARCHAR(255),

  StartTime DATETIME, 
  EndTime DATETIME, 
  SuspendDuration INT, 

  WallDuration INT, 
  CpuDuration INT, 
  CpuCount INT, 

  NetworkType VARCHAR(255),
  NetworkInbound INT, 
  NetworkOutbound INT, 
  Memory INT, 
  Disk INT, 

  StorageRecordId VARCHAR(255),
  ImageId VARCHAR(255),
  CloudType VARCHAR(255),

  PublisherDNID INT NOT NULL,	    -- Foreign key

  PRIMARY KEY (VMUUID),

  INDEX (UpdateTime),
  INDEX (GlobalUserNameID),
  INDEX (SiteID),
  INDEX (ImageID)

);


DROP PROCEDURE IF EXISTS InsertCloudRecord;
DELIMITER //
CREATE PROCEDURE InsertCloudRecord(
  VMUUID VARCHAR(255), site VARCHAR(255), 
  machineName VARCHAR(255), 
  localUserId VARCHAR(255),
  localGroupId VARCHAR(255), globalUserName VARCHAR(255), 
  fqan VARCHAR(255), vo VARCHAR(255), 
  voGroup VARCHAR(255), voRole VARCHAR(255), status VARCHAR(255),
  startTime DATETIME, endTime DATETIME, 
  suspendDuration INT,
  wallDuration INT, cpuDuration INT, 
  cpuCount INT, networkType VARCHAR(255),  networkInbound INT, 
  networkOutbound INT, memory INT, 
  disk INT, storageRecordId VARCHAR(255),
  imageId VARCHAR(255), cloudType VARCHAR(255),
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO CloudRecords(VMUUID, SiteID, MachineName, LocalUserId, LocalGroupId,
        GlobalUserNameID, FQAN, VOID, VOGroupID, VORoleID, Status, StartTime, EndTime, SuspendDuration,
        WallDuration, CpuDuration, CpuCount, NetworkType, NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType, PublisherDNID)
      VALUES (
        VMUUID, SiteLookup(site), machineName, localUserId, localGroupId, DNLookup(globalUserName), 
        fqan, VOLookup(vo),
        VOGroupLookup(voGroup), VORoleLookup(voRole), status, startTime, endTime, suspendDuration, 
        wallDuration, cpuDuration, cpuCount, networkType, networkInbound, networkOutbound, memory,
        disk, storageRecordId, imageId, cloudType, DNLookup(publisherDN)
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

CREATE TABLE Sites (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
 ,  name VARCHAR(255) NOT NULL

 , INDEX(name)

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

CREATE TABLE DNs (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
 ,  name VARCHAR(255) NOT NULL

 ,  INDEX(name)

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
-- View on CloudRecords
CREATE VIEW VCloudRecords AS
    SELECT UpdateTime, VMUUID, site.name SiteName, MachineName, 
           LocalUserId, LocalGroupId, userdn.name GlobalUserName, FQAN, vo.name VO, 
           vogroup.name VOGroup, vorole.name VORole,
           Status, StartTime, EndTime,
           SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, DNs userdn, VOs vo, VOGroups vogroup, VORoles vorole WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id
        AND VOID = vo.id
        AND VOGroupID = vogroup.id
        AND VORoleID = vorole.id;

-- -----------------------------------------------------------------------------
-- View on CloudRecords
CREATE VIEW VAnonCloudRecords AS
    SELECT UpdateTime, VMUUID, site.name SiteName, MachineName,
           LocalUserId, LocalGroupId, GlobalUserNameID, FQAN, VO,  Status, StartTime, EndTime,
           SuspendDuration, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, DNs userdn WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id;

