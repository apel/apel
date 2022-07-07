# APEL client and server source code

[![Build Status](https://travis-ci.org/apel/apel.svg?branch=dev)](https://travis-ci.org/apel/apel)
[![Coverage Status](https://coveralls.io/repos/github/apel/apel/badge.svg?branch=dev)](https://coveralls.io/github/apel/apel?branch=dev)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a8cdc36c46b241e6a77428fbfb6f23bd)](https://www.codacy.com/gh/apel/apel/dashboard)
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

## Acknowledgements

<span>
  <img alt="STFC logo" src="https://github.com/GOCDB/gocdb/raw/dev/htdocs/images/UKRI_STF_Council-Logo_Horiz-RGB_crop.png" height="57" />
  <img alt="EU flag" src="https://github.com/GOCDB/gocdb/raw/dev/htdocs/images/eu_flag_yellow_low_150.png" height="51" />
  <img alt="EOSC-hub logo" src="https://github.com/GOCDB/gocdb/raw/dev/htdocs/images/eosc-hub-v-web_150.png" height="57" />
</span>

APEL is provided by [STFC](https://stfc.ukri.org/), a part of [UK Research and Innovation](www.ukri.org), and is co-funded by the [EOSC-hub](https://www.eosc-hub.eu/) project (Horizon 2020) under Grant number 777536. Licensed under the [Apache 2 License](http://www.apache.org/licenses/LICENSE-2.0).
