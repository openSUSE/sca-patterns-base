"""
Supportconfig Analysis Library for HAE python patterns

Library of functions for creating python patterns specific to 
High Availability Extension (HAE)
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
#    Jason Record (jrecord@suse.com)
#
#  Modified: 2014 Jun 10
#
##############################################################################

import sys
import re
import Core
import string

def getSBDInfo():
	"""
	Gets split brain detection partition information. SBD partitions with invalid sbd dump output are ignored.

	Args:		None
	Returns:	List of SBD Dictionaries with keys
		SBD_DEVICE (String) - 
		SBD_OPTS (String) - 
		Version (Int) - 
		Slots (Int) - 
		Sector_Size (Int) - 
		Watchdog (Int) - 
		Allocate (Int) - 
		Loop (Int) - 
		MsgWait (Int) - 
	Example:

	"""
	SBD_LIST = []
	SBD_DICTIONARY = { 
		'Device': '',
		'SBD_DEVICE': '',
		'SBD_OPTS': '',
		'Version': '',
		'Slots': -1,
		'Sector_Size': -1,
		'Watchdog': -1,
		'Allocate': -1,
		'Loop': -1,
		'MsgWait': -1,
	}
	FILE_OPEN = "ha.txt"
	CONTENT = {}
	IDX_PATH = 3
	IDX_KEY = 0
	IDX_VALUE = 1
	SYSCONFIG_FOUND = False
	DUMP_FOUND = False

	try:
		FILE = open(Core.path + "/" + FILE_OPEN)
	except Exception, error:
#		print "Error opening file: %s" % error
		Core.updateStatus(Core.ERROR, "ERROR: Cannot open " + FILE_OPEN)

	SBD_PATH = ''
	SBD_DEVICE = ''
	SBD_OPTS = ''
	DUMPCMD = re.compile("/usr/sbin/sbd -d .* dump")
	SYSCONFIG = re.compile("^# /etc/sysconfig/sbd")
	INVALID = re.compile("Syntax", re.IGNORECASE)
	for LINE in FILE:
		if DUMP_FOUND:
#			print "Dump: " + str(LINE)
			if "#==[" in LINE:
				DUMP_FOUND = False
				#append SBD_DICTIONARY to SBD_LIST
				SBD_DICTIONARY['Device'] = SBD_PATH
				SBD_DICTIONARY['SBD_DEVICE'] = SBD_DEVICE
				SBD_DICTIONARY['SBD_OPTS'] = SBD_OPTS
				SBD_LIST.append(dict(SBD_DICTIONARY))
#				print "SBD_DICTIONARY = " + str(SBD_DICTIONARY)
				SBD_PATH = ''
				SBD_DICTIONARY = { 
					'Device': '',
					'SBD_DEVICE': '',
					'SBD_OPTS': '',
					'Version': '',
					'Slots': -1,
					'Sector_Size': -1,
					'Watchdog': -1,
					'Allocate': -1,
					'Loop': -1,
					'MsgWait': -1,
				}
			elif INVALID.search(LINE):
				DUMP_FOUND = False
				SBD_PATH = ''
				SBD_DICTIONARY = { 
					'Device': '',
					'SBD_DEVICE': '',
					'SBD_OPTS': '',
					'Version': '',
					'Slots': -1,
					'Sector_Size': -1,
					'Watchdog': -1,
					'Allocate': -1,
					'Loop': -1,
					'MsgWait': -1,
				}
			elif LINE.startswith('Header'):
				SBD_DICTIONARY['Version'] = LINE.split(':')[IDX_VALUE].strip()
			elif LINE.startswith('Number'):
				SBD_DICTIONARY['Slots'] = int(LINE.split(':')[IDX_VALUE].strip())
			elif LINE.startswith('Sector'):
				SBD_DICTIONARY['Sector_Size'] = int(LINE.split(':')[IDX_VALUE].strip())
			elif "watchdog" in LINE:
				SBD_DICTIONARY['Watchdog'] = int(LINE.split(':')[IDX_VALUE].strip())
			elif "allocate" in LINE:
				SBD_DICTIONARY['Allocate'] = int(LINE.split(':')[IDX_VALUE].strip())
			elif "loop" in LINE:
				SBD_DICTIONARY['Loop'] = int(LINE.split(':')[IDX_VALUE].strip())
			elif "msgwait" in LINE:
				SBD_DICTIONARY['MsgWait'] = int(LINE.split(':')[IDX_VALUE].strip())				
		elif SYSCONFIG_FOUND:
			if "#==[" in LINE:
				SYSCONFIG_FOUND = False
			elif LINE.startswith('SBD_DEVICE'):
				SBD_DEVICE = re.sub("\n|\"|\'", '', LINE.split('=')[IDX_VALUE])
			elif LINE.startswith('SBD_OPTS'):
				SBD_OPTS = re.sub("\n|\"|\'", '', LINE.split('=')[IDX_VALUE])
		elif SYSCONFIG.search(LINE):
			SYSCONFIG_FOUND = True
		elif DUMPCMD.search(LINE):
			SBD_PATH = LINE.split()[IDX_PATH].strip()
			DUMP_FOUND = True

#	print "SBD_LIST Size = " + str(len(SBD_LIST))
#	print "SBD_LIST = " + str(SBD_LIST) + "\n"
	return SBD_LIST


