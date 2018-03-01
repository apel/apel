# APEL client and server source code

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/3fd919315f4b49e7b99df6d5512eca35)](https://app.codacy.com/app/apel/apel?utm_source=github.com&utm_medium=referral&utm_content=apel/apel&utm_campaign=badger)
[![Build Status](https://travis-ci.org/apel/apel.svg?branch=dev)](https://travis-ci.org/apel/apel)
[![Coverage Status](https://coveralls.io/repos/apel/apel/badge.svg?branch=dev)](https://coveralls.io/github/apel/apel?branch=dev)
[![Code Health](https://landscape.io/github/apel/apel/dev/landscape.svg?style=flat)](https://landscape.io/github/apel/apel/dev)

## Project overview

The APEL project provides grid accounting for EGI. It is written in 
Python and uses MySQL. It has the following components:

### apel-parsers

These extract data from the following batch systems:
* LSF 5.x to 9.x
* PBS
* SGE/OGE
* SLURM
* HTCondor

and place it in the client database.

### apel-client

This processes the data and sends it to the APEL server using SSM.

### apel-server

This processes data from all sites and sends it on to the accounting 
portal using SSM.

### apel-lib

This contains all the library python code for apel-parsers, apel-client
and apel-server.

### apel-ssm

This is a messaging system, which has its own GitHub repository at 
[apel/ssm](https://github.com/apel/ssm)
