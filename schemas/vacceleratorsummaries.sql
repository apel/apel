-- This schema is used in conjunction (and should be merged with) accelerator.sql
-- in order to create a unified view used for sorting data.  It creates supporting
-- tables to join data accurately.

---------------------------------------------------------------------------------

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
CREATE EVENT model_summaries_hourly
    ON SCHEDULE
      EVERY 1 HOUR
    COMMENT 'Checks for new model/type combos and binds the correct category to them.'
    DO
      CALL GetNewModels();
      CALL GetModelSummaries();


-- This is where you get your data from in Grafana :>
DROP VIEW IF EXISTS VAcceleratorSummaries;
CREATE VIEW VAcceleratorSummaries AS
SELECT * FROM AcceleratorModelSummaries;
