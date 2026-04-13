-- This script contains a SQL block that can update
-- APEL version 2.4.0 databases of the following types to x.x.x:
--  - Server Grid Accounting Database

-- UPDATE SCRIPT FOR SERVER SCHEMA


ALTER TABLE Summaries
  DROP PRIMARY KEY,
  ADD PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID,
                   SubmitHostId, InfrastructureType, ServiceLevelType, ServiceLevel, NodeCount, Processors);

ALTER TABLE NormalisedSummaries
  DROP PRIMARY KEY,
  ADD PRIMARY KEY (SiteID, Month, Year, GlobalUserNameID, VOID, VORoleID, VOGroupID,
                   SubmitHostId, Infrastructure, NodeCount, Processors, ServiceLevelType);
