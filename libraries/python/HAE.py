"""
Supportconfig Analysis Library for HAE python patterns

Library of functions for creating python patterns specific to 
High Availability Extension (HAE) clustering
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
#  Modified: 2014 Jun 17
#
##############################################################################

import sys
import re
import Core
import string

def haeEnabled():
	"""
	Determines if an HAE cluster is enabled on the node based on a corosysnc.conf file.

	Args:		None
	Returns:	True if enabled, False if disabled
	Example:

	if HAE.haeEnabled():
		Core.updateStatus(Core.IGNORE, "HAE Cluster enabled")
	else:
		Core.updateStatus(Core.WARN, "HAE Cluster disabled")
	"""
	FILE_OPEN = 'ha.txt'
	CONTENT = {}

	if Core.listSections(FILE_OPEN, CONTENT):
		for LINE in CONTENT:
#			print CONTENT[LINE]
			if "corosync.conf" in CONTENT[LINE]:
				return True
	return False

def haeConnected():
	"""
	Determines if the node is connected to the HAE cluster.

	Args:		None
	Returns:	True if connected, False if disconnected
	Example:

	if HAE.haeConnected():
		Core.updateStatus(Core.IGNORE, "Node connected to HAE Cluster")
	else:
		Core.updateStatus(Core.WARN, "Node is disconnected, start HAE cluster services")
	"""
	FILE_OPEN = 'ha.txt'
	SECTION = 'cibadmin -Q'
	CONTENT = {}
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		CONNECTED = re.compile('<cib.*epoch=')
		for LINE in CONTENT:
			if CONNECTED.search(CONTENT[LINE]):
				return True
	return False

def getSBDInfo():
	"""
	Gets split brain detection partition information. Gathers information from the sbd dump command and the /etc/sysconfig/sbd file. SBD partitions with invalid sbd dump output are ignored.

	Args:		None
	Returns:	List of SBD Dictionaries with keys
		SBD_DEVICE (String) - The /etc/sysconfig/sbd SDB_DEVICE variable. This value applies to all and is stored with each sbd device.
		SBD_OPTS (String) - The /etc/sysconfig/sbd SBD_OPTS variable
		Version (Int) - The SDB header version string
		Slots (Int) - The number of SDB slots
		Sector_Size (Int) - The SBD sector size
		Watchdog (Int) - The SBD watchdog timeout
		Allocate (Int) - The SBD allocate timeout
		Loop (Int) - The SBD loop timeout
		MsgWait (Int) - The SBD msgwait timeout
	Example:

	SBD = HAE.getSBDInfo()
	MSG_WAIT_MIN = 300
	MSG_WAIT_OVERALL = MSG_WAIT_MIN
	# Find the smallest msgwait value among the SBD partitions
	for I in range(0, len(SBD)):
		if( SBD[I]['MsgWait'] < MSG_WAIT_OVERALL ):
			MSG_WAIT_OVERALL = SBD[I]['MsgWait']
	# See if the smallest msgwait is less than the minimum required
	if ( MSG_WAIT_OVERALL < MSG_WAIT_MIN ):
		Core.updateStatus(Core.REC, "Consider changing your msgwait time")
	else:
		Core.updateStatus(Core.IGNORE, "The msgwait is sufficient")
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

def getNodeInfo():
	"""
	Gets cluster node information from the cibadmin -Q output or cib.xml if the node is not connected to the cluster. It includes information from the <node> and <node_state> tags. Only key/value pairs within the <node_state> tag itself are included, not tags below <node_state>.

	Args:		None
	Returns:	List of Node Dictionaries with keys
		*All key:value pairs are derived from the configuration file itself.
	Example:

	STANDBY_NODES = []
	NODES = HAE.getNodeInfo()
	for I in range(0, len(NODES)):
		# If the standby key exists in the node dictionary, proceed
		if "standby" in NODES[I]:
			if 'on' in NODES[I]['standby']:
				STANDBY_NODES.append(NODES[I]['uname'])
	if( len(STANDBY_NODES) > 0 ):
		Core.updateStatus(Core.WARN, "Node(s) in standby mode: " + " ".join(STANDBY_NODES))
	else:
		Core.updateStatus(Core.IGNORE, "Node(s) in standby mode: None")
	"""
	IDX_KEY = 0
	IDX_VALUE = 1
	NODES = []
	NODE = {}
	FILE_OPEN = 'ha.txt'
	CONTENT = {}
	inNode = False
	endNode = re.compile('/>$')
	if Core.getSection(FILE_OPEN, 'cibadmin -Q', CONTENT):
		for LINE in CONTENT:
			DATA = CONTENT[LINE].strip()
			if "</nodes>" in DATA:
				break
			elif inNode:
				if "</node>" in DATA:
					NODES.append(dict(NODE))
					NODE = {}
					inNode = False
				elif "<nvpair" in CONTENT[LINE]:
					PARTS = re.sub('^<nvpair|/>$|>$|"', '', DATA).strip().split()
#					print "cibadmin PARTS = " + str(PARTS)
					KEY = ''
					VALUE = ''
					for I in range(0, len(PARTS)):
						if "name" in PARTS[I].lower():
							KEY = PARTS[I].split("=")[IDX_VALUE]
						elif "value" in PARTS[I].lower():
							VALUE = re.sub('/>.*$', '', PARTS[I].split("=")[IDX_VALUE])
					NODE.update({KEY:VALUE})
			elif "<node " in DATA:
				inNode = True
				if endNode.search(DATA):
					inNode = False
				PARTS = re.sub('^<node|/>$|>$|"', '', DATA).strip().split()
#				print "cibadmin PARTS = " + str(PARTS)
				KEY = ''
				VALUE = ''
				for I in range(0, len(PARTS)):
					KEY = PARTS[I].split("=")[IDX_KEY]
					VALUE = PARTS[I].split("=")[IDX_VALUE]
					NODE.update({KEY:VALUE})
				if not inNode:
					NODES.append(dict(NODE))
					NODE = {}
		# Add node state information on connected nodes
		for LINE in CONTENT:
			if "<node_state " in CONTENT[LINE]:
				NODE_STATE = {}
				PARTS = re.sub('<node_state|/>$|>$|"', '', CONTENT[LINE]).strip().split()
#				print "cibadmin PARTS = " + str(PARTS)
				KEY = ''
				VALUE = ''
				for I in range(0, len(PARTS)):
					KEY = PARTS[I].split("=")[IDX_KEY]
					VALUE = PARTS[I].split("=")[IDX_VALUE]
					NODE_STATE.update({KEY:VALUE})
				for I in range(0, len(NODES)):
					if( NODES[I]['id'] == NODE_STATE['id'] ):
						NODES[I].update(NODE_STATE)
						break

	if( len(NODES) == 0 ):
		if Core.getSection(FILE_OPEN, 'cib.xml$', CONTENT):
			for LINE in CONTENT:
				DATA = CONTENT[LINE].strip()
				if "</nodes>" in DATA:
					break
				elif inNode:
					if "</node>" in DATA:
						NODES.append(dict(NODE))
						NODE = {}
						inNode = False
					elif "<nvpair" in CONTENT[LINE]:
						PARTS = re.sub('^<nvpair|/>$|>$|"', '', DATA).strip().split()
#						print "cib.xml PARTS = " + str(PARTS)
						KEY = ''
						VALUE = ''
						for I in range(0, len(PARTS)):
							if "name" in PARTS[I].lower():
								KEY = PARTS[I].split("=")[IDX_VALUE]
							elif "value" in PARTS[I].lower():
								VALUE = re.sub('/>.*$', '', PARTS[I].split("=")[IDX_VALUE])
						NODE.update({KEY:VALUE})
				elif "<node " in DATA:
					inNode = True
					if endNode.search(DATA):
						inNode = False
					PARTS = re.sub('^<node|/>$|>$|"', '', DATA).strip().split()
#					print "cib.xml PARTS = " + str(PARTS)
					KEY = ''
					VALUE = ''
					for I in range(0, len(PARTS)):
						KEY = PARTS[I].split("=")[IDX_KEY]
						VALUE = PARTS[I].split("=")[IDX_VALUE]
						NODE.update({KEY:VALUE})
					if not inNode:
						NODES.append(dict(NODE))
						NODE = {}
		
#	print "NODES = " + str(len(NODES))
#	for I in range(0, len(NODES)):
#		print "NODE[" + str(I) + "] =  " + str(NODES[I]) + "\n"
	return NODES

def getClusterConfig():
	"""
	Gets cluster configuration information from the cibadmin -Q output or cib.xml if the node is not connected to the cluster. It includes information from the <cib> and <cluster_property_set> tags.

	Args:		None
	Returns:	Dictionary with keys
		connected-to-cluster (Boolean) - True if the node is connected to the cluster, and False if not
		*All other key:value pairs are derived from the cluster configuration file itself
	Example:

	CLUSTER = HAE.getClusterConfig()
	if 'stonith-enabled' in CLUSTER:
		if "true" in CLUSTER['stonith-enabled']:
			Core.updateStatus(Core.IGNORE, "Stonith is enabled for the cluster")
		else:
			Core.updateStatus(Core.WARN, "Stonith is disabled for the cluster")
	else:
		Core.updateStatus(Core.WARN, "Stonith is disabled by default for the cluster")
	"""
	IDX_VALUE = 1
	CLUSTER = {}
	FILE_OPEN = 'ha.txt'
	CONTENT = {}
	inBootStrap = False
	if Core.getSection(FILE_OPEN, 'cibadmin -Q', CONTENT):
		for LINE in CONTENT:
			if inBootStrap:
				if "</cluster_property_set>" in CONTENT[LINE]:
					inBootStrap = False
					break
				elif "<nvpair" in CONTENT[LINE]:
					PARTS = CONTENT[LINE].replace('"', '').strip().split()
#					print "cibadmin PARTS = " + str(PARTS)
					KEY = ''
					VALUE = ''
					for I in range(0, len(PARTS)):
						if "name" in PARTS[I].lower():
							KEY = PARTS[I].split("=")[IDX_VALUE]
						elif "value" in PARTS[I].lower():
							VALUE = re.sub('/>.*$', '', PARTS[I].split("=")[IDX_VALUE])
					CLUSTER.update({KEY:VALUE})
			elif "<cluster_property_set" in CONTENT[LINE]:
				inBootStrap = True
				CLUSTER.update({'connected-to-cluster':True})
			elif "<cib " in CONTENT[LINE]:
				PARTS = re.sub('<cib|>', '', CONTENT[LINE]).strip().split('"')
				if( len(PARTS[-1]) == 0 ):
					del(PARTS[-1])
#				print "cibadmin PARTS = " + str(PARTS)
				key = re.compile("=$")
				for I in range(0, len(PARTS)):
					if key.search(PARTS[I]):
						KEY_STR = PARTS[I].strip().strip('=')
					else:
						CLUSTER.update({KEY_STR:PARTS[I].strip()})

	if( len(CLUSTER) == 0 ):
		#The node is not connected to the cluster, so get the information from the cib.xml file
		if Core.getSection(FILE_OPEN, 'cib.xml$', CONTENT):
			for LINE in CONTENT:
				if inBootStrap:
					if "</cluster_property_set>" in CONTENT[LINE]:
						inBootStrap = False
						break
					elif "<nvpair" in CONTENT[LINE]:
						PARTS = CONTENT[LINE].replace('"', '').strip().split()
#						print "cib.xml PARTS = " + str(PARTS)
						KEY = ''
						VALUE = ''
						for I in range(0, len(PARTS)):
							if "name" in PARTS[I].lower():
								KEY = PARTS[I].split("=")[IDX_VALUE]
							elif "value" in PARTS[I].lower():
								VALUE = re.sub('/>.*$', '', PARTS[I].split("=")[IDX_VALUE])
						CLUSTER.update({KEY:VALUE})
				elif "<cluster_property_set" in CONTENT[LINE]:
					inBootStrap = True
					CLUSTER.update({'connected-to-cluster':False})
				elif "<cib " in CONTENT[LINE]:
					PARTS = re.sub('<cib|>', '', CONTENT[LINE]).strip().split('"')
					if( len(PARTS[-1]) == 0 ):
						del(PARTS[-1])
#					print "cib.xml PARTS = " + str(PARTS)
					key = re.compile("=$")
					for I in range(0, len(PARTS)):
						if key.search(PARTS[I]):
							KEY_STR = PARTS[I].strip().strip('=')
						else:
							CLUSTER.update({KEY_STR:PARTS[I].strip()})

#	print "CLUSTER Size = " + str(len(CLUSTER))
#	print "CLUSTER =      " + str(CLUSTER)
	return CLUSTER

def getConfigCTDB():
	"""
	Gets the /etc/sysconfig/ctdb configuration file information.

	Args:		None
	Returns:	Dictionary with keys
		*All key:value pairs are derived from the configuration file itself. All key names are changed to uppercase. All values are left as is.
	Example:

	CTDB = HAE.getConfigCTDB()
	if 'CTDB_START_AS_DISABLED' in CTDB:
		if "yes" in CTDB['CTDB_START_AS_DISABLED']:
			Core.updateStatus(Core.IGNORE, "CTDB Starting disabled")
		else:
			Core.updateStatus(Core.WARN, "CTDB Starting enabled")
	else:
		Core.updateStatus(Core.ERROR, "Missing CTDB_START_AS_DISABLED, ignoring test")
	"""
	IDX_KEY = 0
	IDX_VALUE = 1
	CONFIG = {}
	FILE_OPEN = 'ha.txt'
	SECTION = "/etc/sysconfig/ctdb"
	CONTENT = {}
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if( len(CONTENT[LINE]) > 0 ):
				KEY = CONTENT[LINE].split('=')[IDX_KEY].strip().upper()
				VALUE = re.sub('"|\'', '', CONTENT[LINE].split('=')[IDX_VALUE]).strip()
				CONFIG.update({KEY:VALUE})

#	print "CONFIG Size = " + str(len(CONFIG))
#	print "CONFIG =      " + str(CONFIG)
	return CONFIG

def getConfigCorosync():
	"""
	Gets Corosync configuration information from /etc/corosync/corosync.conf. All values are forced to lowercase.

	Args:		None
	Returns:	Dictionary with keys and lists
		*All key:value pairs are derived from the cluster configuration file itself. The totem interfaces are a list of dictionaries within the totem dictionary.
	Example:

	COROSYNC = HAE.getConfigCorosync()
	BINDADDRS = {}
	DUP_BINDADDRS = {}
	for I in range(0, len(COROSYNC['totem']['interface'])):
		ADDR = COROSYNC['totem']['interface'][I]['bindnetaddr']
		if ADDR in BINDADDRS:
			# There is a duplicate bind net address key, add the duplicate to the list
			DUP_BINDADDRS[ADDR] = True
		else:
			# The address is not a duplicate, add it to the list of bind net addresses to check
			BINDADDRS[ADDR] = True
	if( len(DUP_BINDADDRS) > 0 ):
		Core.updateStatus(Core.CRIT, "Detected Duplicate Corosync Bind Addresses: " + " ".join(DUP_BINDADDRS.keys()))
	else:
		Core.updateStatus(Core.IGNORE, "All Corosync Bind Addresses are Unique")
	"""
	IDX_KEY = 0
	IDX_VALUE = 1
	COROSYNC = {}
	FILE_OPEN = 'ha.txt'
	SECTION = 'corosync.conf'
	CONTENT = {}
	inTag = False
	inTotem = False
	inNet = False
	inMember = False
	
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		TAG = re.compile('^\S+\s+{')
		IFACE_ID = 'interface'
		IFACE = re.compile(IFACE_ID + '\s+{', re.IGNORECASE)
		MEMBER_ID = 'member'
		MEMBER = re.compile(MEMBER_ID + '\s+{', re.IGNORECASE)
		SKIP_LINE = re.compile('^#|^\s+$')
		for LINE in CONTENT:
			DATA = CONTENT[LINE].strip()
			if SKIP_LINE.search(DATA):
				continue
			if inTotem:
				if inNet:
					if inMember:
						if "}" in DATA:
							NET_DICT[MEMBER_ID].append(dict(MEMBER_DICT))
							inMember = False
						elif ":" in DATA:
							KEY = DATA.split(':')[IDX_KEY].strip()
							VALUE = DATA.split(':')[IDX_VALUE].strip()
							MEMBER_DICT.update({KEY:VALUE})
					elif "}" in DATA:
						COROSYNC[TAG_ID][IFACE_ID].append(dict(NET_DICT))
						inNet = False
					elif MEMBER.search(DATA):
						inMember = True
						MEMBER_DICT = {}
					elif ":" in DATA:
						KEY = DATA.split(':')[IDX_KEY].strip()
						VALUE = DATA.split(':')[IDX_VALUE].strip()
						NET_DICT.update({KEY:VALUE})
				elif "}" in DATA:
					COROSYNC[TAG_ID].update(dict(TAG_DICT))
					inTotem = False
				elif IFACE.search(DATA):
					inNet = True
					NET_DICT = {}
					NET_DICT[MEMBER_ID] = []
				elif ":" in DATA:
					KEY = DATA.split(':')[IDX_KEY].strip()
					VALUE = DATA.split(':')[IDX_VALUE].strip()
					TAG_DICT.update({KEY:VALUE})
			elif inTag:
				if "}" in DATA:
					COROSYNC[TAG_ID].update(dict(TAG_DICT))
					inTag = False
				elif ":" in DATA:
					KEY = DATA.split(':')[IDX_KEY].strip()
					VALUE = DATA.split(':')[IDX_VALUE].strip()
					TAG_DICT.update({KEY:VALUE})
			elif TAG.search(DATA):
				TAG_ID = DATA.split()[IDX_KEY]
				COROSYNC[TAG_ID] = {}
				TAG_DICT = {}
				if "totem" in DATA:
					inTotem = True
					COROSYNC[TAG_ID][IFACE_ID] = []
				else:
					inTag = True

	# print the data structure for debugging purposes
#	for X in COROSYNC:
#		for Y in COROSYNC[X]:
#			if 'interface' in Y:
#				for I in range(0, len(COROSYNC[X][Y])):
#					for Z in COROSYNC[X][Y][I]:
#						print ("COROSYNC[" + X + "][" + Y + "][" + str(I) + "][" + Z + "] : " + str(COROSYNC[X][Y][I][Z]))
#			else:
#				print ("COROSYNC[" + X + "][" + Y + "] : " + str(COROSYNC[X][Y]))

	return COROSYNC








