APEL client and server source code
==================================

Project overview
----------------

The APEL project provides grid accounting for EGI. It is written in 
python and MySQL. It has the following
components:

  apel-parsers
  ------------
These extract data from the following batch systems:
 * SGE/OGE
 * LSF 5.x to 9.x
 * PBS
and place in the client database.

  apel-client
  -----------
This processes the data and sends it to the APEL server using SSM.

  apel-server
  -----------
This processes data from all sites and sends it on to the accounting 
portal using SSM.

  apel-lib
  --------
This contains all the library python code for apel-parsers, apel-client
and apel-server

  apel-ssm
  --------
This is a messaging system, which has its own github repository at 
https://github.com/apel/ssm

