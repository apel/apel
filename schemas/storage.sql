-- ------------------------------------------------------------------------------
-- StorageSystems
DROP TABLE IF EXISTS StorageSystems;
CREATE TABLE StorageSystems (
    id                      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(255),

    INDEX(name)
);

DROP FUNCTION IF EXISTS StorageSystemLookup;
DELIMITER //
CREATE FUNCTION StorageSystemLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM StorageSystems WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO StorageSystems(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- Sites
DROP TABLE IF EXISTS Sites;
CREATE TABLE Sites (
    id                      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(255),

    INDEX(name)
);

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


-- ------------------------------------------------------------------------------
-- StorageShares
DROP TABLE IF EXISTS StorageShares;
CREATE TABLE StorageShares (
    id                      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(255),
    INDEX(name)
);

DROP FUNCTION IF EXISTS StorageShareLookup;
DELIMITER //
CREATE FUNCTION StorageShareLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM StorageShares WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO StorageShares(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- StorageMedia
DROP TABLE IF EXISTS StorageMedia;
CREATE TABLE StorageMedia (
    id                      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(255),
    INDEX(name)
);

DROP FUNCTION IF EXISTS StorageMediaLookup;
DELIMITER //
CREATE FUNCTION StorageMediaLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM StorageMedia WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO StorageMedia(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- StorageClasses
DROP TABLE IF EXISTS StorageClasses;
CREATE TABLE StorageClasses(
    id                      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(255),
    INDEX(name)
);

DROP FUNCTION IF EXISTS StorageClassLookup;
DELIMITER //
CREATE FUNCTION StorageClassLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM StorageClasses WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO StorageClasses(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- UserIdentities
DROP TABLE IF EXISTS UserIdentities;
CREATE TABLE UserIdentities (
    id                      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(255),
    INDEX(NAME)
);

DROP FUNCTION IF EXISTS UserIdentityLookup;
DELIMITER //
CREATE FUNCTION UserIdentityLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM UserIdentities WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO UserIdentities(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- Groups
DROP TABLE IF EXISTS Groups;
CREATE TABLE Groups (
    id                      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(255),
    INDEX (name)
);

DROP FUNCTION IF EXISTS GroupLookup;
DELIMITER //
CREATE FUNCTION GroupLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM Groups WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO Groups(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- SubGroups
DROP TABLE IF EXISTS SubGroups;
CREATE TABLE SubGroups (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(255),
    INDEX (name)
);

DROP FUNCTION IF EXISTS SubGroupLookup;
DELIMITER //
CREATE FUNCTION SubGroupLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM SubGroups WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO SubGroups(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- Roles
DROP TABLE IF EXISTS Roles;
CREATE TABLE Roles (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(255),
    INDEX (name)
);

DROP FUNCTION IF EXISTS RoleLookup;
DELIMITER //
CREATE FUNCTION RoleLookup(lookup VARCHAR(255)) RETURNS INTEGER DETERMINISTIC
BEGIN
    DECLARE result INTEGER;
    SELECT id FROM Roles WHERE name=lookup INTO result;
    IF result IS NULL THEN
        INSERT INTO Roles(name) VALUES (lookup);
        SET result=LAST_INSERT_ID();
    END IF;
RETURN result;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- GroupAttributes
DROP TABLE IF EXISTS GroupAttributes;
CREATE TABLE GroupAttributes (
    StarRecordID            VARCHAR(255) NOT NULL,
    AttributeType           VARCHAR(255),
    AttributeValue          VARCHAR(255),
    PRIMARY KEY(StarRecordID, AttributeType)
    );

DROP PROCEDURE IF EXISTS ReplaceGroupAttribute;
DELIMITER //
CREATE PROCEDURE ReplaceGroupAttribute(
    starRecordID            VARCHAR(255),
    attributeType           VARCHAR(255),
    attributeValue          VARCHAR(255)
    )
BEGIN
    REPLACE INTO GroupAttributes(StarRecordID, AttributeType, AttributeValue)
    VALUES (starRecordID, attributeType, attributeValue);
END //
DELIMITER ;


-- ------------------------------------------------------------------------------
-- StarRecords
DROP TABLE IF EXISTS StarRecords;
CREATE TABLE StarRecords (
    RecordId          VARCHAR(255) NOT NULL PRIMARY KEY,
    CreateTime              DATETIME NOT NULL,
    StorageSystemID         INT NOT NULL,
    SiteID                  INT NOT NULL,
    StorageShareID          INT NOT NULL,
    StorageMediaID          INT NOT NULL,
    StorageClassID          INT NOT NULL,
    FileCount               INTEGER,
    DirectoryPath           VARCHAR(255),
    LocalUser               VARCHAR(255),
    LocalGroup              VARCHAR(255),
    UserIdentityID          INT NOT NULL,
    GroupID                 INT NOT NULL,
    SubGroupID              INT NOT NULL,
    RoleID                  INT NOT NULL,
    StartTime               DATETIME NOT NULL,
    EndTime                 DATETIME NOT NULL,
    ResourceCapacityUsed    BIGINT NOT NULL,
    LogicalCapacityUsed     BIGINT,
    ResourceCapacityAllocated BIGINT,

    INDEX(StorageSystemID),
    INDEX(StorageShareID),
    INDEX(StorageMediaID),
    INDEX(StorageClassID),
    INDEX(UserIdentityID),
    INDEX(GroupID)

);


DROP PROCEDURE IF EXISTS ReplaceStarRecord;
DELIMITER //
CREATE PROCEDURE ReplaceStarRecord(
    recordId                VARCHAR(255),
    createTime              DATETIME,
    storageSystem           VARCHAR(255),
    site                    VARCHAR(255),
    storageShare            VARCHAR(255),
    storageMedia            VARCHAR(255),
    storageClass            VARCHAR(255),
    fileCount               INTEGER,
    directoryPath           VARCHAR(255),
    localUser               VARCHAR(255),
    localGroup              VARCHAR(255),
    userIdentity            VARCHAR(255),
    groupName               VARCHAR(255),
    subGroupName            VARCHAR(255),
    roleName                VARCHAR(255),
    startTime               DATETIME,
    endTime                 DATETIME,
    resourceCapacityUsed    BIGINT,
    logicalCapacityUsed     BIGINT,
    resourceCapacityAllocated BIGINT
    )
BEGIN
    REPLACE INTO StarRecords(RecordId,
        CreateTime,
        StorageSystemID,
        SiteID,
        StorageShareID,
        StorageMediaID,
        StorageClassID,
        FileCount,
        DirectoryPath,
        LocalUser,
        LocalGroup,
        UserIdentityID,
        GroupID,
        SubGroupID,
        RoleID,
        StartTime,
        EndTime,
        ResourceCapacityUsed,
        LogicalCapacityUsed,
        ResourceCapacityAllocated)
    VALUES (
        recordId,
        createTime,
        StorageSystemLookup(storageSystem),
        SiteLookup(site),
        StorageShareLookup(storageShare),
        StorageMediaLookup(storageMedia),
        StorageClassLookup(storageClass),
        fileCount,
        directoryPath,
        localUser,
        localGroup,
        UserIdentityLookup(userIdentity),
        GroupLookup(groupName),
        SubGroupLookup(subGroupName),
        RoleLookup(roleName),
        startTime,
        endTime,
        resourceCapacityUsed,
        logicalCapacityUsed,
        resourceCapacityAllocated
        );
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- VStarRecords
DROP VIEW IF EXISTS VStarRecords;

CREATE VIEW VStarRecords AS
SELECT CreateTime,
       RecordId,
       StorageSystems.name AS StorageSystem,
       Sites.name AS Site,
       StorageShares.name AS StorageShare,
       StorageMedia.name AS StorageMedia,
       StorageClasses.name AS StorageClass,
       FileCount,
       DirectoryPath,
       LocalUser,
       LocalGroup,
       UserIdentities.name AS UserIdentity,
       Groups.name AS `Group`,
       Roles.name AS `Role`,
       SubGroups.name AS SubGroup,
       StartTime,
       EndTime,
       ResourceCapacityUsed,
       LogicalCapacityUsed,
       ResourceCapacityAllocated
FROM StarRecords, StorageSystems, Sites, StorageShares,
     StorageMedia, StorageClasses, UserIdentities, Groups,
     SubGroups, Roles
WHERE StarRecords.StorageSystemID = StorageSystems.id
  AND StarRecords.SiteID = Sites.id
  AND StarRecords.StorageShareID = StorageShares.id
  AND StarRecords.StorageMediaID = StorageMedia.id
  AND StarRecords.StorageClassID = StorageClasses.id
  AND StarRecords.UserIdentityID = UserIdentities.id
  AND StarRecords.GroupID = Groups.id
  AND StarRecords.SubGroupID = SubGroups.id
  AND StarRecords.RoleID = Roles.id;

-- -----------------------------------------------------------------------------
-- Summaries
DROP TABLE IF EXISTS DaySummaries;
CREATE TABLE DaySummaries (
  Site                        VARCHAR(255),
  StorageSystem               VARCHAR(255),
  StorageShare                VARCHAR(255),
  StorageMedia                VARCHAR(255),
  DirectoryPath               VARCHAR(255),
  `Group`                     VARCHAR(255),
  EndTime                     DATETIME NOT NULL,
  Month                       INTEGER NOT NULL,
  Year                        INTEGER NOT NULL,
  FileCount                   INTEGER,
  ResourceCapacityUsed        BIGINT NOT NULL,
  LogicalCapacityUsed         BIGINT,
  ResourceCapacityAllocated   BIGINT,
  PRIMARY KEY (Site, StorageSystem, StorageShare, StorageMedia, DirectoryPath,
               `Group`, EndTime, Month, Year)
);




DROP PROCEDURE IF EXISTS DailySummary;
DELIMITER //
CREATE PROCEDURE DailySummary()
BEGIN
   REPLACE INTO DaySummaries(Site, StorageSystem, StorageShare, StorageMedia,
   DirectoryPath, `Group`, EndTime, Month, Year, FileCount, ResourceCapacityUsed,
   LogicalCapacityUsed, ResourceCapacityAllocated)
   SELECT Site,
          StorageSystem,
          StorageShare,
          StorageMedia,
          DirectoryPath,
          `Group`,
          EndTime,
          MONTH(EndTime),
          YEAR(EndTime),
          SUM(FileCount),
          SUM(ResourceCapacityUsed),
          SUM(LogicalCapacityUsed),
          SUM(ResourceCapacityAllocated)
   FROM VStarRecords
   Group BY 1,2,3,4,5,6,7;
END //
