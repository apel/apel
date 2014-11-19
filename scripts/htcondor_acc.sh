#! /bin/sh

CONDOR_LOCATION=/home/condor/release
OUTPUT_LOCATION=/scratch/condor/apel

NOW=$(date +"%Y%m%dT%H%M%S")
OUTPUT_FILE=$OUTPUT_LOCATION/accounting.$NOW

$CONDOR_LOCATION/bin/condor_history -constraint "JobStartDate > 0" -format "%d|" ClusterId -format "%s|" Owner -format "%d|" RemoteWallClockTime -format "%d|" RemoteUserCpu -format "%d|" RemoteSysCpu -format "%d|" JobStartDate -format "%d|" EnteredCurrentStatus -format "%d|" ResidentSetSize_RAW -format "%d|" ImageSize_RAW -format "%d\n" RequestCpus > $OUTPUT_FILE

/usr/bin/apelparser

/bin/find $OUTPUT_LOCATION -name accounting.\* -mtime +30 -exec /bin/rm {} \;
