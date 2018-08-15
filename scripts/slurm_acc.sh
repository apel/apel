#!/bin/bash

sleep 2

NOW=$(date +"%Y%m%d")
FILE="/var/log/apel/slurm_acc.$NOW"

sacct -P -n --format=JobID,JobName,User,Group,Start,End,Elapsed,CPUTimeRAW,Partition,NCPUS,NNodes,NodeList,MaxRSS,MaxVMSize,State -j "$JOBID" >> "$FILE"
