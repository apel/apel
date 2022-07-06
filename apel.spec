# Conditionally define python_sitelib
%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:           apel
Version:        1.9.0
%define releasenumber 1
Release:        %{releasenumber}%{?dist}
Summary:        APEL packages

Group:          Development/Languages
License:        ASL 2.0
URL:            https://wiki.egi.eu/wiki/APEL
Source:         %{name}-%{version}-%{releasenumber}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

%define apelconf %_sysconfdir/apel

%description
The apel packages.
The project is written in Python.

%package lib
Summary:        Libraries required for Apel Client, Server and Parsers
Group:          Development/Languages
Requires:       MySQL-python, python-ldap < 3.4.0 , python-iso8601, python-dirq
Requires(pre):  shadow-utils

%description lib
apel-lib provides required libraries for the rest of APEL system.

%package parsers
Summary:        Parsers for APEL system
Group:          Development/Languages
Requires:       apel-lib >= %{version}
Requires(pre):  shadow-utils

%description parsers
The apel-parsers package contains parsers for all the batch systems
supported by the APEL system: Torque, SGE and LSF.

%package client
Summary:        APEL client package
Group:          Development/Languages
Requires:       apel-lib >= %{version}, apel-ssm >= 3.2.0
Requires(pre):  shadow-utils

%description client
The apel-client package contains all code needed to retrieve data from
the accounting database, process it and send it to the apel server using
SSM.

%package server
Summary:        APEL server package
Group:          Development/Languages
Requires:       apel-lib >= %{version}
Requires(pre):  shadow-utils

%description server
The apel-server package contains all code needed to receive accounting data
from clients, to process and to send the results elsewhere using SSM.

%prep
%setup -q -n %{name}-%{version}-%{releasenumber}

%build

%install
rm -rf $RPM_BUILD_ROOT

# Create directories
mkdir -p %{buildroot}%{apelconf}
mkdir -p %{buildroot}%_bindir
mkdir -p %{buildroot}%{python_sitelib}/apel
mkdir -p %{buildroot}%_sysconfdir/logrotate.d
mkdir -p %{buildroot}%_datadir/apel
mkdir -p %{buildroot}%_defaultdocdir
# Directories for logs, PID files
mkdir -p %{buildroot}%{_localstatedir}/log/apel
mkdir -p %{buildroot}%{_localstatedir}/run/apel

# Python libraries
# Library
cp -fr apel/* %{buildroot}%{python_sitelib}/apel

# Scripts
cp bin/client.py %{buildroot}%_bindir/apelclient
cp bin/parser.py %{buildroot}%_bindir/apelparser
cp bin/dbloader.py %{buildroot}%_bindir/apeldbloader
cp bin/dbunloader.py %{buildroot}%_bindir/apeldbunloader
cp bin/summariser.py %{buildroot}%_bindir/apelsummariser
cp bin/retrieve_dns.py %{buildroot}%_bindir/apelauth

# Configuration files
cp conf/client.cfg %{buildroot}%{apelconf}
cp conf/summariser.cfg %{buildroot}%{apelconf}/
cp conf/unloader.cfg %{buildroot}%{apelconf}/
cp conf/loader.cfg %{buildroot}%{apelconf}/
cp conf/db.cfg %{buildroot}%{apelconf}/
cp conf/parser.cfg %{buildroot}%{apelconf}/
cp conf/auth.cfg %{buildroot}%{apelconf}/

# database schemas
cp schemas/client.sql %{buildroot}%_datadir/apel/
cp schemas/server.sql %{buildroot}%_datadir/apel/
cp schemas/server-extra.sql %{buildroot}%_datadir/apel/
cp schemas/cloud.sql %{buildroot}%_datadir/apel/
cp schemas/storage.sql %{buildroot}%_datadir/apel/

# All update scripts matched by wildcard
cp scripts/update-*.sql %{buildroot}%_datadir/apel/

# accounting scripts
cp scripts/slurm_acc.sh %{buildroot}%_datadir/apel/
cp scripts/htcondor_acc.sh %{buildroot}%_datadir/apel/

# message status script
cp scripts/msg_status.py %{buildroot}%_datadir/apel/

# client logrotate script
cp scripts/apel-client %{buildroot}%{_sysconfdir}/logrotate.d

%clean
rm -rf $RPM_BUILD_ROOT

%pre server
# Create the apel user if it doesn't exist
getent passwd apel >/dev/null || \
    useradd -r apel
exit 0

# ==============================================================================

%files lib
%defattr(-,root,root,-)

%{python_sitelib}/apel

# ------------------------------------------------------------------------------

%files parsers
%defattr(-,root,root,-)

%attr(755,root,root) %_bindir/apelparser

%config(noreplace) %attr(600,-,-) %{apelconf}/parser.cfg

%attr(755,root,root) %_datadir/apel/slurm_acc.sh
%attr(755,root,root) %_datadir/apel/htcondor_acc.sh

# ------------------------------------------------------------------------------

%files client
%defattr(-,root,root,-)

%_datadir/apel/client.sql
# Directories for logs, PID files
%dir %{_localstatedir}/log/apel
%dir %{_localstatedir}/run/apel

%attr(755,root,root) %_bindir/apelclient

%config(noreplace) %attr(600,-,-) %{apelconf}/client.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/apel-client

# ------------------------------------------------------------------------------

%files server
%defattr(-,root,root,-)

%_datadir/apel/server.sql
%_datadir/apel/server-extra.sql
%_datadir/apel/cloud.sql
%_datadir/apel/storage.sql
# Include all update scripts by wildcard matching
%_datadir/apel/update-*.sql

%attr(755,root,root) %_datadir/apel/msg_status.py
%exclude %_datadir/apel/msg_status.pyc
%exclude %_datadir/apel/msg_status.pyo

# Directories for logs, PID files
%dir %{_localstatedir}/log/apel
%dir %{_localstatedir}/run/apel

%attr(755,root,root) %_bindir/apeldbunloader
%attr(755,root,root) %_bindir/apeldbloader
%attr(755,root,root) %_bindir/apelsummariser
%attr(755,root,root) %_bindir/apelauth

%config(noreplace) %{apelconf}/summariser.cfg
%config(noreplace) %{apelconf}/unloader.cfg
%config(noreplace) %{apelconf}/loader.cfg
%config(noreplace) %attr(600,apel,apel) %{apelconf}/db.cfg
%config(noreplace) %{apelconf}/auth.cfg

# ==============================================================================

%changelog
 * Fri Mar 19 2021 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.9.0-1
 - [client] Added AMS support. Requires at least SSM version 3.2.0.
 - [server] Added ability to alter the number of records unloaded per message.
 - [server] Added logging of the record type being loaded.
 - Added python-dirq to RPM package dependencies.
 - Fixed mistake in storage accounting schema.
 - Added linting to RPM build process.

 * Mon Aug 19 2019 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.8.2-1
 - [server] Tweaked how cloud records are loaded so that the last received
   record for a VM in a month is kept (rather than the one with the latest
   timestamp). This simplifies things when sites republish cloud VM accounting.

 * Wed Jul 03 2019 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.8.1-1
 - [client] Added option to update benchmarks/spec levels using a local
   configuration option rather than the BDII.

 * Mon Jan 07 2019 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.8.0-1
 - [client] Added warning in log if no records are unloaded during a run.
 - [parsers] Added optional 'cputmult' factor to HTCondor parser to support its
   use as a parser for HTCondorCE set ups.
 - [server] Added PID/process check to summariser to prevent overlapping runs.

 * Thu Nov 29 2018 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.7.1-1
 - [parsers] Added support for SLURM parser to use TotalCPU rather than
   CPUTimeRAW for CPU duration and updated suggested sacct script to match.
 - Minor improvements to build process and setup.py script.

 * Tue Jun 05 2018 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.7.0-1
 - [server] Long running VM support: Cloud VMs that run over month boundaries
   will now have their usage in each month assigned to the correct month.

 * Mon Apr 16 2018 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.6.2-1
 - [parsers] Added remaining job statuses for SLURM that indicate the job has
   stopped and that resources have been used.
 - [server] Fix CpuCount being NULL in cloud accounting records and leading to
   warnings when summarising.
 - [docs] Remove references to specific LSF versions as all now allowed.

 * Thu Dec 14 2017 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.6.1-1
 - [parsers] Removed version restriction from LSF parser so that it can
   additionally work with version 10 onwards.
 - Added more columns to cloud summaries primary key to prevent mis-grouping.
 - Added Python setup script to enable installation on non-RHEL-based systems.
 - Made the updating of record timestamps in the database explicit.
 - Added type checking to float and datetime fields in the Python code.

 * Fri Mar 10 2017 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.6.0-1
 - Added support for mixed time formats used in Torque 5.1.3.
 - Changed the way core count is parsed to support Torque 5.1.0.
 - Added CPU count to cloud accounting summaries.
 - Added support for cloud accounting schema v0.4 format records.
 - Added SQL file to update cloud schema.
 - Removed file attribute args from the create directive in logrotate script.
 - Fixed crashes of storage accounting loader due to newer format records.
 - Added support for paged GOCDB API results.
 - Disabled duplicate sites check in server summarising process.
 - Updated partitioning in server-extra.sql.

 * Tue Jan 12 2016 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.5.1-1
 - Add support for Torque 5.1.2 time duration format.
 - Change dirq call to use absolute path to support versions of dirq >= 1.7.
 - Fix crash when StAR loader encouters a valid XML file with no records in it.

 * Tue Jul 14 2015 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.5.0-1
 - Added sorting of accounting logs before parsing which makes reading through
   the parser log easier, especially if files use the YYYYMMDD date format.
 - Added the first version of a basic HTCondor parser.
 - Fixed the server schema to correctly aggregate super summaries when
   viewed as normalised super summaries.

 * Thu Mar 12 2015 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.4.1-1
 - Changed defaults so that parallel jobs are reported for new installations.
 - Corrected year calculation in migrate_apel.py script.

 * Mon Mar 02 2015 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.4.1-0.1.rc1
 - Added an option to the batch configuration section to allow for the
   millisecond timestamps introduced in Univa Grid Engine version 8.2.0.
 - Improved logging output to make it more useful to APEL servers when tracing
   messages.

 * Thu Jan 29 2015 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.4.0-1
 - (No changes from pre-release version.)

 * Thu Jan 29 2015 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.4.0-0.1.rc1
 - Added ability to process files compressed with bzip2.
 - Added multiplier retrieval to GridEngine parser for CPU and wall-clock time.
 - Fixed integer overflow when loading normalised summaries into APEL servers.
 - Corrected the way some logging calls were made and reduced the logging level
   when trying to purge a directory that isn't empty.
 - Changed server authorization system to keep the list of DNs for a limited
   time if unable to update from GOCDB and updated GOCDB query URL.
 - Added Month and Year columns to primary key of CloudSummaries table in cloud
   schema.

 * Tue Nov 04 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.1-1
 - (No changes from pre-release version.)

 * Wed Oct 22 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.1-0.3.beta1
 - Corrected the handling of muliple FQANs in blah logs so that the role and
   group are taken from the first (i.e. primary) FQAN rather than the last.
 - Fixed a crash that occurred when the parser encountered an empty file.
 - Added support for parsing fractional seconds in XML usage records.
 - Fixed database loader crash when save_messages was set to false.
 - Added options to unloader.conf to allow the unloader to unload more than just
   the current and previous months.

 * Tue Jul 15 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-1
 - Added in a missing database view that the central APEL server uses.

 * Thu Jul 03 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-0.4.rc3
 - Added partitioning statement to schema used by central APEL server.

 * Thu Jul 03 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-0.3.rc2
 - Corrections made to server schema to avoid warnings about default values not
   being set.
 - Added missing file to rpmbuild spec file.

 * Mon Jun 30 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-0.2.rc1
 - Added support for APEL servers to be sent normalised summaries using the new
   summary job record format (v0.3).
 - Some views used by the central APEL server, which shouldn't be needed by
   regional servers, have been separated out into server-extra.sql.

 * Fri Aug 15 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.2.2-1
 - Fixed being unable to parse uncompressed accounting logs.

 * Thu Jul 24 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.2.1-1
 - (No changes from pre-release version.)

 * Thu Jul 24 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.2.1-0.1.rc1
 - Changed parsers to handle short FQANS properly.
 - Added a logratate script for client.log. 'apel-client' will be installed to
   the logrotate.d directory.

 * Mon Jun 30 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.2.0-5
 - Updates made to rpmbuild spec file to support new versioning scheme.

 * Thu Jun 26 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.2.0-1
 - Added support for version 9 LSF batch logs to LSF parser.
 - Improved input checking for SLURM and PBS parsers.
 - Improved message handling for regional servers and central APEL server.
 - When parsed files are skipped the log message now gives a clearer reason.
 - Corrected line numbers in 'skipping' log messages which were 1 less than the
   actual value. (Also affects StopLine column of ProcessedFiles table).

 * Wed Dec 11 2013 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.1.3-0
 - Added catch for xml parser exceptions to fix db loader crash.
 - Changed SLURM parser to handle times greater than a day and unit prefixes
   greater than K.
 - Added ORDER BY NULL to GROUP BY queries to improve performance.
 - Changed client.py to fetch site_name if joiner is enabled to fix crash.

 * Fri May 31 2013 Stuart Pullinger <stuart.pullinger@stfc.ac.uk> - 1.1.2-0
 - Changed file permissions for parser.cfg, client.cfg and db.cfg
   to 0600, owner and group of db.cfg to apel:apel, in apel.spec

 * Mon Apr 29 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.1.1-0
 - Separate summarising procedure into component parts and use
   relevant parts for client.py and summariser.py scripts

 * Tue Apr 16 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.1.0-0
 - Option to withhold DNs when sending messages
 - Update and enable SLURM parser
 - Enable parser to reprocess event records
 - Fixes to cloud summaries

 * Wed Mar 20 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.0.5-0
 - Create, send and receive cloud summaries
 - Parse FQAN information and add to CloudRecords table
 - Refactor client script and simplify configuration
 - First version of SLURM parser (thanks to Lisa Zangrando)
 - First version of msg_status script

 * Thu Mar 07 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.0.4-0
 - Change primary key on server JobRecords

 * Wed Feb 27 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.0.3-0
 - Enable saving accepted messages in dbloader
 - Use python-iso8601 for parsing datetimes
 - Fixed crash when parsing empty files
 - Corrections to CAR syntax
 - Fix include_vos and exclude_vos in dbunloader

 * Wed Feb 20 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.0.2-0
 - Correct VHepSpecHistory view
 - Correct handling of omitted Processors, NodeCount info

 * Thu Feb 14 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.0.1-0
 - Remove unnecessary dbld file
 - Handle incorrect BDII value for CPUScalingReference

 * Sat Jan 26 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 1.0.0-0
 - More defensive handling of configuration
 - First release of new apel

 * Thu Jan 24 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.5-0
 - Client and parser scripts rewritten to be more logical and simpler
 - Use INSERT IGNORE for log file records instead of REPLACE
 - Change sync records to reflect any VO or local job filtering
 - Make MPI parsing optional

 * Wed Jan 16 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.4-0
 - Updated to use new cloud schema and message format

 * Thu Jan 10 2013 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.3-0
 - Loader accepts StAR messages, database updated
 - Move to using one specfile, hyphenated rpm names
 - Stored procedure improvements

 * Thu Dec 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.2-0
 - Correct database logic.  Improve logging.

 * Tue Nov 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.1-0
 - First tag
