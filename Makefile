OBSPACKAGE=sca-patterns
SVNDIRS=patterns
PKGSPEC=$(OBSPACKAGE).spec
PATBASE='/var/opt/sca/patterns'
VERSION=$(shell awk '/Version:/ { print $$2 }' spec/${PKGSPEC})
RELEASE=$(shell awk '/Release:/ { print $$2 }' spec/${PKGSPEC})
SRCDIR=$(OBSPACKAGE)-$(VERSION)
SRCFILE=$(SRCDIR).tar.gz
BUILDDIR=/usr/src/packages

default: rpm

build:
	@echo build: Building package files
#	gzip -9f man/*
	
install:
	@echo install: Creating directory structure
	@install -d \
		$(RPM_BUILD_ROOT)/usr/sbin \
		$(RPM_BUILD_ROOT)/$(PATBASE) \
		$(RPM_BUILD_ROOT)/$(PATBASE)/lib \
		$(RPM_BUILD_ROOT)/$(PATBASE)/lib/bash \
		$(RPM_BUILD_ROOT)/$(PATBASE)/lib/python \
		$(RPM_BUILD_ROOT)/$(PATBASE)/lib/perl/SDP \
		$(RPM_BUILD_ROOT)/$(PATBASE)/local \
		$(RPM_BUILD_ROOT)/$(PATBASE)/Basic \
		$(RPM_BUILD_ROOT)/$(PATBASE)/eDirectory \
		$(RPM_BUILD_ROOT)/$(PATBASE)/Filr \
		$(RPM_BUILD_ROOT)/$(PATBASE)/GroupWise \
		$(RPM_BUILD_ROOT)/$(PATBASE)/HAE \
		$(RPM_BUILD_ROOT)/$(PATBASE)/NCS \
		$(RPM_BUILD_ROOT)/$(PATBASE)/Samba \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle11all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle11sp0 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle11sp1 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle11sp2 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle11sp3 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle10all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle10sp0 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle10sp1 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle10sp2 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle10sp3 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle10sp4 \
		$(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle9all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/OES \
		$(RPM_BUILD_ROOT)/$(PATBASE)/OES/all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/OES/oes11all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/OES/oes1all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/OES/oes2all \
		$(RPM_BUILD_ROOT)/$(PATBASE)/OES/oes2sp3 \
	@echo install: Installing files
	@install -m 644 patterns/lib/bash/* $(RPM_BUILD_ROOT)/$(PATBASE)/lib/bash
	@install -m 644 patterns/lib/python/* $(RPM_BUILD_ROOT)/$(PATBASE)/lib/python
	@install -m 644 patterns/lib/perl/SDP/* $(RPM_BUILD_ROOT)/$(PATBASE)/lib/perl/SDP
	@install -m 555 patterns/Basic/* $(RPM_BUILD_ROOT)/$(PATBASE)/Basic
	@for i in all sle11all sle11sp0 sle11sp1 sle11sp2 sle11sp3; do install -m 555 patterns/SLE/$$i/* $(RPM_BUILD_ROOT)/$(PATBASE)/SLE/$$i  ; done
	@for i in all sle10all sle10sp0 sle10sp1 sle10sp2 sle10sp3 sle10sp4; do install -m 555 patterns/SLE/$$i/* $(RPM_BUILD_ROOT)/$(PATBASE)/SLE/$$i  ; done
	@install -m 555 patterns/SLE/sle9all/* $(RPM_BUILD_ROOT)/$(PATBASE)/SLE/sle9all
	@for i in all oes11all oes1all oes2all oes2sp3; do install -m 555 patterns/OES/$$i/* $(RPM_BUILD_ROOT)/$(PATBASE)/OES/$$i  ; done
	@for i in eDirectory Filr GroupWise HAE NCS Samba; do install -m 555 patterns/$$i/* $(RPM_BUILD_ROOT)/$(PATBASE)/$$i  ; done

uninstall:
	@echo uninstall: Uninstalling from build directory
	@rm -rf $(RPM_BUILD_ROOT)
	@rm -rf $(BUILDDIR)/SOURCES/$(SRCFILE).gz
	@rm -rf $(BUILDDIR)/SPECS/$(PKGSPEC)
	@rm -rf $(BUILDDIR)/BUILD/$(SRCDIR)
	@rm -f $(BUILDDIR)/SRPMS/$(OBSPACKAGE)*.src.rpm
	@rm -f $(BUILDDIR)/RPMS/noarch/$(OBSPACKAGE)*.rpm

dist:
	@echo dist: Creating distribution source tarball
	@mkdir -p $(SRCDIR)
	@for i in $(SVNDIRS); do cp -a $$i $(SRCDIR); done
	@cp COPYING.GPLv2 $(SRCDIR)
	@cp Makefile $(SRCDIR)
	@find $(SRCDIR) -maxdepth 2 -type d  | grep '\.svn$$' | xargs rm -rf
	@tar zcf $(SRCFILE) $(SRCDIR)/*
	@rm -rf $(SRCDIR)
	@mv -f $(SRCFILE) src

clean: uninstall
	@echo clean: Cleaning up make files
	@rm -rf $(OBSPACKAGE)*
	@for i in $(SVNDIRS); do rm -f $$i/*~; done
	@rm -f src/$(OBSPACKAGE)-*gz
	@rm -f *~

prep: dist
	@echo prep: Copying source files for build
	@cp src/$(SRCFILE) $(BUILDDIR)/SOURCES
	@cp spec/$(PKGSPEC) $(BUILDDIR)/SPECS

rpm: clean prep
	@echo rpm: Building RPM packages
	@rpmbuild -ba $(BUILDDIR)/SPECS/$(PKGSPEC)
	mv $(BUILDDIR)/SRPMS/$(OBSPACKAGE)-* .
	mv $(BUILDDIR)/RPMS/noarch/$(OBSPACKAGE)-* .
	@rm -rf $(BUILDDIR)/BUILD/$(SRCDIR)
	@rm -f $(BUILDDIR)/SOURCES/$(SRCFILE)
	@rm -f $(BUILDDIR)/SPECS/$(PKGSPEC)
	@ls -ls $$LS_OPTIONS

commit:
	@echo commit: Committing changes to SVN
	@svn up
	@svn ci -m "Committing Source: $(OBSPACKAGE)-$(VERSION)-$(RELEASE)"
	@echo

help:
	@clear
	@make -v
	@echo
	@echo Make options for package: $(OBSPACKAGE)
	@echo make {build, install, uninstall, dist, clean, prep, rpm[default]}
	@echo
