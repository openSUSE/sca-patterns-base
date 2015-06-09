"""
Supportconfig Analysis Library for Xen patterns

Library of python functions used when dealing with supportconfigs from Xen
vitural machines or their virtual machine servers.
"""
##############################################################################
#  Copyright (C) 2014,2015 SUSE LLC
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
#  Modified: 2015 Jun 06
#
##############################################################################

import re
import Core

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
			if re.match(r'kernel.*xen.*gz', content[line]):
				return True
	return False

def getConfigFiles():
	"""
	Stores the non-XML Xen configuration files in list of dictionaries

	Args: None
	Returns: List of Dictionaries

	Example:
	Pending
	"""
	CONFIG_FILES = []
	CONFIG_FILE_LIST = []
	SECTION_LIST = {}
	MultiLine = re.compile("=\s*\[") # A line that has an =[ k
	IN_MULTI_LINE = False
	VALUES = []
	if Core.listSections("xen.txt", SECTION_LIST):
		for LINE in SECTION_LIST:
			if SECTION_LIST[LINE].startswith("/etc/xen/vm/"):
				if '.xml' not in SECTION_LIST[LINE]:
					CONFIG_FILE_LIST.append(SECTION_LIST[LINE])
		for CONFIG in CONFIG_FILE_LIST:
			#print "----------------------\nGetting", CONFIG
			CONTENT = []
			if Core.getExactSection("xen.txt", CONFIG, CONTENT):
				CONFIG_VALUES = {}
				for LINE in CONTENT:
					LINE = LINE.strip()
					if( IN_MULTI_LINE ):
						if LINE.endswith("]"):
							VALUES.append(LINE)
							VALUE_STRING = ' '.join(VALUES)
							TMP = VALUE_STRING.split("=", 1)
							#print "TMP", TMP
							CONFIG_VALUES[TMP[0].strip()] = TMP[1].strip('"').strip()
							#print "  CONFIG_VALUES", CONFIG_VALUES
							IN_MULTI_LINE = False
							VALUES = [] #prepare for new multiline value in config file
						else:
							VALUES.append(LINE)
					elif( MultiLine.search(LINE) and not LINE.endswith("]")):
						IN_MULTI_LINE = True
						VALUES.append(LINE)
					else: #assume single line entry
						TMP = LINE.split("=", 1)
						#print "TMP", TMP, "Length", len(TMP)
						if( len(TMP) != 2 ): #Invalid entry, assume the config file is invalid and ignore it.
							#print " Invalid config file"
							CONFIG_VALUES = {}
							break
						elif( "=" in TMP[1] and "]" not in TMP[1] ):
							#print " Invalid config file"
							CONFIG_VALUES = {}
							break
						else:
							CONFIG_VALUES[TMP[0].strip()] = TMP[1].strip('"').strip()
				#print "  CONFIG_VALUES", CONFIG_VALUES
				if( CONFIG_VALUES):
					CONFIG_FILES.append(CONFIG_VALUES)

		#if( CONFIG_FILES ):
			#print "======\n"
			#for I in range(len(CONFIG_FILES)):
				#print I, "==", CONFIG_FILES[I], "\n"
		#else:
			#print "CONFIG_FILES empty"

	return CONFIG_FILES

def getDiskValueList(XEN_CONFIG_DISK_VALUE):
	#print "\n", XEN_CONFIG_DISK_VALUE, "\n"
	DISK_LIST = []
	DISK_VALUE_LIST = XEN_CONFIG_DISK_VALUE.strip("[]").split()

	for DISK in DISK_VALUE_LIST:
		DISK_KEY_VALUES = {}
		DISK_VALUE_PART = DISK.strip("',").split(",")
		if DISK_VALUE_PART[0].startswith("tap"):
			PART = DISK_VALUE_PART[0].split(':')
			DISK_KEY_VALUES['type'] = ':'.join(PART[0:2]).lower()
			DISK_KEY_VALUES['device'] = PART[2]
		else:
			PART = DISK_VALUE_PART[0].split(':',1)
			DISK_KEY_VALUES['type'] = PART[0].lower()
			DISK_KEY_VALUES['device'] = PART[1]
		DISK_KEY_VALUES['vmdevice'] = DISK_VALUE_PART[1]
		DISK_KEY_VALUES['mode'] = DISK_VALUE_PART[2]
		if( len(DISK_VALUE_PART) > 3 ):
			DISK_KEY_VALUES['domain'] = DISK_VALUE_PART[3]
		DISK_LIST.append(DISK_KEY_VALUES)

	#for I in range(len(DISK_LIST)):
		#print I, ":", DISK_LIST[I]
	#print "\n"

	return DISK_LIST


