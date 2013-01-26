# Conditionally define python_sitelib
%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:           apel
Version:        1.0.0
Release:        0%{?dist}
Summary:        APEL packages

Group:          Development/Languages
License:        ASL 2.0
URL:            https://wiki.egi.eu/wiki/APEL
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

%define apelconf %_sysconfdir/apel

%description
The apel packages. 
The project is written in Python. 

%package lib
Summary:        Libraries required for Apel Client, Server and Parsers
Group:          Development/Languages
Requires:       MySQL-python python-ldap
Requires(pre):  shadow-utils

%description lib
apel-lib provides required libraries for the rest of APEL system. 

%package parsers
Summary:        Parsers for APEL system
Group:          Development/Languages
Requires:       apel-lib
Requires(pre):  shadow-utils

%description parsers
The apel-parsers package contains parsers for all the batch systems
supported by the APEL system: Torque, SGE and LSF. 

%package client
Summary:		APEL client package
Group:          Development/Languages
Requires:       apel-lib apel-ssm
Requires(pre):  shadow-utils

%description client
The apel-client package contains all code needed to retrieve data from 
the accounting database, process it and send it to the apel server using 
SSM.

%package server
Summary:		APEL server package
Group:          Development/Languages
Requires:       apel-lib apel-ssm
Requires(pre):  shadow-utils

%description server
The apel-server package contains all code needed to receive accounting data
from clients, to process and to send the results elsewhere using SSM.

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf $RPM_BUILD_ROOT

# Create directories
mkdir -p %{buildroot}%{apelconf}
mkdir -p %{buildroot}%_bindir
mkdir -p %{buildroot}%{python_sitelib}/apel
mkdir -p %{buildroot}%{_initrddir}
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
cp init.d/dbld %{buildroot}%{_initrddir}

# Configuration files
cp conf/client.cfg %{buildroot}%{apelconf}
cp conf/summariser.cfg %{buildroot}%{apelconf}/
cp conf/unloader.cfg %{buildroot}%{apelconf}/
cp conf/loader.cfg %{buildroot}%{apelconf}/
cp conf/db.cfg %{buildroot}%{apelconf}/
cp conf/parser.cfg %{buildroot}%{apelconf}/

# database schemas
cp schemas/client.sql %{buildroot}%_datadir/apel/
cp schemas/server.sql %{buildroot}%_datadir/apel/
cp schemas/cloud.sql %{buildroot}%_datadir/apel/
cp schemas/storage.sql %{buildroot}%_datadir/apel/

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

%files client
%defattr(-,root,root,-)

%_datadir/apel/client.sql
# Directories for logs, PID files
%dir %{_localstatedir}/log/apel
%dir %{_localstatedir}/run/apel

%attr(755,root,root) %_bindir/apelclient

%config(noreplace) %{apelconf}/client.cfg

%files server
%defattr(-,root,root,-)

%_datadir/apel/server.sql
%_datadir/apel/cloud.sql
%_datadir/apel/storage.sql
# Directories for logs, PID files
%dir %{_localstatedir}/log/apel
%dir %{_localstatedir}/run/apel

%attr(755,root,root) %_bindir/apeldbunloader
%attr(755,root,root) %_bindir/apeldbloader
%attr(755,root,root) %_bindir/apelsummariser

# Init script
%attr(755,root,root) %{_initrddir}/dbld

%config(noreplace) %{apelconf}/summariser.cfg
%config(noreplace) %{apelconf}/unloader.cfg
%config(noreplace) %{apelconf}/loader.cfg
%config(noreplace) %{apelconf}/db.cfg

%changelog
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

