/* This schema is an addition to client.sql for application accounting */

-- ------------------------------------------------------------------------------
-- ApplicationRecords
DROP TABLE IF EXISTS ApplicationRecords;
CREATE TABLE ApplicationRecords (
  SiteID        INT          NOT NULL, -- foreign key
  MachineNameID INT          NOT NULL, -- foreign key
  BinaryPath    VARCHAR(255) NOT NULL, -- TODO Change to a lookup
  LocalUserID   VARCHAR(20),
  StartTime     DATETIME     NOT NULL,
  EndTime       DATETIME     NOT NULL,
  Status        INT,                   -- 0 for unprocessed, 1 for local job, 2 for grid job
  
  PRIMARY KEY(MachineNameID, BinaryPath, EndTime)
);

DROP PROCEDURE IF EXISTS InsertApplicationRecord;
DELIMITER //
CREATE PROCEDURE InsertApplicationRecord(
  site           VARCHAR(255),
  machineName    VARCHAR(255),
  binaryPath     VARCHAR(255),
  localUserId    VARCHAR(20),
  startTime      DATETIME,
  endTime        DATETIME)
BEGIN
        INSERT IGNORE INTO ApplicationRecords(SiteID, MachineNameID, BinaryPath, LocalUserID, StartTime, EndTime, Status)
        VALUES (SiteLookup(site), MachineNameLookup(machineName), binaryPath, localUserId, startTime, endTime, 0);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ReplaceApplicationRecord;
DELIMITER //
CREATE PROCEDURE ReplaceApplicationRecord(
  site           VARCHAR(255),
  machineName    VARCHAR(255),
  binaryPath     VARCHAR(255),
  localUserId    VARCHAR(20),
  startTime      DATETIME,
  endTime        DATETIME)
BEGIN
        REPLACE INTO ApplicationRecords(SiteID, MachineNameID, BinaryPath, LocalUserID, StartTime, EndTime, Status)
        VALUES (SiteLookup(site), MachineNameLookup(machineName), binaryPath, localUserId, startTime, endTime, 0);
END //
DELIMITER ;

-- View on ApplicationRecords
/*DROP VIEW IF EXISTS VApplicationRecords;
CREATE VIEW VApplicationRecords AS
    SELECT site.name Site, subhost.name SubmitHost, machine.name MachineName,
           LocalJobId, LocalUserId,
           StartTime, EndTime
    FROM ApplicationRecords, Sites site, SubmitHosts subhost, MachineNames machine
   	WHERE
        SiteID = site.id
        AND SubmitHostID = subhost.id
	    AND MachineNameID = machine.id
	    AND QueueID = queue.id;*/

-- -----------------------------------------------------------------------------
