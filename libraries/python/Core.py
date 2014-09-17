"""
Supportconfig Analysis Library for Core python patterns

Core library of functions for creating and processing python patterns
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
#    David Hamner (ke7oxh@gmail.com)
#    Jason Record (jrecord@suse.com)
#
#  Modified: 2014 Sep 17
#
##############################################################################

import sys
import re
from distutils.version import LooseVersion
path = ''

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

	Args:		CLASS = META_CLASS
				CATEGORY = META_CATEGORY
				COMPONENT = META_COMPONENT
				ID = PATTERN_ID
				LINK = PRIMARY_LINK
				OVER_ALL = OVERALL
				INFO = OVERALL_INFO
				LINKS = OTHER_LINKS
	Returns:	Updates global variables
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

	Args:		None
	Returns:	Pattern result string to stdout
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

	Args:		overAll (Integer) - Current pattern status. Acceptable values are: 
				Core.TEMP same as Core.STATUS_TEMPORARY
				Core.PART same as Core.STATUS_PARTIAL
				Core.SUCC same as Core.STATUS_SUCCESS
				Core.REC same as Core.STATUS_RECCOMENDED
				Core.WARN same as Core.STATUS_WARNING
				Core.CRIT same as Core.STATUS_CRITICAL
				Core.ERROR same as Core.STATUS_ERROR
				Core.IGNORE same as Core.STATUS_IGNORE
			overAllInfo (String) - Current pattern status message.
	Returns:	Updates global OVERALL and OVERALL_INFO as needed
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

	Args:		overAll (Integer) - Current pattern status. Acceptable values are: 
					Core.TEMP same as Core.STATUS_TEMPORARY
					Core.PART same as Core.STATUS_PARTIAL
					Core.SUCC same as Core.STATUS_SUCCESS
					Core.REC same as Core.STATUS_RECCOMENDED
					Core.WARN same as Core.STATUS_WARNING
					Core.CRIT same as Core.STATUS_CRITICAL
					Core.ERROR same as Core.STATUS_ERROR
					Core.IGNORE same as Core.STATUS_IGNORE
			overAllInfo (String) - Current pattern status message.
	Returns:	Updates global OVERALL and OVERALL_INFO as needed
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

	Args:		None
	Returns:	global path to extracted archive
	Example:	None
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


def listSections(FILE_OPEN, CONTENT):
	"""
	Extracts all section names from FILE_OPEN and adds them to CONTENT.

	Args:		FILE_OPEN (String) - The supportconfig filename to open
				CONTENT (List) - Section names in FILE_OPEN
	Returns:	True or False
					True - Sections were found in FILE_OPEN
					False - No sections found in FILE_OPEN
	Example:

	FILE_OPEN = "ha.txt"
	CONTENT = {}
	if Core.listSections(FILE_OPEN, CONTENT):
		for LINE in CONTENT:
			if "corosync.conf" in CONTENT[LINE]:
				return True
	return False
	"""
	global path
	inSection = False
	RESULT = False
	I = 0

	try:
		FILE = open(path + "/" + FILE_OPEN)
	except Exception, error:
		updateStatus(ERROR, "ERROR: Cannot open " + FILE_OPEN + ": " + str(error))

	SECTION = re.compile('^#==\[')
	for LINE in FILE:
		LINE = LINE.strip("\n")
		if inSection:
			CONTENT[I] = re.sub('^#\s+', '', LINE)
			I += 1
			RESULT = True
			inSection = False
		elif SECTION.search(LINE):
			inSection = True

	FILE.close()
	return RESULT


#get Section of supportconfig
def getSection(FILE_OPEN, SECTION, CONTENT):
	"""
	Extracts the first section of a supportconfig file matching SECTION and puts it into the CONTENT list, one line per list element.

	Args:		FILE_OPEN (String) - The supportconfig filename to open
				SECTION (String) - The section regex identifier in the file
				CONTENT (List) - Section contents line-by-line
	Returns:	True or False
					True - The specified section was found
					False - The section was not found
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
	FoundSection = False
	SectionName = ''
	i = 0
	global path
	try:
		FILE = open(path + "/" + FILE_OPEN)
	except Exception, error:
		updateStatus(ERROR, "ERROR: Cannot open " + FILE_OPEN + ": " + str(error))
	SectionTag = re.compile(SECTION)
	CommentedLine = re.compile('^#|^\s+#')
	for line in FILE:
		line = line.strip("\n")
		if line.startswith('#==['):
#			print "\nNew Section Start"
			SectionName = ''
			if FoundSection:
				break
		elif ( SectionName == '' ):
#			print " SectionName before = " + str(line)
			SectionName = re.sub('^#', '', line).strip()
#			print " SectionName after  = " + str(SectionName)
		elif SectionTag.search(SectionName):
			if( len(line) > 0 ):
				if CommentedLine.search(line):
#					print " Skipping Line: '" + str(line) + "'"
					continue
				else:
#					print " Appending Line: '" + str(line) + "'"
					CONTENT[i] = line
					i += 1
					FoundSection = True
#			else:
#				print " Skipping empty line"
	FILE.close()
	return FoundSection

def normalizeVersionString(versionString):
	"""
	Converts a version string to a list of version elements

	Args:        versionString
	Returns:     A list of version string elements
	"""
#	print "normalizeVersionString ORIGINAL       versionString = '" + versionString + "'"
	versionString = re.sub("[\.,\-,_,+]", "|", versionString)
#	print "normalizeVersionString  SEPERATORS    versionString = '" + versionString + "'"
	versionString = re.sub("([A-Z,a-z]+)", "|\\1|", versionString)
#	print "normalizeVersionString  LETTER GROUPS versionString = '" + versionString + "'"
	versionString = versionString.lstrip("0")
#	print "normalizeVersionString  LEAD ZEROS    versionString = '" + versionString + "'"
	versionString = re.sub("\|\|", "|", versionString)
#	print "normalizeVersionString  DOUBLE BARS   versionString = '" + versionString + "'"
	versionString = versionString.rstrip("|")
#	print "normalizeVersionString  TRAILING BARS versionString = '" + versionString + "'"
#	print "normalizeVersionString  ELEMENTS = " + str(versionString.split("|"))
	return versionString.split("|")

def compareLooseVersions(version1, version2):
#def compareVersions(version1, version2):
	"""
	Compares two version strings using LooseVersion

	Args:		version1 (String) - The first version string
				version2 (String) - The second version string
	Returns:	-1, 0, 1
					-1	version1 is older than version2
					 0	version1 is the same as version2
					 1	version1 is newer than version2
	Example:

	thisVersion = '1.1.0-2'
	thatVersion = '1.2'
	if( compareLooseVersions(thisVersion, thatVersion) > 0 ):
		Core.updateStatus(Core.WARN, "The version is too old, update the system")
	else:
		Core.updateStatus(Core.IGNORE, "The version is sufficient")
	"""
	if(LooseVersion(version1) > LooseVersion(version2)):
		return 1
	elif (LooseVersion(version1) < LooseVersion(version2)):
		return -1
	return 0

def compareVersions(version1, version2):
	"""
	Compares the left most significant version string elements

	Args:		version1 (String) - The first version string
				version2 (String) - The second version string
	Returns:	-1, 0, 1
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
	totalElements = 0
	if( str(version1) == str(version2) ):
		return 0
	else:
#		print "compareVersions: Compare " + str(version1) + " to " + str(version2)
		FIRST = normalizeVersionString(version1)
		SECOND = normalizeVersionString(version2)
		if( len(FIRST) <= len(SECOND) ):
			totalElements = len(FIRST)
		else:
			totalElements = len(SECOND)
#		print "compareVersions: FIRST  = " + str(FIRST[0:totalElements])
#		print "compareVersions: SECOND = " + str(SECOND[0:totalElements])
		for I in range(totalElements):
			if( FIRST[I].isdigit() and SECOND[I].isdigit() ):
				if( int(FIRST[I]) > int(SECOND[I]) ):
					return 1
				elif( int(FIRST[I]) < int(SECOND[I]) ):
					return -1
			else:
				if( str(FIRST[I]) > str(SECOND[I]) ):
					return 1
				elif( str(FIRST[I]) < str(SECOND[I]) ):
					return -1
	return 0

