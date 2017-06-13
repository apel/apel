#!/bin/bash
# This file is run as process 1 by instances of the docker container.
# It starts:
# - the cloud loader, as we want to start loadig as soon as the
#   container is up (rather than waiting for the first summariser run)
# - crond, to allow the periodic running of the summariser
#
# It then goes into an infinite loop as Docker entrypoints have to
# not terminate to keep the container alive

# start the loader service
service apeldbloader-cloud start

# start cron
service crond start

#keep docker running
while true
do
  sleep 1
done

