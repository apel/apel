#!/bin/bash

# This script runs the summariser in a safe way, by 
# switching off the cloud loader to ensure there
# are no writes to the database while summarising.

# Stop the dbloader
/sbin/service apeldbloader-cloud stop

# Wait to ensure dbloader has stopped
sleep 5

# Run the summariser
python /usr/bin/apelsummariser -d /etc/apel/clouddb.cfg -c /etc/apel/cloudsummariser.cfg

# Wait to ensure summariser has stopped
sleep 5

# Start the dbloader
/sbin/service apeldbloader-cloud start

