#!/bin/bash

# This script can be run to extract usage accounting data from SLURM for later
# parsing by an APEL client. There is a choice of sacct commands to run below.


sleep 2

NOW=$(date +"%Y%m%d")
FILE="/var/log/apel/slurm_acc.$NOW"


# Please comment/uncomment the approriate sacct lines for your use case.

# This is the original sacct call which uses CPUTimeRAW for CPU Duration.
# CPUTimeRAW is equal to Elapsed and so gives unrealistic efficiency.

sacct -P -n --format=JobID,JobName,User,Group,Start,End,Elapsed,CPUTimeRAW,Partition,NCPUS,NNodes,NodeList,MaxRSS,MaxVMSize,State -j "$JOBID" >> "$FILE"

# This sacct call uses TotalCPU for CPU Duration which is the sum of SystemCPU and UserCPU.
# TotalCPU should give more realistic efficiency but may not work well for multicore jobs.

### sacct -P -n --format=JobID,JobName,User,Group,Start,End,Elapsed,TotalCPU,Partition,NCPUS,NNodes,NodeList,MaxRSS,MaxVMSize,State -j "$JOBID" >> "$FILE"
