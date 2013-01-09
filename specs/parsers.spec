Name:           apelparsers
Version:        0.0.3
Release:        0%{?dist}
Summary:        Parsers for APEL system

Group:          Development/Languages
License:        ASL 2.0
URL:            https://wiki.egi.eu/wiki/APEL
Source0:        apel2-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       apellib
Requires(pre):  shadow-utils

%define apelconf %_sysconfdir/apel

%description
The apel parsers package contains parsers for all the batch systems
supported by the APEL system: Torque, SGE and LSF. 

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
# Directories for logs, PID files
mkdir -p %{buildroot}%{_localstatedir}/log/apel
mkdir -p %{buildroot}%{_localstatedir}/run/apel

# Scripts
cp bin/parser.py %{buildroot}%_bindir/apelparser

# Configuration files
cp conf/parser.cfg %{buildroot}%{apelconf}/

%clean 
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)

%attr(755,-,-) %_bindir/apelparser

%config(noreplace) %{apelconf}/parser.cfg

%changelog
 * Fri Nov 16 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.1-0
 - First release

 * Wed Dec 16 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.2-0
 - No major changes.
