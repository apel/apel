Name:           apelclient
Version:        0.0.2
Release:        0%{?dist}
Summary:        APEL Client package

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
The apel client package contains all code needed to retrieve data from 
the accounting database, process it and send it to the apel server using 
SSM.

This is a python package. 

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

# Scripts
cp bin/client.py %{buildroot}%_bindir/apelclient

# Configuration files
cp conf/client.cfg %{buildroot}%{apelconf}

# database schema
cp schemas/client.sql %{buildroot}%_datadir/apel/client.sql

%clean 
rm -rf $RPM_BUILD_ROOT

%pre

# Create the apel user if it doesn't exist
getent passwd apel >/dev/null || \
    useradd -r apel
exit 0

%files
%defattr(-,root,root,-)

%_datadir/apel/client.sql
# Directories for logs, PID files
%dir %{_localstatedir}/log/apel
%dir %{_localstatedir}/run/apel


%attr(755,-,-) %_bindir/apelclient

%config(noreplace) %{apelconf}/client.cfg

%changelog
 * Tue Nov 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.1-0
 - First release

 * Thu Dec 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.2-0
 - Correct database logic.  Improve logging.

