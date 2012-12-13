-- ------------------------------------------------------------------------------
-- CloudRecords

CREATE TABLE CloudRecords ( 
  UpdateTime TIMESTAMP, 

  RecordId VARCHAR(255) NOT NULL, 
  SiteID INT NOT NULL,                -- Foreign key

  ZoneName VARCHAR(255), 
  MachineName VARCHAR(255) NOT NULL, 

  LocalUserId VARCHAR(255),
  LocalGroupId VARCHAR(255),

  GlobalUserNameID INT NOT NULL,      -- Foreign key
  FQAN VARCHAR(255),

  Status VARCHAR(255),

  StartTime DATETIME, 
  EndTime DATETIME, 
  SuspendTime DATETIME, 
  TimeZone VARCHAR(255),

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

  PRIMARY KEY (SiteID, MachineName),

  INDEX (UpdateTime),
  INDEX (EndTime),
  INDEX (GlobalUserNameID),
  INDEX (SiteID)

);


DROP PROCEDURE IF EXISTS InsertCloudRecord;
DELIMITER //
CREATE PROCEDURE InsertCloudRecord(
  recordId VARCHAR(255), site VARCHAR(255), 
  zoneName VARCHAR(255), machineName VARCHAR(255), 
  localUserId VARCHAR(255),
  localGroupId VARCHAR(255), globalUserName VARCHAR(255), 
  fqan VARCHAR(255), status VARCHAR(255),
  startTime DATETIME, endTime DATETIME, 
  suspendTime DATETIME, timeZone VARCHAR(255),
  wallDuration INT, cpuDuration INT, 
  cpuCount INT, networkType VARCHAR(255),  networkInbound INT, 
  networkOutbound INT, memory INT, 
  disk INT, storageRecordId VARCHAR(255),
  imageId VARCHAR(255), cloudType VARCHAR(255),
  publisherDN VARCHAR(255))
BEGIN
    REPLACE INTO CloudRecords(RecordId, SiteID, ZoneName, MachineName, LocalUserId, LocalGroupId,
        GlobalUserNameID, FQAN, Status, StartTime, EndTime, SuspendTime, TimeZone,
        WallDuration, CpuDuration, CpuCount, NetworkType, NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId,
        ImageId, CloudType, PublisherDNID)
      VALUES (
        recordId, SiteLookup(site), zoneName, machineName, localUserId, localGroupId, DNLookup(globalUserName), 
        fqan, status, startTime, endTime, suspendTime, 
        timeZone, wallDuration, cpuDuration, cpuCount, networkType, networkInbound, networkOutbound, memory,
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
-- View on CloudRecords
CREATE VIEW VCloudRecords AS
    SELECT UpdateTime, RecordId, site.name SiteName, ZoneName, MachineName, 
           LocalUserId, LocalGroupId, userdn.name GlobalUserName, FQAN, Status, StartTime, EndTime,
           SuspendTime, TimeZone, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, DNs userdn WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id;

-- -----------------------------------------------------------------------------
-- View on CloudRecords
CREATE VIEW VAnonCloudRecords AS
    SELECT UpdateTime, RecordId, site.name SiteName, ZoneName, MachineName,
           LocalUserId, LocalGroupId, GlobalUserNameID, FQAN, Status, StartTime, EndTime,
           SuspendTime, TimeZone, WallDuration, CpuDuration, CpuCount, NetworkType,
           NetworkInbound, NetworkOutbound, Memory, Disk, StorageRecordId, ImageId, CloudType
    FROM CloudRecords, Sites site, DNs userdn WHERE
        SiteID = site.id
        AND GlobalUserNameID = userdn.id;

