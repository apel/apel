#!/bin/bash

OUTPUT_LOCATION=/var/log/condor-ce/accounting

if [ ! -d "$OUTPUT_LOCATION" ]; then
	mkdir -p $OUTPUT_LOCATION
fi

# Find all the history files modified in the last two months
# (there can be more than one, if the CE submits to several schedds)
HISTORY_FILES=$(find /var/lib/condor-ce/spool/ -name history\* -mtime -62)

# Create a temporary accounting file name
NOW=$(date +"%Y%m%dT%H%M%S")
OUTPUT_FILE=$OUTPUT_LOCATION/accounting.$NOW

# Build the filter for the history command
CONSTR="(JobStartDate>0)&&(CompletionDate>$(date +%s -d "01 Jan 2014"))"

# Populate the temporary file
for HF in $HISTORY_FILES
do
  $CONDOR_LOCATION/bin/condor_ce_history -file $HF -constraint $CONSTR \
    -format "%s|" GlobalJobId \
    -format "%s|" RoutedToJobId \
    -format "%s|" Owner \
    -format "%s|" x509userproxysubject \
    -format "%s|" x509UserProxyFirstFQAN \
    -format "%s|" x509UserProxyVOName \
    -format "%d|" RemoteWallClockTime \
    -format "%d|" RemoteUserCpu \
    -format "%d|" RemoteSysCpu \
    -format "%d|" JobStartDate \
    -format "%d|" EnteredCurrentStatus \
    -format "%d|" ResidentSetSize_RAW \
    -format "%d|" ImageSize_RAW \
    -format "%d|" RequestCpus \
    -format "\n" EMPTY >> $OUTPUT_FILE
done

# Invoke the parser
#/usr/bin/apelparser --config /etc/apel/parser.cfg

# Cleanup
/bin/find $OUTPUT_LOCATION -name accounting.\* -mtime +30 -exec /bin/rm {} \;
