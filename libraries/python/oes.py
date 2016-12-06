"""
Supportconfig Analysis Library for Open Enterprise Server for Linux

Library of python functions used when dealing with supportconfigs from OES for 
Linux servers.
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
#  Modified: 2015 Aug 26
#
##############################################################################

import re
import Core

def dsfwCapable():
	"""
	Checks for DSfW capabilities from the LDAP root DSE server in novell-lum.txt file.

	Args:		None
	Returns:	Boolean
		True = Server is DSfW capable
		False = Server is NOT DSfW capable or novell-lum.txt cannot be found

	Example:

	if( oes.dsfwCapable() ):
		Core.updateStatus(Core.IGNORE, "Server is DSfW Capable")
	else:
		Core.updateStatus(Core.WARN, "Server is not DSfW Capable")

	"""
	FILE_OPEN = "novell-lum.txt"
	SECTION = "ldapsearch -x"
	CONTENT = {}
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if "2.16.840.1.113719.1.513.7.1" in CONTENT[LINE]:
				return True
	return False

def ncsActive():
	"""
	Returns true is Novell Cluster Services is active on the server, otherwise it returns false.

	Args:		None
	Returns:	Boolean
		True = NCS is active
		False = NCS is not active

	Example:

	if( oes.ncsActive() ):
		Core.updateStatus(Core.IGNORE, "NCS is Active on the Server")
	else:
		Core.updateStatus(Core.WARN, "NCS is NOT active on the Server")

	"""
	FILE_OPEN = "novell-ncs.txt"
	SECTION = "cluster stats display"
	CONTENT = {}
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if CONTENT[LINE].startswith("node"):
				return True
	return False

def shadowVolumesFound():
	"""
	Checks if Dynamic Storage Technology (DST) shadow volumes are present.

	Args:		None
	Returns:	Boolean
		True = DST Shadow Volumes in use
		False = No DST Shadow Volumes in use

	Example:

	if( oes.shadowVolumesFound() ):
		Core.updateStatus(Core.IGNORE, "DST Shadow Volumes in Use")
	else:
		Core.updateStatus(Core.WARN, "No DST Shadow Volumes in Use")

	"""
	FILE_OPEN = "novell-ncp.txt"
	SECTION = "/etc/opt/novell/ncpserv.conf"
	CONTENT = {}
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if "SHADOW_VOLUME" in CONTENT[LINE]:
				return True
	return False

def getNSSVolumes():
	"""
	Gets all NSS Volumes in a list of dictionaries

	Args:		None
	Returns:	List of Dictionaries
		Each list entry is an NSS Volume dictionary with the following keys
		baseName (string) = The volume name from /dev/nsscmd, volumeName will be assigned
			from VolumeInfo.xml.
		basePool (string) = The pool name associated with the volume from nss /pool, poolName
			will be assgined from VolumeInfo.xml
		baseState (string) = The volume state from /dev/nsscmd, volumeState will be assigned
			from VolumeInfo.xml.
		mounted (boolean) = True if the volume is mounted, otherwise false
		shared (boolean) = True if the volume is shared for clustering, otherwise false
		duplicateKeys (list) = List of duplicate keys found in VolumeInfo.xml

		All additional attributes are taken from the key/value pairs in the volume's 
		Manage_NSS/Volume/<volumeName>/VolumeInfo.xml section of the novell-nss.txt file. 
		The xml file is flattened with no regard to sub sections as the keys currently 
		are unique, regardless of section. When a duplicate key shows up, they are stored
		in duplicateKeys and the key is deleted from the dictionary. Report a bug if a 
		duplicate key is found.

		<salvage>
		<highWaterMark>20</highWaterMark>
		<lowWaterMark>10</lowWaterMark>
		<maxKeepTime>0</maxKeepTime>
		<minKeepTime>0</minKeepTime>
		<freeableSize>0 (0.00  B)</freeableSize>
		<nonFreeableSize>0 (0.00  B)</nonFreeableSize>
		<deletedFiles>0</deletedFiles>
		</salvage>

		would be flattened to:

		highWaterMark=20
		lowWaterMark=10
		maxKeepTime=0
		minKeepTime=0
		freeableSize=0
		nonFreeableSize=0
		deletedFiles=0
		

	Example:

	NSS_VOLUMES = oes.getNSSVolumes()
	if( len(NSS_VOLUMES) > 0 ):
		for VOLUME in NSS_VOLUMES:
			if( VOLUME['Shared'] ):
				Core.updateStatus(Core.IGNORE, "Volume " + str(VOLUME['Name']) + " is a shared volume")
			else:
				Core.updateStatus(Core.WARN, "Volume " + str(VOLUME['Name']) + " is not shared")
	else:
		Core.updateStatus(Core.ERROR, "No NSS Volumes found")

	"""
	# start by getting the volume name and state from the echo volumes command
	FILE_OPEN = "novell-nss.txt"
	SECTION = "echo volumes"
	CONTENT = {}
	DATA_DICT = {}
	VOLUMES = []
	DUP_KEYS = []
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		SKIP = 2
		SKIPPED = 0
		VOL = re.compile('^\S')
		for LINE in CONTENT:
			if( SKIPPED < SKIP ): # skip header lines
				SKIPPED += 1
				continue
			elif CONTENT[LINE].startswith('_ADMIN'): # ignore the _ADMIN volume
				continue
			else: # look for other volumes
				if VOL.search(CONTENT[LINE]):
					DATA = CONTENT[LINE].split()
					VOLUMES.append({'baseName': DATA[0], 'basePool': '', 'baseState': DATA[1], 'mounted': False, 'shared': False, 'duplicateKeys': DUP_KEYS})

		# now get the pool associated with the volume and the shared status
		FILE_OPEN = "novell-nss.txt"
		SECTION = "/nss /pools"
		CONTENT = {}
		if Core.getSection(FILE_OPEN, SECTION, CONTENT):
			SKIP = 2
			SKIPPED = 0
			POOL = re.compile('^\S')
			POOL_NAME = ''
			SHARED = False
			for LINE in CONTENT:
				if( SKIPPED < SKIP ): # skip header lines
					SKIPPED += 1
					continue
				elif " on " in CONTENT[LINE]:
					continue
				else: # look for other volumes
					if POOL.search(CONTENT[LINE]):
						POOL_NAME = CONTENT[LINE].split()[0]
						if "shared (clustered" in CONTENT[LINE].lower():
							SHARED = True
						else:
							SHARED = False
					for IDX, VAL in enumerate(VOLUMES):
						if VAL['baseName'] in CONTENT[LINE]:
							VOLUMES[IDX]['basePool'] = POOL_NAME
							VOLUMES[IDX]['shared'] = SHARED

		# check to see if the volume is mounted
		FILE_OPEN = "fs-diskio.txt"
		SECTION = "/mount"
		CONTENT = {}
		if Core.getSection(FILE_OPEN, SECTION, CONTENT):
			for LINE in CONTENT: # look at each line from mount
				for IDX, VAL in enumerate(VOLUMES): # check each known volume against each mount line
					if CONTENT[LINE].startswith(VAL['baseName']):
						VOLUMES[IDX]['mounted'] = True

		# get volume attributes if present
		FILE_OPEN = "novell-nss.txt"
		for IDX, VAL in enumerate(VOLUMES):
			CONTENT = {}
			if Core.getSection(FILE_OPEN, "Manage_NSS/Volume/" + str(VAL['baseName']) + "/VolumeInfo.xml", CONTENT):
				for LINE in CONTENT:
					MATCH = re.match(r'<(.+?)>(.+?)</.*>', CONTENT[LINE])
					if MATCH:
						if CONTENT[LINE].startswith("<result "):
							continue
						else:
							THIS_KEY = MATCH.group(1)
							if( THIS_KEY in VOLUMES[IDX] ):
								DUP_KEYS.append(THIS_KEY)
							else:
								VOLUMES[IDX][THIS_KEY] = MATCH.group(2).split()[0].strip()
						if CONTENT[LINE].startswith("<enabledAttributes>"):
							VOLUMES[IDX]['enabledAttributes'] = MATCH.group(2).strip()
						elif CONTENT[LINE].startswith("<supportedAttributes>"):
							VOLUMES[IDX]['supportedAttributes'] = MATCH.group(2).strip()
						elif CONTENT[LINE].startswith("<nameSpaces>"):
							VOLUMES[IDX]['nameSpaces'] = MATCH.group(2).strip()

			# remove duplicate keys
			for DUPLICATE_KEY in DUP_KEYS:
				del VOLUMES[IDX][DUPLICATE_KEY]

	return VOLUMES

def getNSSPools():
	"""
	Gets all NSS Pools in a list of dictionaries

	Args:		None
	Returns:	List of Dictionaries
		Each list entry is an NSS Pool dictionary with the following keys
		poolName (string) = The pool name
		poolState (string) = The pool state
		mounted (boolean) = True if the pool device is mounted, otherwise false
		shared (boolean) = True if the pool is shared for clustering, otherwise false
		poolVolumes (list) = List of volumes the pool owns

		All additional attributes are taken from the key/value pairs in the pool's 
		Manage_NSS/Pool/<poolName>/PoolInfo.xml section of the novell-nss.txt file. 
		The xml file is flattened with no regard to sub sections as the keys currently 
		are unique, regardless of section. When a duplicate key shows up, they are stored
		in duplicateKeys and the key is deleted from the dictionary. Report a bug if a 
		duplicate key is found.

		<salvage>
		<highWaterMark>20</highWaterMark>
		<lowWaterMark>10</lowWaterMark>
		<maxKeepTime>0</maxKeepTime>
		<minKeepTime>0</minKeepTime>
		<freeableSize>0 (0.00  B)</freeableSize>
		<nonFreeableSize>0 (0.00  B)</nonFreeableSize>
		<deletedFiles>0</deletedFiles>
		</salvage>

		would be flattened to:

		highWaterMark=20
		lowWaterMark=10
		maxKeepTime=0
		minKeepTime=0
		freeableSize=0
		nonFreeableSize=0
		deletedFiles=0

	Example:

	NSS_POOLS = oes.getNSSPools()
	POOL_WARNINGS = []
	MIN_AVAILABLE = 10
	ATTRIBUTE_ERROR = False
	if( len(NSS_POOLS) > 0 ):
		for POOL in NSS_POOLS:
			if( "percentAvailableSpace" in POOL ):
				if( int(POOL['percentAvailableSpace']) < MIN_AVAILABLE ):
					POOL_WARNINGS.append(POOL['Name'])
				else:
					ATTRIBUTE_ERROR = True
	else:
		Core.updateStatus(Core.ERROR, "No NSS Pools found")

	if( len(POOL_WARNINGS) > 0 ):
		Core.updateStatus(Core.WARN, "Pools with limited available space: " + str(POOL_WARNINGS))
	elif( ATTRIBUTE_ERROR ):
		Core.updateStatus(Core.ERROR, "Some pools missing percentAvailableSpace attribute")
	else:
		Core.updateStatus(Core.IGNORE, "All pools have acceptable available space")


	"""
	FILE_OPEN = "novell-nss.txt"
	SECTION = "/nss /pools"
	CONTENT = {}
	POOLS = []
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		SKIP = 2
		SKIPPED = 0
		POOL = re.compile('^\S')
		for LINE in CONTENT:
			if( SKIPPED < SKIP ): # skip header lines
				SKIPPED += 1
				continue
			elif " on " in CONTENT[LINE]:
				continue
			else: # look for other volumes
				if POOL.search(CONTENT[LINE]):
					DATA = CONTENT[LINE].split()
					if "shared (clustered" in CONTENT[LINE].lower():
						SHARED = True
					else:
						SHARED = False
					POOLS.append({'poolName': DATA[0], 'poolStatus': DATA[1], 'shared': SHARED, 'mounted': False, 'poolVolumes': [], 'duplicateKeys': []})

		# is the pool device is mounted
		FILE_OPEN = "fs-diskio.txt"
		SECTION = "/mount"
		CONTENT = {}
		if Core.getSection(FILE_OPEN, SECTION, CONTENT):
			for LINE in CONTENT: # look at each line from mount
				for IDX, VAL in enumerate(POOLS): # check each known volume against each mount line
					if "/" + str(VAL['poolName']) + " on" in CONTENT[LINE]:
						POOLS[IDX]['mounted'] = True


		# get the volumes the pool owns
		FILE_OPEN = "novell-nss.txt"
		for IDX, VAL in enumerate(POOLS):
			CONTENT = {}
			if Core.getSection(FILE_OPEN, "Manage_NSS/Pool/" + VAL['poolName'] + "/OwnedVolumes.xml", CONTENT):
				for LINE in CONTENT:
					if CONTENT[LINE].startswith("<volumeName>"):
						VOL_NAME = re.search(r'<volumeName>(.+?)</volumeName>', CONTENT[LINE]).group(1).strip()
						POOLS[IDX]['poolVolumes'].append(VOL_NAME)

		# get pool attributes if present
		FILE_OPEN = "novell-nss.txt"
		for IDX, VAL in enumerate(POOLS):
			CONTENT = {}
			DUP_KEYS = []
			if Core.getSection(FILE_OPEN, "Manage_NSS/Pool/" + VAL['poolName'] + "/PoolInfo.xml", CONTENT):
				for LINE in CONTENT:
					MATCH = re.match(r'<(.+?)>(.+?)</.*>', CONTENT[LINE])
					if MATCH:
						if CONTENT[LINE].startswith("<result "):
							continue
						else:
							THIS_KEY = MATCH.group(1)
							if( THIS_KEY in POOLS[IDX] ):
								DUP_KEYS.append(THIS_KEY)
							else:
								POOLS[IDX][THIS_KEY] = MATCH.group(2).split()[0].strip()
						if CONTENT[LINE].startswith("<enabledAttributes>"):
							POOLS[IDX]['enabledAttributes'] = MATCH.group(2).strip()
					POOLS[IDX]['duplicateKeys'] = DUP_KEYS

			# remove duplicate keys
			for DUPLICATE_KEY in DUP_KEYS:
				del POOLS[IDX][DUPLICATE_KEY]

	return POOLS

def getNSSModInfo():
	"""
	Gets all NSS modules in a dictionary of dictionaries gathered from the
	'echo modules > /dev/nsscmd' section of novell-nss.txt.

	Args:		None
	Returns:	Dictionary of Dictionaries
	Each module name is the key to a dictionary for it's version, build and snap date information. 
	Each module has the following keys:

	<module_name> (string) - The name of the module found in the novell-nss.txt file. It is always uppercase.
	version (string) - The module version string.
	build (string) - The module build number
	snapDate (string) - The date the module was built.

	Example:

	NSS_MODULES = oes.getNSSModInfo()
	FOUND = False
	MODULE_NAME = 'NSS'
	BAD_VERSION = '4.12a'
	for MOD in NSS_MODULES:
		if( MODULE_NAME == MOD ):
			FOUND = True
			break
	if( FOUND ):
		if( NSS_MODULES[MODULE_NAME]['version'] == BAD_VERSION ):
			Core.updateStatus(Core.WARN, "Update to resolve potential " + MODULE_NAME + " module issues")
		else:
			Core.updateStatus(Core.IGNORE, "We do not care about this " + MODULE_NAME + " module version")
	else:
		Core.updateStatus(Core.ERROR, "NSS module not found: " + MODULE_NAME)

	"""
	FILE_OPEN = "novell-nss.txt"
	SECTION = "echo modules "
	CONTENT = {}
	IN_STATE = False
	NSS_MODULE_INFO = {}
	START = re.compile(r'^\s*----------')
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if( IN_STATE ):
				if CONTENT[LINE].startswith("#=="):
					IN_STATE = False
				else:
					TMP = CONTENT[LINE].split()
					if( len(TMP) == 4 ):
						NSS_MODULE_INFO[TMP[0].upper()] = {'version': TMP[1], 'build': TMP[2], 'snapDate': TMP[3]}
			elif START.search(CONTENT[LINE]):
				IN_STATE = True

#	for MOD in NSS_MODULE_INFO:
#		print "{0:8} = {1}".format(MOD, str(NSS_MODULE_INFO[MOD]))

	return NSS_MODULE_INFO
