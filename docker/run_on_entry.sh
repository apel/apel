#!/bin/bash

# start cron
service crond start

# start the loader service
service apeldbloader-cloud start

#keep docker running
while true
do
  sleep 1
done

