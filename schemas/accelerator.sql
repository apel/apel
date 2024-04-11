-- This schema adds the tables necessary for Accelerator accounting as a
-- separate record as part of the wider Cloud Accounting system.

-- ------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS SiteNameLookup;
DELIMITER //
CREATE FUNCTION SiteNameLookup(lookup INTEGER) RETURNS VARCHAR(255) DETERMINISTIC
BEGIN
  DECLARE result VARCHAR(255);
  SELECT name FROM Sites WHERE id = lookup INTO result;
  RETURN result;
END //
DELIMITER ;

DROP TABLE IF EXISTS AcceleratorRecords;
CREATE TABLE AcceleratorRecords (
  UpdateTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  MeasurementMonth INT NOT NULL,
  MeasurementYear INT NOT NULL,

  AssociatedRecordType VARCHAR(255) NOT NULL,
  AssociatedRecord VARCHAR(255) NOT NULL,

  GlobalUserName VARCHAR(255),
  FQAN VARCHAR(255) NOT NULL,
  SiteID INT NOT NULL,
  Count DECIMAL(10,3) NOT NULL,
  Cores INT,
  ActiveDuration INT,
  AvailableDuration INT,
  BenchmarkType VARCHAR(255),
  Benchmark DECIMAL(10,3),
  Type VARCHAR(255) NOT NULL,
  Model VARCHAR(255),
  PublisherDNID INT NOT NULL,

  PRIMARY KEY (MeasurementMonth, MeasurementYear,
               AssociatedRecordType, AssociatedRecord,
               SiteID)

  -- [?] INDEX
);

DROP PROCEDURE IF EXISTS ReplaceAcceleratorRecord;
DELIMITER //
CREATE PROCEDURE ReplaceAcceleratorRecord(
  measurementMonth INT,
  measurementYear INT,
  associatedRecordType VARCHAR(255),
  associatedRecord VARCHAR(255),
  globalUserName VARCHAR(255),
  fqan VARCHAR(255),
  SiteName VARCHAR(255),
  count DECIMAL(10,3),
  cores INT,
  activeDuration INT,
  availableDuration INT,
  benchmarkType VARCHAR(255),
  benchmark DECIMAL,
  type VARCHAR(255),
  model VARCHAR(255),
  publisherDN VARCHAR(255)
)
BEGIN
REPLACE INTO AcceleratorRecords(
  MeasurementMonth,
  MeasurementYear,
  AssociatedRecordType,
  AssociatedRecord,
  GlobalUserName,
  FQAN,
  SiteID,
  Count,
  Cores,
  ActiveDuration,
  AvailableDuration,
  BenchmarkType,
  Benchmark,
  Type,
  Model,
  PublisherDNID
)
VALUES(
  measurementMonth,
  measurementYear,
  associatedRecordType,
  associatedRecord,
  globalUserName,
  fqan,
  SiteLookup(SiteName),
  count,
  cores,
  activeDuration,
  availableDuration,
  benchmarkType,
  benchmark,
  type,
  model,
  DNLookup(publisherDN)
);
END //
DELIMITER ;


DROP TABLE IF EXISTS AcceleratorSummaries;
CREATE TABLE AcceleratorSummaries (
    Month INT NOT NULL,
    Year INT NOT NULL,
    AssociatedRecordType VARCHAR(255) NOT NULL,
    GlobalUserName VARCHAR(255),
    SiteName VARCHAR(255) NOT NULL,
    Count DECIMAL(10,3) NOT NULL,
    Cores INT,
    AvailableDuration INT NOT NULL,
    ActiveDuration INT,
    BenchmarkType VARCHAR(255),
    Benchmark DECIMAL(10,3),
    Type VARCHAR(255) NOT NULL,
    Model VARCHAR(255),
    NumberOfRecords INT NOT NULL,
    PublisherDNID VARCHAR(255) NOT NULL,

    PRIMARY KEY (Month, Year, AssociatedRecordType, SiteName, Type)
);


DROP PROCEDURE IF EXISTS SummariseAccelerators;
DELIMITER //
CREATE PROCEDURE SummariseAccelerators()

BEGIN
    REPLACE INTO AcceleratorSummaries(Month, Year, AssociatedRecordType,
        GlobalUserName, SiteName,
        Count, Cores, AvailableDuration, ActiveDuration,
        BenchmarkType, Benchmark, Type, Model, NumberOfRecords, PublisherDNID)
    SELECT
      MeasurementMonth,
      MeasurementYear,
      AssociatedRecordType,
      GlobalUserName,
      SiteNameLookup(SiteID) as SiteName,
      Count,
      Cores,
      SUM(AvailableDuration),
      SUM(ActiveDuration),
      BenchmarkType,
      Benchmark,
      Type,
      Model,
      COUNT(*) as NumberOfRecords,
      'summariser' as PublisherDNID
      FROM AcceleratorRecords
      GROUP BY
          MeasurementMonth, MeasurementYear,
          AssociatedRecordType,
          GlobalUserName, SiteName,
          Cores, Type,
          Benchmark, BenchmarkType
      ORDER BY NULL;
END //
DELIMITER ;


DROP PROCEDURE IF EXISTS ReplaceAcceleratorSummaryRecord;
DELIMITER //
CREATE PROCEDURE ReplaceAcceleratorSummaryRecord(
  Month INT,
  Year INT,
  associatedRecordType VARCHAR(255),
  globalUserName VARCHAR(255),
  SiteName VARCHAR(255),
  count DECIMAL(10,3),
  cores INT,
  activeDuration INT,
  availableDuration INT,
  benchmarkType VARCHAR(255),
  benchmark DECIMAL,
  type VARCHAR(255),
  model VARCHAR(255),
  number INT,
  publisherDNID INT
)
BEGIN
REPLACE INTO AcceleratorSummaries(
  Month,
  Year,
  AssociatedRecordType,
  GlobalUserName,
  SiteName,
  Count,
  Cores,
  ActiveDuration,
  AvailableDuration,
  BenchmarkType,
  Benchmark,
  Type,
  Model,
  NumberOfRecords,
  PublisherDNID
)
VALUES(
  Month,
  Year,
  associatedRecordType,
  globalUserName,
  SiteNameLookup(SiteName),
  count,
  cores,
  activeDuration,
  availableDuration,
  benchmarkType,
  benchmark,
  type,
  model,
  number,
  publisherDNID
);
END //
DELIMITER ;


-- @Author: Nicholas Whyatt, RedProkofiev@github
-- AcceleratorModels is meant to support categorising accelerators by sensible
-- group categories, and then to be merged into VAcceleratorSummaries if necessary
-- or added as a variable from Grafana.
-- Date exists so that the queries can simply ask for the latest version with the idea
-- that models can be recategorised later on in their lifecycle.
SET GLOBAL event_scheduler = ON;

DROP TABLE IF EXISTS AcceleratorModels;
CREATE TABLE AcceleratorModels (
    Date TIMESTAMP NOT NULL,
    Model VARCHAR(255) NOT NULL,
    Type VARCHAR(255) NOT NULL,
    Category VARCHAR(255),

    PRIMARY KEY (Model, Type, Date)
);


-- This table exists to speed up queries within Grafana by storing the results of
-- the nested time-dependent subquery formerly stored directly within
-- VAcceleratorSummaries.
DROP TABLE IF EXISTS AcceleratorModelSummaries;
CREATE TABLE AcceleratorModelSummaries (
    SiteName VARCHAR(255) NOT NULL,
    FQAN VARCHAR(255) NOT NULL,
    GlobalUserName VARCHAR(255),
    Type VARCHAR(255) NOT NULL,
    Model VARCHAR(255),
    Month INT NOT NULL,
    Year INT NOT NULL,
    Count DECIMAL(10,3) NOT NULL,
    Cores INT,
    AvailableDuration INT NOT NULL,
    ActiveDuration INT,
    AssociatedRecordType VARCHAR(255) NOT NULL,
    BenchmarkType VARCHAR(255),
    Benchmark DECIMAL(10,3),
    Category VARCHAR(255),

    PRIMARY KEY (Month, Year, AssociatedRecordType, SiteName, Type, Model)
);


-- GetNewModels shunts all the type, model combinations into AcceleratorModels
-- This means that models already in AcceleratorModels should not be overwritten
-- and if they're now faulty (or uploaded faultily by this procedure, should be
-- updated!)
DROP PROCEDURE IF EXISTS GetNewModels;
DELIMITER //
CREATE PROCEDURE GetNewModels()
BEGIN
    REPLACE INTO AcceleratorModels (Date, Model, Type)
    SELECT TIMESTAMP('2000-01-01 00:00:00'), ar.Model, ar.Type
    FROM AcceleratorRecords ar
    WHERE NOT EXISTS (
        SELECT 1
        FROM AcceleratorModels am
        WHERE am.Model = ar.Model
        AND am.Type = ar.Type
    );
END //
DELIMITER ;


-- Expensive operation to bind time-dependent rules of model summaries into the
-- AcceleratorModelSummaries table.
DROP PROCEDURE IF EXISTS GetModelSummaries;
DELIMITER //
CREATE PROCEDURE GetModelSummaries()
BEGIN
    REPLACE INTO AcceleratorModelSummaries
    SELECT
      iris_accelerator.AcceleratorSummaries.SiteName,
      iris_accelerator.AcceleratorRecords.FQAN,
      iris_accelerator.AcceleratorSummaries.GlobalUserName,
      iris_accelerator.AcceleratorSummaries.Type,
      iris_accelerator.AcceleratorSummaries.Model,
      iris_accelerator.AcceleratorSummaries.Month,
      iris_accelerator.AcceleratorSummaries.Year,
      iris_accelerator.AcceleratorSummaries.Count,
      iris_accelerator.AcceleratorSummaries.Cores,
      iris_accelerator.AcceleratorSummaries.AvailableDuration,
      iris_accelerator.AcceleratorSummaries.ActiveDuration,
      iris_accelerator.AcceleratorSummaries.AssociatedRecordType,
      iris_accelerator.AcceleratorSummaries.BenchmarkType,
      iris_accelerator.AcceleratorSummaries.Benchmark,
      iris_accelerator.AcceleratorModels.Category
    FROM
      iris_accelerator.AcceleratorRecords,
      iris_accelerator.AcceleratorSummaries,
      iris_accelerator.AcceleratorModels
    WHERE
      iris_accelerator.AcceleratorRecords.GlobalUserName = iris_accelerator.AcceleratorSummaries.GlobalUserName
      AND SiteNameLookup(iris_accelerator.AcceleratorRecords.SiteID) = iris_accelerator.AcceleratorSummaries.SiteName
      AND iris_accelerator.AcceleratorRecords.Type = iris_accelerator.AcceleratorSummaries.Type
      AND iris_accelerator.AcceleratorRecords.Model = iris_accelerator.AcceleratorSummaries.Model
      AND iris_accelerator.AcceleratorModels.Date = (
        SELECT MAX(iris_accelerator.AcceleratorModels.Date)
        FROM
          iris_accelerator.AcceleratorModels
        WHERE
          iris_accelerator.AcceleratorModels.Date <= str_to_date(CONCAT_WS('-', iris_accelerator.AcceleratorSummaries.Year, LPAD(iris_accelerator.AcceleratorSummaries.Month, 2, 0)), '%Y-%m-01 00:00:00')
          AND iris_accelerator.AcceleratorSummaries.Model = iris_accelerator.AcceleratorSummaries.Model
          AND iris_accelerator.AcceleratorModels.Type = iris_accelerator.AcceleratorSummaries.Type
        )
    GROUP BY
      MeasurementMonth, MeasurementYear,
      AssociatedRecordType,
      GlobalUserName, SiteName,
      Cores, Type,
      Benchmark, BenchmarkType
    ORDER BY NULL;
END
//
DELIMITER ;


-- This is an insertion of a value for when a card needs to be
-- recategorised.
DROP PROCEDURE IF EXISTS UpdateModel;
DELIMITER //
CREATE PROCEDURE UpdateModel(
    model VARCHAR(255),
    type VARCHAR(255),
    category VARCHAR(255)
)
BEGIN
    INSERT INTO AcceleratorModels(Date, Model, Type, Category)
    VALUES (CURRENT_TIMESTAMP(), model, type, category);
END //
DELIMITER ;


-- WARNING: CHECK UpdateModel to see if that's what you need.
-- This procedure is meant to ALTER an existing record.
-- This means that it will alter historical data.  It should only
-- be used to alter the very first record.
DROP PROCEDURE IF EXISTS AlterModel;
DELIMITER //
CREATE PROCEDURE AlterModel(
    date TIMESTAMP,
    model VARCHAR(255),
    type VARCHAR(255),
    col VARCHAR(255),
    val VARCHAR(255)
)
BEGIN
    SET @sql = CONCAT('UPDATE AcceleratorModels SET ', col, ' = ? WHERE Date = ? AND Model = ? AND Type = ?');
    PREPARE stmt FROM @sql;
    EXECUTE stmt USING val, date, model, type;
    DEALLOCATE PREPARE stmt;
END //
DELIMITER ;

-- Event
-- Insert new model/type combinations into AcceleratorModels
DROP EVENT IF EXISTS model_summaries_hourly;
DELIMITER //
CREATE EVENT model_summaries_hourly
    ON SCHEDULE
      EVERY 1 HOUR
    COMMENT 'Checks for new model/type combos and binds the correct category to them.'
    DO
    BEGIN
      CALL GetNewModels();
      CALL GetModelSummaries();
    END;
//
DELIMITER ;


-- This is where you get your data from in Grafana :>
DROP VIEW IF EXISTS VAcceleratorSummaries;
CREATE VIEW VAcceleratorSummaries AS
SELECT * FROM AcceleratorModelSummaries;
