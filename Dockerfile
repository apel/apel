###########################################################
# This Dockerfile allows for the creation of an APEL Server 
# Docker Image with support for Cloud Accounting
#
# A deployed Docker instance will require an instance of
# the APEL Cloud Accounting Database and the mounting of: 
#
# - a cron job under /etc/cron.d to run
#   /usr/bin/run_cloud_summariser.sh (at least) daily 
# - APEL Cloud configuration files under /etc/apel
#
# and the optional mounting of:
#
# - a host direcotry under /var/spool/apel/cloud
#   to persistantly store messages
# - a MySQL configuraiton file under /etc/mysql
#   (to allow command line access to the MySQL database
#   from within the container.)
#
# It has been placed in the repository root to allow for future
# docker images to built 'commit by commit' from the exact
# state of the source in the repository. At the moment, it is 
# limited to tagged versions that have RPMs, as that is the 
# only way to install APEL.

###########################################################

FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

# Add EPEL repo so we can get pip
RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

# Install tools needed to get RPMs from GitHub
# Install python tools
# Install mysql
# Install cron
# Install APEL requirements
RUN yum -y install wget unzip python-pip python-devel mysql mysql-devel gcc cronie python-iso8601 python-ldap

# Get APEL 1.6.0 codebase
# In future, we maybe be able to run python setup.py install instead
# and build a docker image based on the exact state of the
# repository branch being built
RUN wget https://github.com/apel/apel/releases/download/1.6.0-1/apel-lib-1.6.0-1.el6.noarch.rpm
RUN wget https://github.com/apel/apel/releases/download/1.6.0-1/apel-server-1.6.0-1.el6.noarch.rpm

# Install APEL code base from above RPMs
# Use --nodeps because we dont need the ssm
RUN rpm -i apel-lib-1.6.0-1.el6.noarch.rpm --nodeps
RUN rpm -i apel-server-1.6.0-1.el6.noarch.rpm --nodeps

# Install APEL REST requirements
# python-daemon is sperately installed because it's
# not a hard requiremnt of APEL (ie it's
# not in requirements.txt, but in this case it is needed)
COPY requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt
RUN pip install python-daemon
RUN rm /root/requirements.txt

# Register the cloud loader as a service
COPY scripts/apeldbloader-cloud /etc/init.d/apeldbloader-cloud

# Copy the script the cron job runs
COPY scripts/run_cloud_summariser.sh /usr/bin/run_cloud_summariser.sh

# Make cloud log and run directory
RUN mkdir /var/log/cloud
RUN mkdir /var/run/cloud

# Make the apel user own those directories
RUN chown apel /var/log/cloud
RUN chown apel /var/run/cloud

# Make cloud spool dir
RUN mkdir -p /var/spool/apel/cloud/

COPY docker/run_on_entry.sh /root/run_on_entry.sh

ENTRYPOINT /root/run_on_entry.sh
