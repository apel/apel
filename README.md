# APEL client and server source code

[![Build Status](https://travis-ci.org/apel/apel.svg?branch=dev)](https://travis-ci.org/apel/apel)
[![Coverage Status](https://coveralls.io/repos/github/apel/apel/badge.svg?branch=dev)](https://coveralls.io/github/apel/apel?branch=dev)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b614b03d576a4f5cbb6efa2e64e5f7ef)](https://www.codacy.com/app/apel/apel)
[![Maintainability](https://api.codeclimate.com/v1/badges/03094b74f5fc4f728bc7/maintainability)](https://codeclimate.com/github/apel/apel/maintainability)

## Project overview

The APEL project provides grid accounting for EGI. It is written in
Python and uses MySQL. It has the following components:

### apel-parsers

These extract data from the following batch systems:
* LSF
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
