-- This schema adds the tables necessary for IP accounting as a seperate
-- resource as part of the wider Cloud Accounting system.

-- IPRecords
CREATE TABLE IPRecords (
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  MeasurementTime DATETIME NOT NULL,
  MeasurementMonth INT NOT NULL,
  MeasurementYear INT NOT NULL,

  SiteID INT NOT NULL,
  CloudComputeServiceID INT,
  CloudType VARCHAR(255) NOT NULL,

  LocalUserId VARCHAR(255) NOT NULL,
  LocalGroupId VARCHAR(255) NOT NULL,

  GlobalUserNameID INT NOT NULL,
  FQAN VARCHAR(255) NOT NULL,
  VOID INT NOT NULL,
  VOGroupID INT NOT NULL,
  VORoleID INT NOT NULL,

  IPVersion TINYINT NOT NULL,
  IPCount INT NOT NULL,

  PublisherDNID INT NOT NULL,

  -- We want to keep one record per site, per cloud, per user, per IP version,
  -- per month/year.
  PRIMARY KEY (
    SiteID, CloudComputeServiceID, GlobalUserNameID,
    IPVersion,
    MeasurementMonth, MeasurementYear
  ),

  -- Index the table in a way similar to the CloudRecords table.
  INDEX (UpdateTime),
  INDEX (GlobalUserNameID),
  INDEX (SiteID)

);

DROP PROCEDURE IF EXISTS ReplaceIPRecord;
DELIMITER //
CREATE PROCEDURE ReplaceIPRecord(
  measurementTime DATETIME,
  measurementMonth INT,
  measurementYear INT,
  site VARCHAR(255),
  cloudComputeService VARCHAR(255),
  cloudType VARCHAR(255),
  localUserId VARCHAR(255),
  localGroupId VARCHAR(255),
  globalUserName VARCHAR(255),
  fqan VARCHAR(255),
  vo VARCHAR(255),
  voGroup VARCHAR(255),
  voRole VARCHAR(255),
  ipVersion TINYINT,
  ipCount INT,
  publisherDN VARCHAR(255)
)
BEGIN
REPLACE INTO IPRecords(
  MeasurementTime,
  MeasurementMonth,
  MeasurementYear,
  SiteID,
  CloudComputeServiceID,
  CloudType,
  LocalUserId,
  LocalGroupId,
  GlobalUserNameID,
  FQAN,
  VOID,
  VOGroupID,
  VORoleID,
  IPVersion,
  IPCount,
  PublisherDNID
)
VALUES(
  measurementTime,
  measurementMonth,
  measurementYear,
  SiteLookUp(site),
  CloudComputeServiceLookup(cloudComputeService),
  cloudType,
  localUserId,
  localGroupId,
  DNLookup(globalUserName),
  fqan,
  VOLookup(vo),
  VOGroupLookup(voGroup),
  VORoleLookup(voRole),
  ipVersion,
  ipCount,
  DNLookup(publisherDN)
);
END //
DELIMITER ;
