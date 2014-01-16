# Copyright (C) 2013 SUSE LLC
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#

# norootforbuild
# neededforbuild

%define sca_common sca
%define prodgrp sdp
%define patuser root
%define patgrp root
%define patdirbase /usr/lib/%{sca_common}
%define patdir %{patdirbase}/patterns
%define patlib %{patdir}/lib

Name:         sca-patterns-base
Summary:      Supportconfig Analysis Pattern Base Libraries
URL:          https://bitbucket.org/g23guy/sca-patterns-base
Group:        Documentation/SuSE
Distribution: SUSE Linux Enterprise
Vendor:       SUSE Support
License:      GPL-2.0
Autoreqprov:  on
Version:      1.3
Release:      0
Source:       %{name}-%{version}.tar.gz
BuildRoot:    %{_tmppath}/%{name}-%{version}
Buildarch:    noarch
Requires:     python
Requires:     bash
Requires:     perl
%description
Supportconfig Analysis (SCA) appliance pattern base libraries used 
by all patterns

Authors:
--------
    Jason Record <jrecord@suse.com>

%prep
%setup -q

%build

%install
pwd;ls -la
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/%{patdir}/local
install -d $RPM_BUILD_ROOT/%{patlib}/bash
install -d $RPM_BUILD_ROOT/%{patlib}/python
install -d $RPM_BUILD_ROOT/%{patlib}/perl/SDP
install -m 644 patterns/lib/bash/* $RPM_BUILD_ROOT/%{patlib}/bash
install -m 644 patterns/lib/python/* $RPM_BUILD_ROOT/%{patlib}/python
install -m 644 patterns/lib/perl/SDP/* $RPM_BUILD_ROOT/%{patlib}/perl/SDP

%files
%defattr(-,%{patuser},%{patgrp})
%dir %{patdirbase}
%dir %{patdir}
%dir %{patdir}/local
%dir %{patlib}
%dir %{patlib}/bash
%dir %{patlib}/python
%dir %{patlib}/perl
%dir %{patlib}/perl/SDP
%attr(-,%{patuser},%{patgrp}) %{patdir}/lib/bash/*
%attr(-,%{patuser},%{patgrp}) %{patdir}/lib/python/*
%attr(-,%{patuser},%{patgrp}) %{patdir}/lib/perl/SDP/*

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Thu Jan 16 2014 jrecord@suse.com
- relocated files according to FHS
- added Xen.py library
- added pydoc elements to python libraries for documentation
- added STATUS_IGNORE to all Core libraries

* Wed Jan 08 2014 jrecord@suse.com
- fixed build errors

* Thu Jan 02 2014 jrecord@suse.com
- moved pat to sca-appliance-patdev

* Wed Dec 20 2013 jrecord@suse.com
- separated as individual RPM package

