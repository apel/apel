-- UPDATE SCRIPT FOR CLOUD SCHEMA
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
