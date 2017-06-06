# Scripts included for the Docker image

The following files are present in this directory for the purposes of the Docker image, as they are common to all instances of the APEL cloud server.

* `run_cloud_summariser.sh` 
* `apeldbloader-cloud`

They could also be included in Server RPMs in the future, but are not at the moment, so have been included here (rather than the docker directory, which is reserved for files only relevant to the Docker image).

## run_cloud_summariser.sh

This script runs the summariser in a safe way, by switching off the cloud loader to ensure there are no writes to the database while summarising.

## apeldbloader-cloud

This init script allows the Cloud Loader to be started/stopped with the `service` command. It differs from the more generic `dbld` also included in this directory, as it initiates a specific instance of a database loader, i.e. the Cloud Loader.


