"""
Supportconfig Analysis Library for Device Mapper Multi-path I/O (MPIO) Related Patterns

Library of python functions used when dealing with issues incident to MPIO
"""
##############################################################################
#  Copyright (C) 2015 SUSE LLC
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
#  Modified: 2015 Jun 23
#
##############################################################################

import re
import Core

def devicesManaged():
	"""
	Determines if any disks are managed with MPIO. It looks at the multipath -ll output for device lines with -+- in them.

	Args: None
	Returns: True or False
		True if devices are being managed
		False if they are not.
	
	Example:
	if( SUSE.mpioDevicesManaged() ):
		Core.updateStatus(Core.IGNORE, "MPIO Disks are being managed")
	else:
		Core.updateStatus(Core.WARNG, "No MPIO Disks are being managed")

	"""
	FILE_OPEN = "mpio.txt"
	SECTION = "multipath -ll"
	CONTENT = []
	if Core.getRegExSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if '-+-' in LINE:
				return True
	return False

def convertKeyValue(STR_TO_CONVERT):
	CONVERTED = {}
	TMP = STR_TO_CONVERT.split()
	#print "\nConverting:", TMP
	#process the single-value key/value pairs
	for ITEM in TMP:
		if "='" in ITEM and ITEM.endswith("'"):
			PART = ITEM.split("=")
			CONVERTED[PART[0]] = PART[1].strip("'")
		elif "='" in ITEM or ITEM.endswith("'"):
			#skip multi-value items
			continue
		elif not "=" in ITEM:
			#skip multi-value items
			continue
		else:
			PART = ITEM.split("=")
			CONVERTED[PART[0]] = PART[1]
	#process the multi-valued key/value pairs
	IN_VALUE = False
	MULTI_VALUE = []
	for ITEM in TMP:
		#print "Processing", ITEM
		if "='" in ITEM and ITEM.endswith("'"):
			#print " skipping quoted single value"
			continue
		elif( IN_VALUE ):
			if ITEM.endswith("'"):
				#print " end multi-value"
				IN_VALUE = False
				MULTI_VALUE.append(ITEM)
				PARTS = ' '.join(MULTI_VALUE)
				PART = PARTS.split("=")
				CONVERTED[PART[0]] = PART[1].strip("'")
				MULTI_VALUE = []
			elif "=" not in ITEM:
				#print " multi-value part"
				MULTI_VALUE.append(ITEM)
		else:
			if "='" in ITEM:
				#print " start multi-value"
				IN_VALUE = True
				MULTI_VALUE.append(ITEM)
	#print "Converted: ", CONVERTED
	return CONVERTED


def getManagedDevices():
	"""
	Normalizes the multipath -ll output into a list of dictionaries. The multipath -ll output looks similar to:
	#==[ Command ]======================================#
	# /sbin/multipath -ll
	mpathe (3600601609e003700bd875493d3ade411) dm-2 DGC,VRAID
	size=1.0T features='1 queue_if_no_path' hwhandler='1 emc' wp=rw
	|-+- policy='round-robin 0' prio=4 status=active
	| |- 2:0:1:4 sdai 66:32  active ready running
	| `- 1:0:1:4 sdo  8:224  active ready running
	`-+- policy='round-robin 0' prio=1 status=enabled
		|- 1:0:0:4 sde  8:64   active ready running
		`- 2:0:0:4 sdy  65:128 active ready running

	Args: None
	Returns: List of Dictionaries

	Example:
	Though the order of the elements will be different that shown. These are ordered to demonstrate the key value pairs. 
	getManagedDevices would return a list of dictionaries for the example above as follows:

	[	{'alias': 'mpathe', 'wwid': '3600601609e003700bd875493d3ade411', 'dmdev': 'dm-2', 'description': 'DGC,VRAID', 
		'size': '1.0T', 'features': '1 queue_if_no_path', 'hwhandler': '1 emc', 'wp': 'rw', 
		'devicepath': 
		[	{'path_group_policy': 'round-robin 0', 'path_state': 'running', 'path_group_status': 'active', 'path_devnode': 'sdai', 'path_group_prio': '4', 'dm_status': 'ready', 'path_major_minor': '66:32', 'path_scsi_addr': '2:0:1:4', 'path_status': 'active'}, 
			{'path_group_policy': 'round-robin 0', 'path_state': 'running', 'path_group_status': 'active', 'path_devnode': 'sdo', 'path_group_prio': '4', 'dm_status': 'ready', 'path_major_minor': '8:224', 'path_scsi_addr': '1:0:1:4', 'path_status': 'active'}, 
			{'path_group_policy': 'round-robin 0', 'path_state': 'running', 'path_group_status': 'enabled', 'path_devnode': 'sde', 'path_group_prio': '1', 'dm_status': 'ready', 'path_major_minor': '8:64', 'path_scsi_addr': '1:0:0:4', 'path_status': 'active'}, 
			{'path_group_policy': 'round-robin 0', 'path_state': 'running', 'path_group_status': 'enabled', 'path_devnode': 'sdy', 'path_group_prio': '1', 'dm_status': 'ready', 'path_major_minor': '65:128', 'path_scsi_addr': '2:0:0:4', 'path_status': 'active'}
		]
	}]

	"""
	FILE_OPEN = "mpio.txt"
	SECTION = "multipath -ll"
	CONTENT = []
	DEVICES = []
	IN_DEVICE = False
	MPATH = {}
	ENTRIES = []
	DeviceStart = re.compile(" dm-\d+ ")
	DeviceEntry = re.compile("\d+:\d+:\d+:\d+\s+\D+\s+\d+:\d+", re.IGNORECASE)
	if Core.getRegExSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if DeviceStart.search(LINE):
				if( len(MPATH) > 1 ):
					DEVICES.append(dict(MPATH))
				MPATH = {'devicepath': []}
				PARTS = LINE.split()
				PATH_GROUP_VALUES = {}
				if PARTS[1].startswith('('): # user alias names in use
					MPATH['alias'] = PARTS[0]
					MPATH['wwid'] = PARTS[1].strip('()')
					MPATH['dmdev'] = PARTS[2]
					del PARTS[0:3]
					MPATH['description'] = ' '.join(PARTS)
				else:
					MPATH['alias'] = ''
					MPATH['wwid'] = PARTS[0]
					MPATH['dmdev'] = PARTS[1]
					del PARTS[0:2]
					MPATH['description'] = ' '.join(PARTS)
			elif "size=" in LINE:
				KEY_VALUES = convertKeyValue(LINE)
				MPATH.update(KEY_VALUES)
			elif '-+-' in LINE:
				D = convertKeyValue(LINE)
				#print "==Insert path_group_", D
				PATH_GROUP_VALUES = {}
				# prepend "path_group_" before each PATH_GROUP_VALUES key
				for KEY in list(D.keys()):
					NEW_KEY = "path_group_" + str(KEY)
					PATH_GROUP_VALUES[NEW_KEY] = D[KEY]
					#print "KEY", KEY
					#print "NEW_KEY", NEW_KEY
					#print "RESULT:", PATH_GROUP_VALUES, "\n"
				del D
			elif DeviceEntry.search(LINE):
				TMP = LINE.split()
				ENTRIES = {}
				while TMP[0].startswith(('|','`')):
					del TMP[0]
				COUNT = len(TMP)
				if( TMP > 5 ):
					ENTRIES = {"path_scsi_addr": TMP[0], "path_devnode": TMP[1], "path_major_minor": TMP[2], "path_status": TMP[3], "dm_status": TMP[4], "path_state": TMP[5]}
				elif( TMP > 4 ):
					ENTRIES = {"path_scsi_addr": TMP[0], "path_devnode": TMP[1], "path_major_minor": TMP[2], "path_status": TMP[3], "dm_status": TMP[4]}
				elif( TMP > 3 ):
					ENTRIES = {"path_scsi_addr": TMP[0], "path_devnode": TMP[1], "path_major_minor": TMP[2], "path_status": TMP[3]}
				elif( TMP > 2 ):
					ENTRIES = {"path_scsi_addr": TMP[0], "path_devnode": TMP[1], "path_major_minor": TMP[2]}
				else:
					ENTRIES = {"path_scsi_addr": TMP[0], "path_devnode": TMP[1]}
				if( PATH_GROUP_VALUES ):
					ENTRIES.update(PATH_GROUP_VALUES)
				MPATH['devicepath'].append(ENTRIES)
		if( len(MPATH) > 1 ):
			DEVICES.append(dict(MPATH))

		#print "\n=============\n"
		#for I in range(len(DEVICES)):
			#print "\nDEVICES[" + str(I) + "] ="
			#for X in DEVICES[I]:
				#if ( "devicepath" == X ):
					#print " {0:12} = ".format(X)
					#for Y in DEVICES[I][X]:
						#print "  ", Y
				#else:
					#print " {0:12} = {1}".format(X, DEVICES[I][X])
		#print "\n"

	return DEVICES

def getDiskID(DEVICE_PATH):
	"""
	Gets the system disk (sd?) or world wide name ID for use in MPIO managed disk lookup.
	Returns and sd disk device without partition numbers or a wwid
	"""
	ID = ''
	DEV = DEVICE_PATH.split("/")[-1] + " "
	Digits = re.compile("\d+")
	#print "Evaluate", DEV
	if DEV.startswith("sd"): #check for system device name in the form sd? because they are easy to find
		ID = re.sub(Digits, "", DEV)
	else:
		CONTENT = []
		UDEV_CONTENT = []
		if Core.getRegExSection('mpio.txt', 'ls -lR.*/dev/disk/', CONTENT): #find out how the xen config device is symbolically linked
			for LINE in CONTENT:
				if DEV in LINE: #found the symlink for the xen device
					#print " ", LINE
					LINKED_DEV = LINE.split()[-1].split("/")[-1] #just get the last part of the linked path after the last /
					#print " ", LINKED_DEV
					if LINKED_DEV.startswith("sd"): #the symlink was linked to a system device
						ID = re.sub(Digits, "", LINKED_DEV)
					else:
						Core.getRegExSection('mpio.txt', '/udevadm info -e', UDEV_CONTENT)
						BlockDev = re.compile('^P:\s+/devices/virtual/block/' + str(LINKED_DEV))
						EndBlockDev = re.compile('^$')
						IN_DEV = False
						for UDEV_LINE in UDEV_CONTENT:
							if( IN_DEV ):
								if EndBlockDev.search(UDEV_LINE):
									IN_DEV = False
								elif "DM_NAME=" in UDEV_LINE:
									ID = UDEV_LINE.split("=")[-1]
									IN_DEV = False
									break
							elif BlockDev.search(UDEV_LINE):
								IN_DEV = True
	#print " ", ID, "\n"
	return ID.strip()

def partitionManagedDevice(DISK_ID, MPIO_DEVS):
	"""
	Checks if the DISK_ID is present in the MPIO_DEVS or multipath devices that do not have a no_partitions feature.
	Returns True if the DISK_ID is managed without no_partitions or False if it is not managed or if no_partitions is found on the wwid.
	"""
	#print "\nChecking '" + str(DISK_ID) + "' in:"
	for MPIO in MPIO_DEVS:
		#print MPIO['wwid'], "or", MPIO['device']
		#print MPIO['features']
		if "no_partitions" in MPIO['features']:
			#print " IGNORED: no_partitions found"
			continue
		elif( DISK_ID == MPIO['wwid'] ):
			#print " MATCH"
			return True
		else:
			for LUN_PATH in MPIO['devicepath']:
				#print "LUN_PATH[1]", "'" + str(LUN_PATH[1]) + "'"
				if( DISK_ID == LUN_PATH['path_devnode']):
					#print " MATCH"
					return True
	return False


