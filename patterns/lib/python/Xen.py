"""
Supportconfig Analysis Library for Xen patterns

Library of python functions used when dealing with supportconfigs from Xen
vitural machines or their virtual machine servers.
"""
##############################################################################
#  Copyright (C) 2014 SUSE LLC
##############################################################################
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Authors/Contributors:
#     Jason Record (jrecord@suse.com)
#
#  Modified: 2014 Jan 13
#
##############################################################################

import sys, re, Core, string

def isDom0():
	"""
	Confirms if the supportconfig is from a Xen Dom0 virtual machine server

	Args: None
	Returns: True or False
		True - The server is a virtual machine server
		False - The server is NOT a virutal machine server

	Example:

	if ( Xen.isDom0() ):
		Core.updateStatus(Core.WARN, "The server is a Xen Dom0 virtual machine server")
	else:
		Core.updateStatus(Core.ERROR, "ERROR: Not a Xen Dom0")
	"""
	content = {}
	if Core.getSection('basic-environment.txt', 'Virtualization', content):
		for line in content:
			if "Identity:" in content[line]:
				if "Dom0" in content[line]:
					return True
	return False


def isDomU():
	"""
	Confirms if the supportconfig is from a Xen DomU virtual machine

	Args: None
	Returns: True or False
		True - The server is a virtual machine
		False - The server is NOT a virutal machine

	Example:
		
	if ( Xen.isDomU() ):
		Core.updateStatus(Core.WARN, "The server is a Xen DomU virtual machine")
	else:
		Core.updateStatus(Core.ERROR, "ERROR: Not a Xen DomU")
	"""
	content = {}
	if Core.getSection('basic-environment.txt', 'Virtualization', content):
		for line in content:
			if "Identity:" in content[line]:
				if "DomU" in content[line]:
					return True
	return False


def isDom0Installed():
	"""
	Determines if the Xen Dom0 kernel is installed in the menu.lst available for booting

	Args: None
	Returns: True or False
		True - Xen virtualization is installed
		False - Xen virtualization is NOT installed

	Example:

	if ( Xen.isDom0Installed() ):
		Core.updateStatus(Core.WARN, "The server has Xen Dom0 installed, buy may or may not be running")
	else:
		Core.updateStatus(Core.ERROR, "ABORT: The server does not have Xen Dom0 installed")
	"""
	content = {}
	if Core.getSection('boot.txt', 'menu.lst', content):
		for line in content:
			if "kernel" in content[line]:
				if 'xen.gz' in content[line]:
					return True
	return False


