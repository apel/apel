# Server Upgrade: 1.2.x to 1.3.x

This procedure is for sites running the APEL regional server. Sites running the APEL client are _not_ affected by the schema change described in this document.

## Motivation

Version 1.3 of the APEL server software uses a different database schema to version 1.2. This change was made to allow normalised summary records to be sent to APEL servers which necessitated altering one table among other changes. This requires extra steps to be performed during an upgrade.

## Summary of procedure

The outline of this procedure is to export all the data from the database except for the super-summaries that are compiled from job recrods and received summaries. The super-summaries are then recreated after importing the data once the schema has been updated.

## Procedure

1. Stop any APEL services that use the database (dbloader, dbunloader, summariser). SSM can continue to run.
1. Do a full database backup.
1. Export all data except for the SuperSummaries table. (Assuming the database is named `apel`.)

  ```shell
  mysqldump -u root -p --no-create-info --ignore-table=apel.SuperSummaries apel | gzip > upgrade_data.sql.gz
  ```
1. Log into MySQL and drop the database.
1. Upgrade the RPMs. (Assuming v1.3.1 packages for SL5 are used.)

  ```shell
  rpm -U apel-lib-1.3.1-1.el5.noarch.rpm apel-server-1.3.1-1.el5.noarch.rpm
  ```
1. Log into MySQL and create a new empty database.
1. Load the new server schema.

  ```shell
  mysql -u root -p apel < /usr/share/apel/server.sql
  ```
1. Import data.

  ```shell
  zcat upgrade_data.sql.gz | mysql -u root -p apel
  ```
1. Run the summarising process to rebuild the super-summaries.
1. Restart all APEL services.

## Support

Support with this procedure is available through [GGUS](https://ggus.eu/).
