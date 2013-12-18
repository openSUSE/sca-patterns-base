#
# spec file for package scdiag (Version 1.0)
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

Name:         sca-patterns
Summary:      Supportconfig Analysis Patterns
Group:        Documentation/SuSE
Distribution: SUSE Linux Enterprise
Vendor:       SUSE Support
License:      GPLv2
Autoreqprov:  on
Version:      1.0
Release:      1
Source:       %{name}-%{version}.tar.gz
BuildRoot:    %{_tmppath}/%{name}-%{version}
Buildarch:    noarch
%description
Patterns that identify known issues and used by the sca-agent 
package

Authors:
--------
    Jason Record <jrecord@suse.com>

##################################################################
# Pattern Base Libraries
##################################################################

%package base
Summary:      Supportconfig Analysis Pattern Base Libraries
Group:        Documentation/SuSE
Release:      1
Requires:     python
Requires:     bash
Requires:     perl
%description base
Supportconfig Analysis (SCA) appliance pattern base libraries used 
by all patterns

Authors:
--------
    Jason Record <jrecord@suse.com>

%files base
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

##################################################################
# Basic SLE Health Check Patterns
##################################################################

%package Basic
Summary:      Supportconfig Analysis Patterns for SLE Basic Health
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description Basic
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to basic health issues

Authors:
--------
    Jason Record <jrecord@suse.com>

%files Basic
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/Basic
%attr(555,%{patuser},%{patgrp}) %{patdir}/Basic/*

##################################################################
# SLES/SLED All Patterns
##################################################################

%package SLEALL
Summary:      Supportconfig Analysis Patterns for all SLE
Group:        Documentation/SuSE
Release:      1.2
Requires:     %{name}-base
%description SLEALL
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of SLES/SLED

Authors:
--------
    Jason Record <jrecord@suse.com>

%files SLEALL
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/SLE
%dir %{patdir}/SLE/all
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/all/*

##################################################################
# SLES/SLED 11 Patterns
##################################################################

%package SLE11
Summary:      Supportconfig Analysis Patterns for SLE11
Group:        Documentation/SuSE
Release:      1.2
Requires:     %{name}-base
%description SLE11
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of SLES/SLED 11

Authors:
--------
    Jason Record <jrecord@suse.com>

%files SLE11
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/SLE
%dir %{patdir}/SLE/sle11all
%dir %{patdir}/SLE/sle11sp0
%dir %{patdir}/SLE/sle11sp1
%dir %{patdir}/SLE/sle11sp2
%dir %{patdir}/SLE/sle11sp3
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle11all/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle11sp0/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle11sp1/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle11sp2/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle11sp3/*

##################################################################
# SLES/SLED 10 Patterns
##################################################################

%package SLE10
Summary:      Supportconfig Analysis Patterns for SLE10
Group:        Documentation/SuSE
Release:      1.1
Requires:     %{name}-base
%description SLE10
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of SLES/SLED 10

Authors:
--------
    Jason Record <jrecord@suse.com>

%files SLE10
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/SLE
%dir %{patdir}/SLE/sle10all
%dir %{patdir}/SLE/sle10sp0
%dir %{patdir}/SLE/sle10sp1
%dir %{patdir}/SLE/sle10sp2
%dir %{patdir}/SLE/sle10sp3
%dir %{patdir}/SLE/sle10sp4
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle10all/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle10sp0/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle10sp1/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle10sp2/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle10sp3/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle10sp4/*

##################################################################
# SLES/SLED 9 Patterns
##################################################################

%package SLE09
Summary:      Supportconfig Analysis Patterns for SLE9
Group:        Documentation/SuSE
Release:      1.1
Requires:     %{name}-base
%description SLE09
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of SLES/SLED 9

Authors:
--------
    Jason Record <jrecord@suse.com>

%files SLE09
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/SLE
%dir %{patdir}/SLE/all
%dir %{patdir}/SLE/sle9all
%attr(555,%{patuser},%{patgrp}) %{patdir}/SLE/sle9all/*

##################################################################
# OES 11 Patterns
##################################################################

%package OES
Summary:      Supportconfig Analysis Patterns for OES
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description OES
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of Open Enterprise Server (OES)

Authors:
--------
    Jason Record <jrecord@suse.com>

%files OES
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/OES
%dir %{patdir}/OES/all
%dir %{patdir}/OES/oes11all
%dir %{patdir}/OES/oes1all
%dir %{patdir}/OES/oes2all
%dir %{patdir}/OES/oes2sp3
%attr(555,%{patuser},%{patgrp}) %{patdir}/OES/all/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/OES/oes11all/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/OES/oes1all/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/OES/oes2all/*
%attr(555,%{patuser},%{patgrp}) %{patdir}/OES/oes2sp3/*

##################################################################
# eDirectory Patterns
##################################################################

%package eDirectory
Summary:      Supportconfig Analysis Patterns for eDirectory
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description eDirectory
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of eDirectory

Authors:
--------
    Jason Record <jrecord@suse.com>

%files eDirectory
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/eDirectory
%attr(555,%{patuser},%{patgrp}) %{patdir}/eDirectory/*

##################################################################
# Filr Patterns
##################################################################

%package Filr
Summary:      Supportconfig Analysis Patterns for Filr
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description Filr
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of Filr

Authors:
--------
    Jason Record <jrecord@suse.com>

%files Filr
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/Filr
%attr(555,%{patuser},%{patgrp}) %{patdir}/Filr/*

##################################################################
# GroupWise Patterns
##################################################################

%package GroupWise
Summary:      Supportconfig Analysis Patterns for GroupWise
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description GroupWise
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of GroupWise

Authors:
--------
    Jason Record <jrecord@suse.com>

%files GroupWise
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/GroupWise
%attr(555,%{patuser},%{patgrp}) %{patdir}/GroupWise/*

##################################################################
# HAE Patterns
##################################################################

%package HAE
Summary:      Supportconfig Analysis Patterns for HAE
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description HAE
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of High Availability Extension (HAE)
clustering

Authors:
--------
    Jason Record <jrecord@suse.com>

%files HAE
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/HAE
%attr(555,%{patuser},%{patgrp}) %{patdir}/HAE/*

##################################################################
# NCS Patterns
##################################################################

%package NCS
Summary:      Supportconfig Analysis Patterns for NCS
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description NCS
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of Novell Cluster Services (NCS)

Authors:
--------
    Jason Record <jrecord@suse.com>

%files NCS
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/NCS
%attr(555,%{patuser},%{patgrp}) %{patdir}/NCS/*

##################################################################
# Samba Patterns
##################################################################

%package Samba
Summary:      Supportconfig Analysis Patterns for Samba
Group:        Documentation/SuSE
Release:      1
Requires:     %{name}-base
%description Samba
Supportconfig Analysis (SCA) appliance patterns to identify known
issues relating to all versions of Samba

Authors:
--------
    Jason Record <jrecord@suse.com>

%files Samba
%defattr(-,%{patuser},%{patgrp})
%dir /var/opt/%{produser}
%dir %{patdir}
%dir %{patdir}/Samba
%attr(555,%{patuser},%{patgrp}) %{patdir}/Samba/*

##################################################################
# Final processing
##################################################################

%prep
%setup -q

%build
make build

%install
make install

%changelog
* Thu Dec 16 2013 jrecord@suse.com
- added
  tmp-7002723.py sleall
- error checking now in lastdown-3301593.py

* Wed Dec 11 2013 jrecord@suse.com
- added time consideration to lastdown-3301593.py
- added
  firefox-SUSE-SU-2013_1678-1a.pl sle11sp3
  firefox-SUSE-SU-2013_1678-1b.pl sle11sp2
  firefox-SUSE-SU-2013_1678-1c.pl sle11sp1
  firefox-SUSE-SU-2013_1678-1d.pl sle10sp4
  firefox-SUSE-SU-2013_1678-1e.pl sle10sp3
  flash-SUSE-SU-2013_1716-1a.pl sle11sp3
  flash-SUSE-SU-2013_1716-1b.pl sle11sp2
  java-SUSE-SU-2013_1677-23.pl sle10sp3
  java-SUSE-SU-2013_1677-2a.pl sle11sp3
  java-SUSE-SU-2013_1677-2b.pl sle11sp2
  java-SUSE-SU-2013_1677-2c.pl sle11sp1
  java-SUSE-SU-2013_1677-2d.pl sle10sp4
  java-SUSE-SU-2013_1677-3a.pl sle11sp3
  java-SUSE-SU-2013_1677-3b.pl sle11sp2
  javaibm-SUSE-SU-2013_1669-1a.pl sle10sp4
  javaibm-SUSE-SU-2013_1669-1b.pl sle10sp3
  javaibm-SUSE-SU-2013_1677-1.pl sle9
  kdev-7003734.py sle11all
  kernel-SUSE-SU-2013_1748-1.pl sle11sp2
  kernel-SUSE-SU-2013_1749-1.pl sle11sp3

* Tue Dec 10 2013 - jrecord@suse.com
- updated vmware-00001.pl link
- added
  afcgid-SUSE-SU-2013_1667-1a.pl
  afcgid-SUSE-SU-2013_1667-1b.pl
  guestfs-SUSE-SU-2013_1626-1.pl
  jakarta-SUSE-SU-2013_1660-1a.pl
  jakarta-SUSE-SU-2013_1660-1b.pl
  libxml-SUSE-SU-2013_1625-1.pl
  libxml-SUSE-SU-2013_1627-1.pl
  openjdk-SUSE-SU-2013_1666-1.pl
  vino-SUSE-SU-2013_1631-1.pl
  vino-SUSE-SU-2013_1631-2.pl
  xfs-7013481a.py sle11sp2
  xfs-7013481b.py sle11sp3
  xfs-7014242.py sle11all

* Wed Nov 13 2013 jrecord@suse.com
- added python library POD documentation
- added getDriverInfo to SUSE.py library
- moved scatool to its own package

* Wed Oct 30 2013 jrecord@suse.com
- fixed pattern hash plings
- update pat tool to detect invalid hash plings

* Thu Oct 17 2013 jrecord@suse.com
- fixed scatool supportconfig errors
- added SLE11SP4 to SUSE.pm
- added startup switches to scatool.py

* Mon Oct 07 2013 jrecord@suse.com
- initial

