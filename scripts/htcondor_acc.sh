#! /bin/sh

CONDOR_LOCATION=/usr
OUTPUT_LOCATION=/var/log/accounting

# Find all the history files modified in the last two months
# (there can be more than one, if the CE submits to several schedds)
HISTORY_FILES=$(find /var/lib/condor/spool/ -name history\* -mtime -61)

# Create a temporary accounting file name
NOW=$(date +"%Y%m%dT%H%M%S")
OUTPUT_FILE=$OUTPUT_LOCATION/accounting.$NOW

# Build the filter for the history command
CONSTR="(JobStartDate>0)&&(CompletionDate>`date +%s -d "01 Jan 2014"`)"

# Only get the jobs submitted from this CE (ceCertificateSubject is
# set in /etc/condor/config.s/blah and added to the job classad with
# the SUBMIT_EXPRS directive in the same file)
CONSTR=${CONSTR}"&&(ceCertificateSubject==$(condor_config_val ceCertificateSubject))"

# Populate the temporary file
for HF in $HISTORY_FILES
do
  $CONDOR_LOCATION/bin/condor_history -file $HF -constraint $CONSTR \
    -format "%s|" GlobalJobId \
    -format "%s|" Owner \
    -format "%d|" RemoteWallClockTime \
    -format "%d|" RemoteUserCpu \
    -format "%d|" RemoteSysCpu \
    -format "%d|" JobStartDate \
    -format "%d|" EnteredCurrentStatus \
    -format "%d|" ResidentSetSize_RAW \
    -format "%d|" ImageSize_RAW \
    -format "%d|" RequestCpus \
    -format "%s\n" Group >> $OUTPUT_FILE
done

# Invoke the parser
/usr/bin/apelparser

# Cleanup
/bin/find $OUTPUT_LOCATION -name accounting.\* -mtime +30 -exec /bin/rm {} \;
