-- UPDATE SCRIPT FOR CLIENT SCHEMA
-- This script will set any null UpdateTimes to the zero timestamp
-- (to prevent issues determining how recent a record is)
-- and then explicitly set the UpdateTimes of 
-- future rows to update

UPDATE JobRecords SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE JobRecords MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE SuperSummaries SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE SuperSummaries MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

UPDATE LastUpdated SET UpdateTime = '0000-00-00 00:00:00' WHERE UpdateTime IS NULL;
ALTER TABLE LastUpdated MODIFY COLUMN UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
