Name:           apel
Version:        0.0.3
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
apellib provides required libraries for the rest of APEL system. 

%package parsers
Summary:        Parsers for APEL system
Group:          Development/Languages
Requires:       apellib
Requires(pre):  shadow-utils

%description parsers
The apel parsers package contains parsers for all the batch systems
supported by the APEL system: Torque, SGE and LSF. 

%package client
Summary:		APEL client package
Group:          Development/Languages
Requires:       apellib apelssm
Requires(pre):  shadow-utils

%description client
The apel client package contains all code needed to retrieve data from 
the accounting database, process it and send it to the apel server using 
SSM.

%package server
Summary:		APEL server package
Group:          Development/Languages
Requires:       apellib apelssm
Requires(pre):  shadow-utils

%description server
ApelServer package contains all code needed to receive accounting data
from clients, to process and to send the results to webportal.

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf $RPM_BUILD_ROOT

# Create directories
mkdir -p %{buildroot}%{apelconf}
mkdir -p %{buildroot}%_bindir
mkdir -p %{buildroot}%_sysconfdir/logrotate.d
mkdir -p %{buildroot}%_datadir/apel
mkdir -p %{buildroot}%_defaultdocdir
# Directories for logs, PID files
mkdir -p %{buildroot}%{_localstatedir}/log/apel
mkdir -p %{buildroot}%{_localstatedir}/run/apel

# Scripts
cp bin/client.py %{buildroot}%_bindir/apelclient
cp bin/parser.py %{buildroot}%_bindir/apelparser
cp bin/dbloader.py %{buildroot}%_bindir/dbloader
cp bin/dbunloader.py %{buildroot}%_bindir/dbunloader
cp bin/summariser.py %{buildroot}%_bindir/summariser
cp init.d/dbld %{buildroot}%{_initrddir}

# Configuration files
cp conf/client.cfg %{buildroot}%{apelconf}
cp conf/summariser.cfg %{buildroot}%{apelconf}/
cp conf/unloader.cfg %{buildroot}%{apelconf}/
cp conf/loader.cfg %{buildroot}%{apelconf}/
cp conf/db.cfg %{buildroot}%{apelconf}/
cp conf/parser.cfg %{buildroot}%{apelconf}/

# database schemas
cp schemas/client.sql %{buildroot}%_datadir/apel/client.sql
cp schemas/server.sql %{buildroot}%_datadir/apel/
cp schemas/cloud.sql %{buildroot}%_datadir/apel/
cp schemas/storage.sql %{buildroot}%_datadir/apel/

%clean 
rm -rf $RPM_BUILD_ROOT

%pre client
# Create the apel user if it doesn't exist
getent passwd apel >/dev/null || \
    useradd -r apel
exit 0

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
%attr(755,-,-) %_bindir/apelparser
%config(noreplace) %{apelconf}/parser.cfg

%files client
%defattr(-,root,root,-)

%_datadir/apel/client.sql
# Directories for logs, PID files
%dir %{_localstatedir}/log/apel
%dir %{_localstatedir}/run/apel

%attr(755,-,-) %_bindir/apelclient

%config(noreplace) %{apelconf}/client.cfg

%files server
%defattr(-,root,root,-)

%_datadir/apel/server.sql
%_datadir/apel/cloud.sql
%_datadir/apel/storage.sql
# Directories for logs, PID files
%dir %attr(644,apel,apel) %{_localstatedir}/log/apel
%dir %attr(644,apel,apel) %{_localstatedir}/run/apel

%attr(755,-,-) %_bindir/dbunloader
%attr(755,-,-) %_bindir/dbloader
%attr(755,-,-) %_bindir/summariser

# Init script
%attr(755,root,root) %{_initrddir}/dbld

%config(noreplace) %{apelconf}/summariser.cfg
%config(noreplace) %{apelconf}/unloader.cfg
%config(noreplace) %{apelconf}/loader.cfg
%config(noreplace) %{apelconf}/db.cfg

%changelog
 * Tue Nov 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.1-0
 - First release

 * Thu Dec 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.2-0
 - Correct database logic.  Improve logging.

