"""
Supportconfig Analysis Library for SUSE Manager patterns

Library of python functions used when dealing with supportconfigs from SUSE
Manager server or proxy.
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
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
#  Authors/Contributors:
#     Jason Record (jrecord@suse.com)
#
#  Modified: 2014 Dec 02
#
##############################################################################

import Core

def getSumaInfo():
	"""
	Gets basic information about SUMA from the supportconfig files.

	Args:		None
	Returns:	Dictionary with keys
		Installed (Boolean) - True if SUSE Mangaer is installed as a base product
		Known (Boolean) - True if the product information contained the correct number of fields
		Name (String) - The name of the SUSE Manager product
		Version (String) - The version string
		Release (String) - The release string
		Type (String) - server, proxy or unknown

	Example:

	SUMA = suma.getSumaInfo()
	if( SUMA['Installed'] ):
		if( Core.compareVersions(SUMA['Version'], '2.1') == 0 ):
			Core.updateStatus(Core.REC, "SUSE Manager 2.1 is installed")
		else:
			Core.updateStatus(Core.ERROR, "ERROR: SUSE Manager 2.1 required")
	else:
		Core.updateStatus(Core.ERROR, "ERROR: SUSE Manager not installed")

	"""
	INFO = {'Installed': False, 'Known': False}
	CONTENT = {}
	FOUND = False
	IDX_NAME = 3
	IDX_BASE = -1
	IDX_VERSION = 4
	if Core.getSection('updates.txt', '/zypper.*products', CONTENT):
		for LINE in CONTENT:
			if( FOUND ):
				LIST = CONTENT[LINE].split("|")
				if( len(LIST) >= 7 ):
					INFO['Known'] = True
					if "yes" in LIST[IDX_BASE].lower():
						if "suse manager" in LIST[IDX_NAME].lower():
							INFO['Installed'] = True
							INFO['Name'] = LIST[IDX_NAME].strip()
							(INFO['Version'], INFO['Release']) = LIST[IDX_VERSION].strip().split("-")
							if "server" in INFO['Name'].lower():
								INFO['Type'] = 'server'
							elif "proxy" in INFO['Name'].lower():
								INFO['Type'] = 'proxy'
							else:
								INFO['Type'] = 'unknown'
							FOUND = False
			elif CONTENT[LINE].startswith("--+"):
				FOUND = True
#	print INFO
	return INFO

def jabberdRunning():
	"""
	Confirms if all the processes required for jabberd are running.

	Args: None
	Returns: True or False
		True - The jabberd processes are running
		False - One or more jabberd processes are NOT running

	Example:

	if ( suma.jabberdRunning() ):
		Core.updateStatus(Core.IGNORE, "The jabberd process(es) are running")
	else:
		Core.updateStatus(Core.WARN, "ERROR: The jabberd process(es) are not running")
	"""
	CONTENT = {}
	COUNT = {}
	if Core.getSection('basic-health-check.txt', '/ps a', CONTENT):
		for line in CONTENT:
			STR = CONTENT[line].lower()
			if "/usr/bin/router " in STR:
				COUNT['router'] = True
			elif "/usr/bin/sm " in STR:
				COUNT['sm'] = True
			elif "/usr/bin/c2s " in STR:
				COUNT['c2s'] = True
			elif "/usr/bin/s2s " in STR:
				COUNT['s2s'] = True
#	print COUNT
	if( len(COUNT) == 4 ):
		return True
	else:
		return False


