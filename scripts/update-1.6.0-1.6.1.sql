-- This script contains multiple comment blocks that can update
-- APEL version 1.6.0 databases of the following types to 1.6.1:
--  - Client Grid Accounting Database
--  - Server Grid Accounting Database
--  - Cloud Accounting Database
--  - Storage Accounting Database

-- To update, find the relevent comment block below and remove
-- its block comment symbols /* and */ then run this script.

/*
-- UPDATE SCRIPT FOR CLIENT SCHEMA

-- If you have a Client Grid Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This section will set any null Client Grid UpdateTimes to the zero timestamp
-- (to prevent issues determining how recent a record is)
-- and then explicitly set the UpdateTimes of 
-- future rows to update

UPDATE JobRecords SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE JobRecords MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE SuperSummaries SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE SuperSummaries MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE LastUpdated SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE LastUpdated MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
*/


/*
-- UPDATE SCRIPT FOR SERVER SCHEMA

-- If you have a Server Grid Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This script will set any null Server Grid UpdateTimes to the zero timestamp
-- (to prevent issues determining how recent a record is)
-- and then explicitly set the UpdateTimes of 
-- future rows to update

UPDATE JobRecords SET UpdateTime = '0000-00-00 00:00:00'  WHERE UpdateTime IS NULL;
ALTER TABLE JobRecords MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE Summaries SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE Summaries MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE NormalisedSummaries SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE NormalisedSummaries MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE HybridSuperSummaries SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE HybridSuperSummaries MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE SyncRecords SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE SyncRecords MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE LastUpdated SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE LastUpdated MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
*/


/*
-- UPDATE SCRIPT FOR CLOUD SCHEMA

-- If you have a Cloud Accounting Database and wish to
-- upgrade to APEL Version next, remove the block comment
-- symbols around this section and run this script

-- This section will set any null Cloud UpdateTimes to the zero timestamp
-- (to prevent issues determining how recent a record is)
-- and then explicitly set the UpdateTimes of
-- future rows to update

UPDATE CloudRecords SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE CloudRecords MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE CloudSummaries SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE CloudSummaries MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE LastUpdated SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE LastUpdated MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- This section will add the outstanding fields that are part of the
-- GROUP BY statement in the summariser to the CloudSummaries
-- table primary key.
-- If it is grouped on as part of the summariser,
-- it should be part of the primary key.

-- It's possible CpuCount could be NULL, and to add it to the
-- primary key the cloumn has to be set to NOT NULL,
-- so set any NULL values to a reasonable default.
UPDATE CloudSummaries SET CpuCount=0 WHERE CpuCount IS NULL;

-- Set CpuCount column to NOT NULL,
ALTER TABLE CloudSummaries MODIFY CpuCount INT NOT NULL;

-- Add fields to primary key to prevent summaries overriding each other.
ALTER TABLE CloudSummaries DROP PRIMARY KEY, ADD PRIMARY KEY(
  SiteID, CloudComputeServiceID, Month, Year, GlobalUserNameID,
  VOID, VOGroupID, VORoleID, Status, CloudType, ImageId, CpuCount,
  BenchmarkType, Benchmark
  );

*/


/*
-- UPDATE SCRIPT FOR STORAGE SCHEMA

-- If you have a Storage Accounting Database and wish to
-- upgrade to the next APEL version, remove the block comment
-- symbols around this section and then run this script.

-- This script adds the VStarRecords view.

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
*/
