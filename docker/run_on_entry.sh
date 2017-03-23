#!/bin/bash
# This file is run as process 1 by instances of the docker container
# it starts:
# - crond, to allow the periodic running of the summariser
# - the cloud loader, as we want to start loadig as soon as the
#   container is up (rather than waiting for the first summariser run)
#
# It then goes into an infinite loop as docker entrypoints have to
# not terminate to keep the container alive

# start cron
service crond start

# start the loader service
service apeldbloader-cloud start

#keep docker running
while true
do
  sleep 1
done

