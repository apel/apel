# Conditionally define python_sitelib
%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:           apel
Version:        1.3.0
Release:        1%{?dist}
Summary:        APEL packages

Group:          Development/Languages
License:        ASL 2.0
URL:            https://wiki.egi.eu/wiki/APEL
# Value between %{version} and extension must match "Release" without %{dist}
Source:         %{name}-%{version}-1.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

%define apelconf %_sysconfdir/apel

%description
The apel packages. 
The project is written in Python. 

%package lib
Summary:        Libraries required for Apel Client, Server and Parsers
Group:          Development/Languages
Requires:       MySQL-python python-ldap python-iso8601
Requires(pre):  shadow-utils

%description lib
apel-lib provides required libraries for the rest of APEL system. 

%package parsers
Summary:        Parsers for APEL system
Group:          Development/Languages
Requires:       apel-lib >= 1.3.0
Requires(pre):  shadow-utils

%description parsers
The apel-parsers package contains parsers for all the batch systems
supported by the APEL system: Torque, SGE and LSF. 

%package client
Summary:        APEL client package
Group:          Development/Languages
Requires:       apel-lib >= 1.3.0, apel-ssm
Requires(pre):  shadow-utils

%description client
The apel-client package contains all code needed to retrieve data from 
the accounting database, process it and send it to the apel server using 
SSM.

%package server
Summary:        APEL server package
Group:          Development/Languages
Requires:       apel-lib >= 1.3.0, apel-ssm
Requires(pre):  shadow-utils

%description server
The apel-server package contains all code needed to receive accounting data
from clients, to process and to send the results elsewhere using SSM.

%prep
# Value after %{version} must match "Release" without %{dist}
%setup -q -n %{name}-%{version}-1

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

# slurm accounting script
cp scripts/slurm_acc.sh %{buildroot}%_datadir/apel/

# message status script
cp scripts/msg_status.py %{buildroot}%_datadir/apel/

%clean 
rm -rf $RPM_BUILD_ROOT

%pre server
# Create the apel user if it doesn't exist
getent passwd apel >/dev/null || \
    useradd -r apel
exit 0

%files lib
%defattr(-,root,root,-)
%{python_sitelib}/apel

%files parsers
%defattr(-,root,root,-)
%attr(755,root,root) %_bindir/apelparser
%config(noreplace) %{apelconf}/parser.cfg
%attr(600,-,-) %{apelconf}/parser.cfg
%attr(755,root,root) %_datadir/apel/slurm_acc.sh

%files client
%defattr(-,root,root,-)

%_datadir/apel/client.sql
# Directories for logs, PID files
%dir %{_localstatedir}/log/apel
%dir %{_localstatedir}/run/apel

%attr(755,root,root) %_bindir/apelclient

%config(noreplace) %{apelconf}/client.cfg
%attr(600,-,-) %{apelconf}/client.cfg

%files server
%defattr(-,root,root,-)

%_datadir/apel/server.sql
%_datadir/apel/server-extra.sql
%_datadir/apel/cloud.sql
%_datadir/apel/storage.sql
%attr(755,root,root) %_datadir/apel/msg_status.py

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
%config(noreplace) %{apelconf}/db.cfg
%attr(600,apel,apel) %{apelconf}/db.cfg
%config(noreplace) %{apelconf}/auth.cfg

%changelog
 * Tue Jul 15 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-1
 - Added in a missing database view that the central APEL server uses.

 * Thu Jul 03 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-0.4.rc3
 - Add partitioning statement to schema used by central APEL server.

 * Thu Jul 03 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-0.3.rc2
 - Corrections made to server schema to avoid warnings about default values not
   being set.
 - Added missing file to rpmbuild spec file.

 * Mon Jun 30 2014 Adrian Coveney <adrian.coveney@stfc.ac.uk> - 1.3.0-0.2.rc1
 - Added support for APEL servers to be sent normalised summaries using the new
   summary job record format (v0.3).
 - Some views used by the central APEL server, which shouldn't be needed by
   regional servers, have been separated out into server-extra.sql.

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

