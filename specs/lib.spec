# Conditionally define python_sitelib
%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:           apellib
Version:        0.0.3
Release:        0%{?dist}
Summary:        Libraries required for Apel Client, Server and Parsers

Group:          Development/Languages
License:        ASL 2.0
URL:            https://wiki.egi.eu/wiki/APEL
Source0:        apel2-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       MySQL-python python-ldap
Requires(pre):  shadow-utils

%description
apellib provides required libraries for the rest of APEL system. 

The project is written in Python. 

%prep
%setup -q -n apel2-%{version}

%install
rm -rf $RPM_BUILD_ROOT

# Create directories
mkdir -p %{buildroot}%{python_sitelib}/apel
mkdir -p %{buildroot}%_defaultdocdir

# Library
cp -fr apel/* %{buildroot}%{python_sitelib}/apel

%clean 
rm -rf $RPM_BUILD_ROOT

%pre

%files
%defattr(-,root,root,-)
%{python_sitelib}/apel

%changelog
 * Tue Nov 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.1-0
 - First release

 * Wed Dec 13 2012 Will Rogers <will.rogers@stfc.ac.uk>  - 0.0.2-0
 - Change datatype handling.  Add cloud functionality.
