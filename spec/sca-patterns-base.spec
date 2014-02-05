# spec file for package sca-patterns-base
#
# Copyright (C) 2014 SUSE LLC
#
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#

# norootforbuild
# neededforbuild

%define sca_common sca
%define patdirbase /usr/lib/%{sca_common}
%define patdir %{patdirbase}/patterns
%define prodgrp sdp
%define patuser root
%define patgrp root

Name:         sca-patterns-base
Summary:      Supportconfig Analysis Pattern Base Libraries
URL:          https://bitbucket.org/g23guy/sca-patterns-base
Group:        Documentation/SuSE
License:      GPL-2.0
Autoreqprov:  on
Version:      1.3
Release:      4
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
install -d $RPM_BUILD_ROOT/%{patdirbase}/patterns/local
install -d $RPM_BUILD_ROOT/%{patdirbase}/bash
install -d $RPM_BUILD_ROOT/%{patdirbase}/python
install -d $RPM_BUILD_ROOT/%{patdirbase}/perl/SDP
install -m 644 libraries/bash/* $RPM_BUILD_ROOT/%{patdirbase}/bash
install -m 644 libraries/python/* $RPM_BUILD_ROOT/%{patdirbase}/python
install -m 644 libraries/perl/SDP/* $RPM_BUILD_ROOT/%{patdirbase}/perl/SDP

%files
%defattr(-,%{patuser},%{patgrp})
%dir %{patdirbase}
%dir %{patdir}
%dir %{patdir}/local
%dir %{patdirbase}/bash
%dir %{patdirbase}/python
%dir %{patdirbase}/perl
%dir %{patdirbase}/perl/SDP
%attr(-,%{patuser},%{patgrp}) %{patdirbase}/bash/*
%attr(-,%{patuser},%{patgrp}) %{patdirbase}/python/*
%attr(-,%{patuser},%{patgrp}) %{patdirbase}/perl/SDP/*

%clean
rm -rf $RPM_BUILD_ROOT

%changelog

