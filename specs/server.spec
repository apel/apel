Name:           apelserver
Version:        0.0.1
Release:        0%{?dist}
Summary:        Package with software for APEL Server

Group:          Development/Languages
License:        ASL 2.0
URL:            https://wiki.egi.eu/wiki/APEL
Source0:        apel2-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       apellib apelssm
Requires(pre):  shadow-utils

%define apelconf %_sysconfdir/apel

%description
ApelServer package contains all code needed to receive accounting data
from clients, to process and to send the results to webportal.

Code is written in Python. This RPM package is designed
for SL 5.

%prep
%setup -q -n apel2-%{version}

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
mkdir -p %{buildroot}%{_initrddir}

# Scripts
cp bin/dbloader.py %{buildroot}%_bindir/dbloader
cp bin/dbunloader.py %{buildroot}%_bindir/dbunloader
cp bin/summariser.py %{buildroot}%_bindir/summariser
cp init.d/dbld %{buildroot}%{_initrddir}

# Configuration files
cp conf/summariser.cfg %{buildroot}%{apelconf}/
cp conf/unloader.cfg %{buildroot}%{apelconf}/
cp conf/loader.cfg %{buildroot}%{apelconf}/
cp conf/db.cfg %{buildroot}%{apelconf}/

# database schema
cp schemas/server.sql %{buildroot}%_datadir/apel/
cp schemas/cloud.sql %{buildroot}%_datadir/apel/
cp schemas/storage.sql %{buildroot}%_datadir/apel/


%clean 
rm -rf $RPM_BUILD_ROOT

%pre

# Create the apel user if it doesn't exist
getent passwd apel >/dev/null || \
    useradd -r apel
exit 0

%files
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
 * Tue Nov 20 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.0-1
 - First release
