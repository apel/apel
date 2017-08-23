-- This script is contains multiple comments block that apply to
-- APEL Version 1.6.0, and the following databases:
--  - Client Grid Accounting Database
--  - Server Grid Accounting Database
--  - Cloud Accounting Database

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

-- This script will set any null Cloud UpdateTimes to the zero timestamp
-- (to prevent issues determining how recent a record is)
-- and then explicitly set the UpdateTimes of
-- future rows to update

UPDATE CloudRecords SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE CloudRecords MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE CloudSummaries SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE CloudSummaries MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE LastUpdated SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE LastUpdated MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
*/
