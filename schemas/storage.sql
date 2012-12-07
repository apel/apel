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

DROP FUNCTION IF EXISTS UserIdentitiesLookup;
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
-- GroupAttributes
DROP TABLE IF EXISTS GroupAttributes;
CREATE TABLE GroupAttributes (
-- TODO: RecordIdentity as VARCHAR?!
    StarRecordID            VARCHAR(255) NOT NULL,
    AttributeType           VARCHAR(255),
    AttributeValue          VARCHAR(255),
    PRIMARY KEY(StarRecordID, AttributeType)
    );

DROP PROCEDURE IF EXISTS InsertGroupAttribute;
DELIMITER //
CREATE PROCEDURE InsertGroupAttribute(
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
-- TODO: RecordIdentity as VARCHAR!?
    RecordIdentity          VARCHAR(255) NOT NULL PRIMARY KEY,
    CreateTime              TIMESTAMP NOT NULL,
-- normalise me! [DONE]
    StorageSystemID         INT NOT NULL,
-- normalise me! [DONE]
    StorageShareID          INT NOT NULL,
-- normalise me! [DONE]
    StorageMediaID          INT NOT NULL,
-- normalise me! [DONE]
    StorageClassID          INT NOT NULL,
    FileCount               INTEGER,
    DirectoryPath           VARCHAR(255),
    LocalUser               VARCHAR(255),
    LocalGroup              VARCHAR(255),
-- normalize me! [DONE]
    UserIdentityID          INT NOT NULL,
-- normalize me! [DONE]
    GroupID                 INT NOT NULL,
    MeasureTime             TIMESTAMP NOT NULL,
    ValidDuration           INTEGER NOT NULL,
    ResourceCapacityUsed    BIGINT NOT NULL,
    LogicalCapacityUsed     BIGINT NOT NULL,

    INDEX(StorageSystemID),
    INDEX(StorageShareID),
    INDEX(StorageMediaID),
    INDEX(StorageClassID),
    INDEX(UserIdentityID),
    INDEX(GroupID)

);

-- WORK IN PROGRESS !!!

DROP PROCEDURE IF EXISTS InsertStarRecord;
DELIMITER //
CREATE PROCEDURE InsertStarRecord(
    recordIdentity          VARCHAR(255),
    createTime              TIMESTAMP,
    storageSystem           VARCHAR(255),
    storageShare            VARCHAR(255),
    storageMedia            VARCHAR(255),
    storageClass            VARCHAR(255),
    fileCount               INTEGER,
    directoryPath           VARCHAR(255),
    localUser               VARCHAR(255),
    localGroup              VARCHAR(255),
    userIdentity            VARCHAR(255),
    groupName               VARCHAR(255),
    measureTime             TIMESTAMP,
    validDuration           INTEGER,
    resourceCapacityUsed    BIGINT,
    logicalCapacityUsed     BIGINT
    )
BEGIN
    REPLACE INTO StarRecords(RecordIdentity, 
        CreateTime,
        StorageSystemID,
        StorageShareID,
        StorageMediaID,
        StorageClassID,
        FileCount,
        DirectoryPath,
        LocalUser,
        LocalGroup,
        UserIdentityID,
        GroupID,
        MeasureTime,
        ValidDuration,
        ResourceCapacityUsed,
        LogicalCapacityUsed)
    VALUES (
        recordIdentity,
        createTime,
        StorageSystemLookup(storageSystem),
        StorageShareLookup(storageShare),
        StorageMediaLookup(storageMedia),
        StorageClassLookup(storageClass),
        fileCount,
        directoryPath,
        localUser,
        localGroup,
        UserIdentityLookup(userIdentity),
        GroupLookup(groupName),
        measureTime,
        validDuration,
        resourceCapacityUsed,
        logicalCapacityUsed
        );
END //
DELIMITER ;