-- This change attempts to fix the exploding processing time for increasingly large 
-- JobRecords and precursor tables for the JoinJobRecords procedure
--
-- Overwrites JoinJobRecords
-- Alters existing indexes to EventRecords, BlahdRecords, and JobRecords
-- Adds new indexes to EventRecords, BlahdRecords, and JobRecords
USE clientdb;

ALTER TABLE JobRecords ADD INDEX JobJoinIdx (UpdateTime, LocalJobId, SubmitHost, MachineNameID, EndTime);

ALTER TABLE EventRecords DROP INDEX EventJoinIdx; 
                          -- INDEX EventJoinIdx (SiteID, JobName) -- old
ALTER TABLE EventRecords ADD INDEX EventJoinIdx (Status, SiteID, JobName, EndTime);

ALTER TABLE EventRecords DROP INDEX EventUpdateIdx;
ALTER TABLE EventRecords ADD INDEX EventUpdateIdx (Status, MachineNameID, JobName, EndTime);

ALTER TABLE BlahdRecords DROP INDEX BlahdJoinIdx;
                          -- INDEX BlahdJoinIdx (ValidFrom, ValidUntil, SiteID, LrmsId) -- old
ALTER TABLE BlahdRecords ADD INDEX BlahdJoinIdx (Processed, ValidFrom, ValidUntil, SiteID, LrmsId, CEID);

ALTER TABLE BlahdRecords DROP INDEX BlahdUpdateIdx;
ALTER TABLE BlahdRecords ADD INDEX BlahdUpdateIdx (Processed, ValidUntil, CEID, LrmsId);


-- ------------------------------------------------------------------------------
-- Procedure for converting EventRecords + BlahdRecords into JobRecords
DROP PROCEDURE IF EXISTS JoinJobRecords;
DELIMITER //
CREATE PROCEDURE JoinJobRecords()
BEGIN
    DECLARE procstart DATETIME;
    DECLARE apeldn INT;

    SET procstart = NOW();
    SET apeldn = DNLookup("apelclient");

    REPLACE INTO JobRecords (
      UpdateTime,
      SiteID,                -- Foreign key
      SubmitHostID,          -- Foreign key
      MachineNameID,         -- Foreign key
      QueueID,               -- Foreign key
      LocalJobId,
      LocalUserId,
      GlobalUserNameID,      -- Foreign key
      FQAN,
      VOID,                  -- Foreign key
      VOGroupID,             -- Foreign key
      VORoleID,              -- Foreign key
      WallDuration,
      CpuDuration,
      Processors,
      NodeCount,
      StartTime,
      EndTime,
      InfrastructureDescription,
      InfrastructureType,
      MemoryReal,
      MemoryVirtual,
      ServiceLevelType,
      ServiceLevel,
      PublisherDNID,
      EndYear,
      EndMonth)
-- as long as we are not joining records from external databases we can do it with
-- raw IDs

    SELECT 
        NOW(),                                         -- JobRecord.UpdateTime
        EventRecords.SiteID as SiteID,                     -- JobRecord.Site
        BlahdRecords.CEID as SubmitHostID,                 -- JobRecord.SubmitHost
        EventRecords.MachineNameID as MachineNameID,       -- JobRecord.MachineName
        EventRecords.QueueID as QueueID,                   -- JobRecord.Queue
        EventRecords.JobName as LocalJobId,                -- JobRecord.LocalJobId
        EventRecords.LocalUserID as LocalUserId,           -- JobRecord.LocalUserId
        BlahdRecords.GlobalUserNameID as GlobalUserNameID, -- JobRecord.GlobalUserName
        BlahdRecords.FQAN as FQAN,
        BlahdRecords.VOID as VOID,                         -- JobRecord.VOID
        BlahdRecords.VOGroupID as VOGroupID,               -- JobRecord.VOGroup
        BlahdRecords.VORoleID as VORoleID,                 -- JobRecord.VORole
        EventRecords.WallDuration as WallDuration,         -- JobRecord.WallDuration
        EventRecords.CpuDuration as CpuDuration,           -- JobRecord.CpuDuration
        EventRecords.Processors as Processors,             -- JobRecord.Processors
        EventRecords.NodeCount as NodeCount,               -- JobRecord.NodeCount
        EventRecords.StartTime as StartTime,               -- JobRecord.StartTime
        EventRecords.EndTime as EndTime,                   -- JobRecord.EndTime
        EventRecords.Infrastructure as InfrastructureDescription,     -- JobRecord.Infrastructure
        "grid",                                            -- JobRecord.InfrastructureType
        EventRecords.MemoryReal as MemoryReal,             -- JobRecord.MemoryReal
        EventRecords.MemoryVirtual as MemoryVirtual,       -- JobRecord.MemoryVirtual
        SpecRecords.ServiceLevelType as ServiceLevelType,
        SpecRecords.ServiceLevel as ServiceLevel,
        apeldn,                            -- JobRecords.PublisherDN
        YEAR(EventRecords.EndTime),
        MONTH(EventRecords.EndTime)
    FROM SpecRecords
    INNER JOIN EventRecords FORCE INDEX (EventJoinIdx) ON EventRecords.SiteID = SpecRecords.SiteID
                             AND (EventRecords.EndTime >= SpecRecords.StartTime
                                  AND (EventRecords.EndTime < SpecRecords.StopTime OR SpecRecords.StopTime IS NULL))
    INNER JOIN BlahdRecords FORCE INDEX (BlahdJoinIdx) ON BlahdRecords.SiteID = SpecRecords.SiteID
                             AND BlahdRecords.CEID = SpecRecords.CEID
                             AND BlahdRecords.LrmsId = EventRecords.JobName
                             AND BlahdRecords.ValidFrom <= EventRecords.EndTime
                             AND BlahdRecords.ValidUntil > EventRecords.EndTime

    UPDATE EventRecords FORCE INDEX (EventUpdateIdx), JobRecords FORCE INDEX (JobJoinIdx)
    SET Status = 2
    WHERE EventRecords.Status = 0
        AND EventRecords.MachineNameID = JobRecords.MachineNameID
        AND EventRecords.JobName = JobRecords.LocalJobId
        AND EventRecords.EndTime = JobRecords.EndTime
        AND JobRecords.UpdateTime >= procstart;

    UPDATE BlahdRecords FORCE INDEX (BlahdUpdateIdx), JobRecords FORCE INDEX (JobJoinIdx)
    SET BlahdRecords.Processed = 1
    WHERE BlahdRecords.Processed = 0
        AND BlahdRecords.LrmsId = JobRecords.LocalJobId
        AND BlahdRecords.CEID = JobRecords.SubmitHostID
        AND BlahdRecords.ValidUntil > JobRecords.EndTime
        AND JobRecords.UpdateTime >= procstart;

END //
DELIMITER ;
