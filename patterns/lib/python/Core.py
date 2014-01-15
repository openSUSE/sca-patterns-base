"""
Supportconfig Analysis Library for Core python patterns

Core library of functions for creating and processing python patterns
"""
##############################################################################
#  Copyright (C) 2013-2014 SUSE LLC
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
#    David Hamner (dhamner@novell.com)
#    Jason Record (jrecord@suse.com)
#
#  Modified: 2014 Jan 14
#
##############################################################################

import sys, re, distutils.version
from distutils.version import LooseVersion
global path

STATUS_TEMPORARY = -2
STATUS_PARTIAL = -1
STATUS_SUCCESS = 0
STATUS_RECOMMEND = 1
STATUS_PROMOTION = 2
STATUS_WARNING = 3
STATUS_CRITICAL = 4
STATUS_ERROR = 5
STATUS_IGNORE = 6

TEMP = STATUS_TEMPORARY
PART = STATUS_PARTIAL
SUCC = STATUS_SUCCESS
REC = STATUS_RECOMMEND
WARN = STATUS_WARNING
CRIT = STATUS_CRITICAL
ERROR = STATUS_ERROR
IGNORE = STATUS_IGNORE

PASS = 0
EXIT = 5

META_CLASS = ""
META_CATEGORY = ""
META_COMPONENT = ""
PATTERN_ID = ""
PRIMARY_LINK = ""
OVERALL = STATUS_TEMPORARY
TMP = OVERALL
OVERALL_INFO = ""
OTHER_LINKS = ""
#META_LINK_<TAG>=
#META_LINK_<TAG>=

def init(CLASS, CATEGORY, COMPONENT, ID, LINK, OVER_ALL, INFO, LINKS):
	"""
	Initialize the pattern metadata variables and process the startup options.
	A python pattern should initialize the metadata variables and then call
	this function. Required at the beginning of the pattern.

	Args:
		CLASS = META_CLASS
		CATEGORY = META_CATEGORY
		COMPONENT = META_COMPONENT
		ID = PATTERN_ID
		LINK = PRIMARY_LINK
		OVER_ALL = OVERALL
		INFO = OVERALL_INFO
		LINKS = OTHER_LINKS
		
	Returns: Updates global variables
	"""
	global META_CLASS
	global META_CATEGORY
	global META_COMPONENT
	global PATTERN_ID
	global PRIMARY_LINK
	global OVERALL
	global OVERALL_INFO
	global OTHER_LINKS

	META_CLASS = CLASS
	META_CATEGORY = CATEGORY
	META_COMPONENT = COMPONENT
	PATTERN_ID = ID
	PRIMARY_LINK = LINK
	OVERALL = OVER_ALL
	OVERALL_INFO = INFO
	OTHER_LINKS = LINKS
	processOptions()


def printPatternResults():
	"""
	Prints to stdout the pattern result string. The pattern result string is case
	sensitive and order dependent. This function ensures the strings is printed 
	correctly. Call this function when the pattern had completed its processing.
	Required at the end of the pattern.

	Args: None
	Returns: Pattern result string to stdout
	"""
	global META_CLASS
	global META_CATEGORY
	global META_COMPONENT
	global PATTERN_ID
	global PRIMARY_LINK
	global OVERALL
	global OVERALL_INFO
	global OTHER_LINKS
	print "META_CLASS" + "=" + META_CLASS + "|" + "META_CATEGORY" + "=" + META_CATEGORY + "|" + "META_COMPONENT" + "=" + META_COMPONENT + "|" + "PATTERN_ID" + "=" + PATTERN_ID + "|"  + "PRIMARY_LINK" + "=" + PRIMARY_LINK + "|" + "OVERALL" + "=" + str(OVERALL) + "|"  + "OVERALL_INFO" + "=" + OVERALL_INFO + "|" + OTHER_LINKS

def updateStatus(overAll, overAllInfo):
	"""
	Update the global pattern result string with the current pattern state. The
	pattern result string is only updated if overAll is greater than its previous
	value. overAll is used to update the global OVERALL status value, and 
	overAllInfo is used to update the global OVERALL_INFO status message. The 
	OVERALL_INFO string is displayed on the SCA Report.

	Args:
		overAll (Integer) - Current pattern status. Acceptable values are: 
			Core.TEMP same as Core.STATUS_TEMPORARY
			Core.PART same as Core.STATUS_PARTIAL
			Core.SUCC same as Core.STATUS_SUCCESS
			Core.REC same as Core.STATUS_RECCOMENDED
			Core.WARN same as Core.STATUS_WARNING
			Core.CRIT same as Core.STATUS_CRITICAL
			Core.ERROR same as Core.STATUS_ERROR
			Core.IGNORE same as Core.STATUS_IGNORE
		overAllInfo (String) - Current pattern status message.
	Returns: Updates global OVERALL and OVERALL_INFO as needed
	Example:

	Core.updateStatus(Core.WARN, "Found a condition suitable for a warning")
	Core.updateStatus(Core.STATUS_CRITICAL, "Found a more severe condition, the warning is overwritten")
	Core.updateStatus(Core.CRIT, "Another critical condition found, but ignored because critical is already set")
	Core.updateStatus(Core.SUCC, "A successful condition found, but ignored because the severity is already at critical")
	"""
	global OVERALL_INFO
	global OVERALL
	global EXIT
	if(OVERALL < overAll):
		OVERALL = overAll
		OVERALL_INFO = overAllInfo
	if(OVERALL >= EXIT):
		printPatternResults()
		sys.exit()


def setStatus(overAll, overAllInfo):
	"""
	Manually overrides the OVERALL status and the OVERALL_INFO message string.
	Regardless of the current status, this function overrides it.

	Args:
		overAll (Integer) - Current pattern status. Acceptable values are: 
			Core.TEMP same as Core.STATUS_TEMPORARY
			Core.PART same as Core.STATUS_PARTIAL
			Core.SUCC same as Core.STATUS_SUCCESS
			Core.REC same as Core.STATUS_RECCOMENDED
			Core.WARN same as Core.STATUS_WARNING
			Core.CRIT same as Core.STATUS_CRITICAL
			Core.ERROR same as Core.STATUS_ERROR
			Core.IGNORE same as Core.STATUS_IGNORE
		overAllInfo (String) - Current pattern status message.
	Returns: Updates global OVERALL and OVERALL_INFO as needed
	Example:

	Core.updateStatus(Core.WARN, "Found a condition suitable for a warning")
	Core.updateStatus(Core.STATUS_CRITICAL, "Found a more severe condition, the warning is overwritten")
	Core.updateStatus(Core.CRIT, "Another critical condition found, but ignored because critical is already set")
	Core.setStatus(Core.SUCC, "A successful condition found, and manually set to override the previous critical condition")
	"""
	global OVERALL_INFO
	global OVERALL
	OVERALL = overAll
	OVERALL_INFO = overAllInfo


def processOptions():
	"""
	A function to handle the pattern's startup options. Currently only
	-p /path/to/extracted/archive is supported. It is the only required 
	startup option. Required at the beginning of a pattern.

	Args: None
	Returns: global path to extracted archive
	Example: None
	"""
	#find path
	global path
	foundPath = False
	path = "error: no path"
	for i in sys.argv:
		if foundPath == True:
			path = i
			break
		if i == "-p":
			foundPath = True
	return path


#get Section of supportconfig
def getSection(FILE_OPEN, SECTION, CONTENT):
	"""
	Extracts a section of a supportconfig file and puts it into the CONTENT
	list, one line per list element.

	Args:
		FILE_OPEN (String) - The supportconfig filename to open
		SECTION (String) - The section identifier in the file
		CONTENT (List) - Section contents line-by-line
	Returns: True or False
		True - The specified section was found
		False - the section was not found
	Example:

	fileOpen = "boot.txt"
	section = "menu.lst"
	content = {}
	if Core.getSection(fileOpen, section, content):
		for line in content:
			if "xen.gz" in content[line]:
				Core.updateStatus(Core.IGNORE, "Found Xen kernel boot option"
	Core.updateStatus(Core.WARN, "Missing Xen kernel boot option")
	"""
	FoundSectionTag = False
	FoundSection = False
	i = 0
	global path
	try:
		FILE = open(path + "/" + FILE_OPEN)
	except Exception:
		updateStatus(ERROR, "ERROR: Cannot open " + FILE_OPEN)
	for line in FILE:
		if FoundSection and not (line.startswith( '#==[' )) and not FoundSectionTag:
			line = line.strip();
			if not (line == ""):
				CONTENT[i] = line
				i = i + 1
		if FoundSectionTag:
			if SECTION in line:
				FoundSection = True
				FoundSectionTag = False
		if line.startswith( '#==[' ):
			FoundSectionTag = True
	FILE.close()
	return FoundSection


def compareVersions(version1, version2):
	"""
	Compares two version strings

	Args:
		version1 (String) - The first version string
		version2 (String) - The second version string
	Returns: -1, 0, 1
		-1	version1 is older than version2
		0	version1 is the same as version2
		1	version1 is newer than version2
	Example:

	thisVersion = '1.1.0-2'
	thatVersion = '1.2'
	if( compareVersions(thisVersion, thatVersion) > 0 ):
		Core.updateStatus(Core.WARN, "The version is too old, update the system")
	else:
		Core.updateStatus(Core.IGNORE, "The version is sufficient")
	"""
	if(LooseVersion(version1) > LooseVersion(version2)):
		return 1
	elif (LooseVersion(version1) < LooseVersion(version2)):
		return -1
	return 0



