-- This script contains a SQL block that can update
-- APEL version 1.8.2 databases of the following types to 1.9.1:
--  - Client Grid Accounting Database

-- UPDATE SCRIPT FOR CLIENT SCHEMA

-- This will set any null LrmsIds to the empty string and change the default value to the same.

UPDATE BlahdRecords SET LrmsId = '' WHERE LrmsId is NULL;
ALTER TABLE BlahdRecords MODIFY COLUMN LrmsId VARCHAR(255) DEFAULT '';

-- This will correct the capitalisation of "SiteID" in the primary key.

ALTER TABLE BlahdRecords DROP PRIMARY KEY, ADD PRIMARY KEY(TimeStamp, SiteID, LrmsId, CEID);
