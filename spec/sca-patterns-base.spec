#
# spec file for package sca-patterns-base (Version 1.1)
#
# Copyright (C) 2013 SUSE LLC
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#

# norootforbuild
# neededforbuild

%define produser sca
%define prodgrp sdp
%define patuser root
%define patgrp root
%define patdir /var/opt/%{produser}/patterns

Name:         sca-patterns-base
Summary:      Supportconfig Analysis Pattern Base Libraries
Group:        Documentation/SuSE
Distribution: SUSE Linux Enterprise
Vendor:       SUSE Support
License:      GPLv2
Autoreqprov:  on
Version:      1.1
Release:      1
Source:       %{name}-%{version}.tar.gz
BuildRoot:    %{_tmppath}/%{name}-%{version}
Buildarch:    noarch
Requires:     python
Requires:     bash
Requires:     perl
%description
Supportconfig Analysis (SCA) appliance pattern base libraries used 
by all patterns, including pattern development tools

Authors:
--------
    Jason Record <jrecord@suse.com>

%files
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/lib
%dir %{patdir}/lib/bash
%dir %{patdir}/lib/python
%dir %{patdir}/lib/perl
%dir %{patdir}/lib/perl/SDP
%dir %{patdir}/local
%attr(-,%{patuser},%{patgrp}) %{patdir}/lib/bash/*
%attr(-,%{patuser},%{patgrp}) %{patdir}/lib/python/*
%attr(-,%{patuser},%{patgrp}) %{patdir}/lib/perl/SDP/*
/usr/bin/*

%prep
%setup -q

%build
make build

%install
make install

%changelog
* Wed Dec 18 2013 jrecord@suse.com
- separted into individual package

