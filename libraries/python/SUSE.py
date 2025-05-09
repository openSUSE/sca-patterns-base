"""
Supportconfig Analysis Library for SUSE python patterns

Library of functions for creating python patterns specific to SUSE
"""
##############################################################################
#  Copyright (C) 2013-2025 SUSE LLC
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
#    Jason Record (jason.record@suse.com)
#    David Hamner (ke7oxh@gmail.com)
#
#  Modified: 2025 May 08
#  Version:  1.0.3
#
##############################################################################

import re
import Core
from Core import path
import datetime
import ast

# Kernel version constants
# https://www.suse.com/support/kb/doc/?id=000019587
SLE9GA       = '2.6.5-7.97'
SLE9SP0      = '2.6.5-7.97'
SLE9SP1      = '2.6.5-7.139'
SLE9SP2      = '2.6.5-7.191'
SLE9SP3      = '2.6.5-7.244'
SLE9SP4      = '2.6.5-7.308'
SLE9SP5      = '2.6.5-8'
SLE10GA      = '2.6.16.21-0.8'
SLE10SP0     = '2.6.16.21-0.8'
SLE10SP1     = '2.6.16.46-0.12'
SLE10SP2     = '2.6.16.60-0.21'
SLE10SP3     = '2.6.16.60-0.54.5'
SLE10SP4     = '2.6.16.60-0.85.1'
SLE10SP5     = '2.6.17'
SLE11GA      = '2.6.27.19-5'
SLE11SP0     = '2.6.27.19-5'
SLE11SP1     = '2.6.32.12-0.7'
SLE11SP2     = '3.0.13-0.27'
SLE11SP3     = '3.0.76-0.11.1'
SLE11SP4     = '3.0.101-0.63.1'
SLE12GA      = '3.12.28-4'
SLE12SP0     = '3.12.28-4'
SLE12SP1     = '3.12.49-11.1'
SLE12SP2     = '4.4.21-69'
SLE12SP3     = '4.4.73-5.1'
SLE12SP4     = '4.12.14-94.41'
SLE12SP5     = '4.12.14-120.1'
SLE15GA      = '4.12.14-23.1'
SLE15SP0     = '4.12.14-23.1'
SLE15SP1     = '4.12.14-195.1'
SLE15SP2     = '5.3.18-22.2'
SLE15SP3     = '5.3.18-57.3'
SLE15SP4     = '5.14.21-150400.22.1'
SLE15SP5     = '5.14.21-150500.53.2'
SLE15SP6     = '6.4.0-150600.21.3'
SLE15SP7     = '5.999' #Update to actual version when/if applicable
ALP1SP0      = '6.0' #Update to actual version when/if applicable

def packageInstalled(PackageName):
	"""
	The PackageName is installed on the server
	Args:		PackageName - The RPM package name to check if installed
	Returns:	True or False
					True	PackageName is installed
					False	PackageName is NOT installed
	Example:

	PACKAGE_NAME = 'bind'
	if ( SUSE.packageInstalled(PACKAGE_NAME) ):
		Core.updateStatus(Core.WARN, "The package " + PACKAGE_NAME + " is installed")
	else:
		Core.updateStatus(Core.IGNORE, "The package " + PACKAGE_NAME + " is NOT installed")	
	"""
	rpmInfo = getRpmInfo(PackageName)
	if "version" in rpmInfo:
		return True
	return False


def getRpmInfo(PackageName):
	"""
	Retrieves RPM package information from supportconfig files using the specified PackageName

	Args:		PackageName - RPM package name on which you want details
	Returns:	Dictionary with keys
					name (String) - The RPM package name
					version (String) - The RPM package version string
					vendor (String) - The RPM vendor
					installTime (String) - The date and time the package was installed
	Example:

	RPM_NAME = 'kernel-xen'
	RPM_INFO = SUSE.getRpmInfo(RPM_NAME)
	if( len(RPM_INFO) > 0 ):
		Core.updateStatus(STATUS_IGNORE, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is installed")
	else:
		Core.updateStatus(STATUS_WARNING, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is missing, install it")
	"""
	rpmInfo = {}
	fileOpen = "rpm.txt"
	section = "[0-9]{DISTRIBUTION}"
	content = {}
	tmpContent = {}
	#get name version and vendor
	if (Core.getSection(fileOpen, section, content)):
		for line in content:
			if content[line].startswith(PackageName + " "):
				tmpContent = re.sub(r' +', ' ', content[line])
				tmpContent = tmpContent.split(' ')
#				print "getRpmInfo: tmpContent = " + str(tmpContent)
				rpmInfo['name'] = tmpContent[0] #name
				rpmInfo['version'] = tmpContent[-1] #version
				tmpContent.pop(0)
				tmpContent.pop()
				rpmInfo['vendor'] = ' '.join(tmpContent).strip() #vendor
				#rpmInfo[1] = tmpContent[1,-2]

#	print "getRpmInfo: rpmInfo    = " + str(rpmInfo)
	#get install time
	section = "rpm -qa --last"
	content = {}
	if (Core.getSection(fileOpen, section, content)):
		for line in content:
			if content[line].startswith(PackageName):
				rpmInfo['installTime'] = content[line].split(' ',1)[1].strip()
#	print "getRpmInfo: rpmInfo    = " + str(rpmInfo)
	return rpmInfo

class PatchInfo:
	"""
	A class to retrieve patch information by patch name. The first patch name that matches the search string will be used for the patch information.

	Variables
	---------
	search_name = (String) The string used to find the patch from the name column
	patch_name = (String) The exact patch name string found in the name column
	patch_count = (Int) The number of patches that match patch_name
	installed = (Boolean) True if at least one patch is installed in the patch_name set, otherwise False
	all_installed = (Boolean) True if all patches in the patch_name set are installed, otherwise False
	needed = (Boolean) True if at least one patch is needed in the patch_name set, otherwise False
	valid = (Boolean) True if a valid updates.txt section with patch information was found, otherwise False
	patchlist = (List of Dictionaries) The dictionary keys correspond to the 'zypper patches' or 'rug pch' output columns with the exception of Installed
		Dictionary Keys:
			Category (String) The patch category like security or recommended
			Status (String) The patch status including Installed, NotApplicable, Applied, Needed, etc.
			Catalog (String) The catalog from which the patch came
			Version (String) The patch's version number string
			Name (String) The name of the patch
			Installed (Boolean) True if the patch is installed or applied, otherwise False

	Example:

	import Core
	import SUSE

	DEBUG = False
	PATCH = SUSE.PatchInfo('slessp3-kernel')
	if( DEBUG ):
		PATCH.debugPatchDisplay()
	if( PATCH.valid ):
		if( PATCH.all_installed ):
			Core.updateStatus(Core.IGNORE, "Patches have been applied")
		else:
			Core.updateStatus(Core.WARN, "Update server to apply missing kernel patches")
	else:
		Core.updateStatus(Core.ERROR, "ERROR: Invalid patch updates.txt section")
	"""
	patchCount = 0

	def __init__(self, search_name):
		PatchInfo.patchCount += 1
		self.search_name = search_name
		self.patch_name = ''
		self.patch_count = 0
		self.installed = False
		self.all_installed = True
		self.needed = False
		self.valid = False
		self.patchlist = []
		# populate the patchlist
		PATCH_DICTIONARY = {}
		FILE_OPEN = "updates.txt"
		SECTIONS = ['zypper --non-interactive --no-gpg-checks patches', '/rug pch']
		CONTENT = {}
		PATCH = re.compile(self.search_name, re.IGNORECASE)
		for SECTION in SECTIONS:
#			print "Check section: " + str(SECTION)
			if Core.getSection(FILE_OPEN, SECTION, CONTENT):
				for LINE in CONTENT:
					if PATCH.search(CONTENT[LINE]):
#						print CONTENT[LINE]
						PATCH_ARRAY = re.sub(r"\s+", "", CONTENT[LINE]).split("|")
						PATCH_DICTIONARY['Catalog'] = PATCH_ARRAY[0]
						PATCH_DICTIONARY['Name'] = PATCH_ARRAY[1]
						PATCH_DICTIONARY['Version'] = PATCH_ARRAY[2]
						PATCH_DICTIONARY['Category'] = PATCH_ARRAY[3]
						PATCH_DICTIONARY['Status'] = PATCH_ARRAY[4]
						if( PATCH_DICTIONARY['Status'] == "Installed" or PATCH_DICTIONARY['Status'] == "Applied" ):
							PATCH_DICTIONARY['Installed'] = True
							self.installed = True
						elif( PATCH_DICTIONARY['Status'] == "Needed" ):
							PATCH_DICTIONARY['Installed'] = False
							self.needed = True
							self.all_installed = False
						else:
							PATCH_DICTIONARY['Installed'] = False
							self.all_installed = False
#						print "  " + str(PATCH_DICTIONARY)
						self.patchlist.append(dict(PATCH_DICTIONARY))
						if( len(self.patch_name) == 0 ):
							self.patch_name = PATCH_DICTIONARY['Name']
							PATCH = re.compile(fr"\|\s+{self.patch_name}\s+\|")
				self.valid = True
				self.patch_count = len(self.patchlist)
#				print "Total Patches: " + str(self.patch_count) + "\n"
				break

		if( self.patch_count == 0 ):
			self.installed = False
			self.all_installed = False
			self.needed = False

	def getLastInstalled(self):
		"""
		Returns a dictionary of the last installed patch in the patch_name set based on the version string
		"""
		VER = 0
		PATCH_FOUND = {}
		for PATCH in self.patchlist:
			if( PATCH['Status'] == "Installed" or PATCH['Status'] == "Applied" ):
				if( PATCH['Version'] > VER ):
					VER = PATCH['Version']
					PATCH_FOUND = PATCH
		return PATCH_FOUND

	def getLastNeeded(self):
		"""
		Returns a dictionary of the last needed patch in the patch_name set based on the version string
		"""
		VER = 0
		PATCH_FOUND = {}
		for PATCH in self.patchlist:
			if( PATCH['Status'] == "Needed" ):
				if( PATCH['Version'] > VER ):
					VER = PATCH['Version']
					PATCH_FOUND = PATCH
		return PATCH_FOUND

	def debugPatchDisplay(self):
		"""
		Prints the entire list of dictionaries and the class variables. Used for debug purposes only.
		"""
		print("Patch List:")
		for patch in self.patchlist:
			print("  " + str(patch))
		print("PatchInfo.valid         " + str(self.valid))
		print("PatchInfo.patch_count   " + str(self.patch_count))
		print("PatchInfo.patchCount    " + str(PatchInfo.patchCount))
		print("PatchInfo.search_name   '" + str(self.search_name) + "'")
		print("PatchInfo.patch_name    '" + str(self.patch_name) + "'")
		print("PatchInfo.installed     " + str(self.installed))
		print("PatchInfo.all_installed " + str(self.all_installed))
		print("PatchInfo.needed        " + str(self.needed))

def getDriverInfo( DRIVER_NAME ):
	"""
	Gets information about the specified kernel driver

	Args:		DRIVER_NAME - The kernel driver name on which you want details
	Returns:	Dictionary with keys
					name (String) - The kernel driver name
					loaded (Boolean) - True if loaded, otherwise False
					filename (String) - The driver filename
					version (String) - The driver's version string
					license (String) - The driver's license string
					description (String) - Description of the driver
					srcversion (String) - The driver's source version
					supported (String) - Support status string, usually yes or no
					vermagic (String) - Version magic string
	Example:

	DRIVER_NAME = 'zapi'
	DRIVER_INFO = SUSE.getDriverInfo(DRIVER_NAME)
	if( DRIVER_INFO['loaded'] ):
		Core.updateStatus(STATUS_IGNORE, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is installed")
	else:
		Core.updateStatus(STATUS_WARNING, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is missing, install it")
	"""
	FILE_OPEN = "modules.txt"
	SECTION = "modinfo " + DRIVER_NAME
	DRIVER_KEYS_MISSING = [ 'filename', 'version', 'license', 'description', 'srcversion', 'supported', 'vermagic' ]
	DRIVER_DICTIONARY = { 'name': DRIVER_NAME, 'loaded': True, DRIVER_KEYS_MISSING[0]: '', DRIVER_KEYS_MISSING[1]: '', DRIVER_KEYS_MISSING[2]: '', DRIVER_KEYS_MISSING[3]: '', DRIVER_KEYS_MISSING[4]: '', DRIVER_KEYS_MISSING[5]: 'no', DRIVER_KEYS_MISSING[6]: '' }
	CONTENT = {}
	# Get the module's information section in modules.txt.
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			for KEY in DRIVER_KEYS_MISSING:
				# find and extract module key/value pairs
				if CONTENT[LINE].startswith(KEY + ": "):
					ELEMENTS = CONTENT[LINE].split()
					# remove the key from the key/value pair
					del ELEMENTS[0]
					# assign the value to the dictionary key
					DRIVER_DICTIONARY[KEY] = ' '.join(ELEMENTS)
	else:
		# supportconfig only get module information for loaded modules
		DRIVER_DICTIONARY['loaded'] = False
	return DRIVER_DICTIONARY

def getServiceInfo(SERVICE_NAME):
	"""
	Returns a dictionary of system service information for SERVICE_NAME

	Args:		SERVICE_NAME - Name of System V service
	Returns:	Dictionary with keys
					Name (String) - System V service name
					Running (Integer) - -1=Unknown, 0=Unused or Dead, 1=Running
					BootLevels (String) - A list of runlevel numbers in which the service is 
						turned on for boot. An empty string means the service is turned off at
						boot for all runlevels.
					RunLevel (String) - The current system runlevel
					OnForRunLevel (Bool) - False=Service is turned off for the current runlevel, True=Service is turned on for the current runlevel
					Known (Bool) - True=The service is found in the service table, False=The service is not known and only partial information may be included.
	Example:

	SERVICE = 'cups'
	SERVICE_INFO = SUSE.getServiceInfo(SERVICE)
	if( SERVICE_INFO['Running'] > 0 ):
		Core.updateStatus(Core.IGNORE, "Service is running: " + str(SERVICE_NAME));
	else:
		Core.updateStatus(Core.WARN, "Service is down: " + str(SERVICE_NAME));
	"""
	SERVICE_TABLE = {
		'apache2': 'web.txt',
		'atd': 'cron.txt',
		'audit': 'security-audit.txt',
		'auditd': 'security-audit.txt',
		'autofs': 'fs-autofs.txt',
		'boot.subdomain': 'security-apparmor.txt',
		'cron': 'cron.txt',
		'cset.init.d': 'slert.txt',
		'cset': 'slert.txt',
		'cups': 'print.txt',
		'dhcpd': 'dhcp.txt',
		'heartbeat': 'ha.txt',
		'iscsitarget': 'fs-iscsi.txt',
		'kdump': 'crash.txt',
		'ldap': 'ldap.txt',
		'libvirtd': 'kvm.txt',
		'multipathd': 'mpio.txt',
		'named': 'dns.txt',
		'network': 'network.txt',
		'nfslock': 'nfs.txt',
		'nfs': 'nfs.txt',
		'nfsserver': 'nfs.txt',
		'nmb': 'samba.txt',
		'nscd': 'network.txt',
		'ntp': 'ntp.txt',
		'o2cb': 'ocfs2.txt',
		'ocfs2': 'ocfs2.txt',
		'openais': 'ha.txt',
		'openibd': 'ib.txt',
		'open-iscsi': 'fs-iscsi.txt',
		'owcimomd': 'cimom.txt',
		'portmap': 'nfs.txt',
		'rcd': 'updates-daemon.txt',
		'sfcb': 'cimom.txt',
		'slert': 'slert.txt',
		'slpd': 'slp.txt',
		'smartd': 'fs-smartmon.txt',
		'smb': 'samba.txt',
		'smt': 'smt.txt',
		'sshd': 'ssh.txt',
		'winbind': 'samba.txt',
		'xend': 'xen.txt',
		'xntpd': 'ntp.txt',
	}
	SERVICE_INFO = {
		'Name': SERVICE_NAME,
		'Running': -1,
		'BootLevels': '',
		'RunLevel': '',
		'OnForRunLevel': False,
		'Known': False,
	}
	SECTION = ''
	CONTENT = {}
	COMPLETE_CONFIRMED = 4
	COMPLETE_COUNT = 0
	if SERVICE_NAME in SERVICE_TABLE:
		FILE_OPEN = SERVICE_TABLE[SERVICE_NAME]
		SERVICE_INFO['Known'] = True
	else:
		FILE_OPEN = 'basic-health-check.txt'

	if ( SERVICE_INFO['Known'] ):
		SERVICE_INFO['Running'] = 0
		SECTION = "/etc/init.d/" + SERVICE_NAME + " status"
		if Core.getSection(FILE_OPEN, SECTION, CONTENT):
			STATE = re.compile(r'running', re.IGNORECASE)
			for LINE in CONTENT:
				if STATE.search(CONTENT[LINE]):
					SERVICE_INFO['Running'] = 1
					break
	else:
		SECTION = '/bin/ps'
		if Core.getSection(FILE_OPEN, SECTION, CONTENT):
			STATE = re.compile(fr"/{SERVICE_NAME}\s|/{SERVICE_NAME}$", re.IGNORECASE)
			for LINE in CONTENT:
				if STATE.search(CONTENT[LINE]):
#					print "State Found: " + str(CONTENT[LINE])
					SERVICE_INFO['Running'] = 1
					break

	FILE_OPEN = 'boot.txt'
	SECTION = "boot.msg"
	CONTENT = {}
	IDX_RUN_LEVEL = 4
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		STATE = re.compile(r"Master Resource Control: runlevel.*has been reached", re.IGNORECASE)
		for LINE in CONTENT:
			if STATE.search(CONTENT[LINE]):
				SERVICE_INFO['RunLevel'] = CONTENT[LINE].strip().split()[IDX_RUN_LEVEL]
				break

	FILE_OPEN = 'chkconfig.txt'
	SECTION = "chkconfig --list"
	CONTENT = {}
	IDX_RUN_LEVEL = 0
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		STATE = re.compile(r"^" + SERVICE_NAME + " ", re.IGNORECASE)
		LINE_CONTENT = {}
		for LINE in CONTENT:
			if STATE.search(CONTENT[LINE]):
				LINE_CONTENT = CONTENT[LINE].strip().split()
				SWITCH = re.compile(r"\d:on", re.IGNORECASE)
				for I in range(1, 8):
					if SWITCH.search(LINE_CONTENT[I]):
						RUN_LEVEL = str(LINE_CONTENT[I].split(':')[IDX_RUN_LEVEL])
						SERVICE_INFO['BootLevels'] += RUN_LEVEL
						if ( SERVICE_INFO['RunLevel'] == RUN_LEVEL ):
							SERVICE_INFO['OnForRunLevel'] = True
				break

#	print "getServiceInfo: SERVICE_INFO = " + str(SERVICE_INFO)
	return SERVICE_INFO

def getServiceDInfo(SERVICE_NAME):
	"""
	Returns a dictionary of systemd service information for SERVICE_NAME

	Args:		SERVICE_NAME - Name of systemd service
	Returns:	Dictionary with keys corresponding to systemctl show SERVICE_NAME
				output.
	Example:

	SERVICE = 'cups.service'
	SERVICE_INFO = SUSE.getServiceDInfo(SERVICE)
	if( SERVICE_INFO['SubState'] == 'running' ):
		Core.updateStatus(Core.IGNORE, "Service is running: " + str(SERVICE_NAME));
	else:
		Core.updateStatus(Core.WARN, "Service is down: " + str(SERVICE_NAME));
	"""
	FILE_OPEN = "systemd.txt"
	SECTION = "systemctl show '" + str(SERVICE_NAME) + "'"
	SERVICED_DICTIONARY = {}
	CONTENT = {}
	# Get the service information section in systemd.txt.
	if Core.getSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			ELEMENT = CONTENT[LINE].split('=')
			KEY = ELEMENT[0]
			# remove the key from the key/value pair
			del ELEMENT[0]
			# assign the value to the dictionary key
			SERVICED_DICTIONARY[KEY] = '='.join(ELEMENT)
	return SERVICED_DICTIONARY

def serviceDHealth(SERVICE_NAME):
	"""
	Reports the health of the specified systemd service

	Args:		SERVICE_NAME
	Returns:	N/A
	Example:	

	PACKAGE = "cups"
	SERVICE = "cups.service"
	if( SUSE.packageInstalled(PACKAGE) ):
		SUSE.serviceDHealth(SERVICE)
	else:
		Core.updateStatus(Core.ERROR, "Basic Service Health; Package Not Installed: " + str(PACKAGE))
	"""
	SERVICE_DICTIONARY = getServiceDInfo(SERVICE_NAME)
	RC = 1
	if( not SERVICE_DICTIONARY ):
		Core.updateStatus(Core.ERROR, "Basic Service Health; Service not found: " + str(SERVICE_NAME));
	elif( SERVICE_DICTIONARY['LoadState'] == 'not-found' ):
		Core.updateStatus(Core.ERROR, "Basic Service Health; Service not found: " + str(SERVICE_NAME));
	elif( 'UnitFileState' in SERVICE_DICTIONARY ):
		if( SERVICE_DICTIONARY['UnitFileState'] == 'enabled' ):
			if( SERVICE_DICTIONARY['SubState'] == 'running' ):
				Core.updateStatus(Core.IGNORE, "Basic Service Health; Turned on at boot, and currently running: " + str(SERVICE_NAME));
				RC = 0
			else:
				Core.updateStatus(Core.CRIT, "Basic Service Health; Turned on at boot, but not running: " + str(SERVICE_NAME));
		elif( SERVICE_DICTIONARY['UnitFileState'] == 'disabled' ):
			if( SERVICE_DICTIONARY['SubState'] == 'running' ):
				Core.updateStatus(Core.WARN, "Basic Service Health; Turned off at boot, but currently running: " + str(SERVICE_NAME));
			else:
				Core.updateStatus(Core.IGNORE, "Basic Service Health; Turned off at boot, but not running: " + str(SERVICE_NAME));
		elif( SERVICE_DICTIONARY['UnitFileState'] == 'static' ):
			if( SERVICE_DICTIONARY['SubState'] == 'running' ):
				Core.updateStatus(Core.IGNORE, "Basic Service Health; Static service is currently running: " + str(SERVICE_NAME));
				RC = 0
			else:
				Core.updateStatus(Core.WARN, "Basic Service Health; Static service SubState '" + SERVICE_DICTIONARY['SubState'] + "': " + str(SERVICE_NAME));
		else:
			Core.updateStatus(Core.ERROR, "Basic Service Health; Unknown UnitFileState '" + str(SERVICE_DICTIONARY['UnitFileState']) + "': " + str(SERVICE_NAME));
	else:
		if( SERVICE_DICTIONARY['ActiveState'] == 'failed' ):
			Core.updateStatus(Core.CRIT, "Basic Service Health; Service failure detected: " + str(SERVICE_NAME));
		elif( SERVICE_DICTIONARY['ActiveState'] == 'inactive' ):
			Core.updateStatus(Core.IGNORE, "Basic Service Health; Service is not active: " + str(SERVICE_NAME));
		elif( SERVICE_DICTIONARY['ActiveState'] == 'active' ):
			if( SERVICE_DICTIONARY['SubState'] == 'running' ):
				Core.updateStatus(Core.IGNORE, "Basic Service Health; Service is running: " + str(SERVICE_NAME));
			else:
				Core.updateStatus(Core.CRIT, "Basic Service Health; Service is active, but not running: " + str(SERVICE_NAME));
		else:
			Core.updateStatus(Core.ERROR, "Basic Service Health; Unknown ActiveState '" + SERVICE_DICTIONARY['ActiveState'] + "': " + str(SERVICE_NAME));

	return RC

def compareRPM(package, versionString):
	"""
	Compares the versionString to the installed package's version

	Args:		package - RPM package name
				versionString - RPM package version string to compare against
	Returns:	-1, 0, 1
					-1	if RPM_NAME older than RPM_VERSION
					0	if RPM_NAME equals RPM_VERSION
					1	if RPM_NAME newer than RPM_VERSION
	Example:

	RPM_NAME = 'mypackage'
	RPM_VERSION = '1.1.0'
	if( SUSE.packageInstalled(RPM_NAME) ):
		INSTALLED_VERSION = SUSE.compareRPM(RPM_NAME, RPM_VERSION)
		if( INSTALLED_VERSION <= 0 ):
			Core.updateStatus(Core.CRIT, "Bug detected in " + RPM_NAME + ", update server for fixes")
		else:
			Core.updateStatus(Core.IGNORE, "Bug fixes applied for " + RPM_NAME)
	else:
		Core.updateStatus(Core.ERROR, "ERROR: RPM package not installed: " + RPM_NAME)
	"""
	try:
		#get package version
		packageVersion = getRpmInfo(package)['version']
#		print "compareRPM: Package                  = " + str(package)
#		print "compareRPM: Given version            = " + str(kernelVersion)
#		print "compareRPM: Version in Supportconfig = " + str(foundVersion)

		return Core.compareVersions(packageVersion, versionString)
	except Exception as error:
		#error out...
		Core.updateStatus(Core.ERROR, "ERROR: Package info not found -- " + str(error))

def compareKernel(kernelVersion):
	"""
	Checks if kernel version is newer then given version
	Args:		kernelVersion - The kernel version string to compare
	Returns:	-1, 0, 1
					-1	if Installed kernel version older than kernelVerion
					0	if Installed kernel version equals kernelVerion
					1	if Installed kernel version newer than kernelVerion
	Example:

	KERNEL_VERSION = '4.12.14'
	INSTALLED_VERSION = SUSE.compareKernel(KERNEL_VERSION)
	if( INSTALLED_VERSION < 0 ):
		Core.updateStatus(Core.CRIT, "Bug detected in kernel version " + KERNEL_VERSION + " or before, update server for fixes")
	else:
		Core.updateStatus(Core.IGNORE, "Bug fixes applied in kernel version " + KERNEL_VERSION + " or higher")
	"""
	foundVersion = ""
	fileOpen = "basic-environment.txt"
	section = "uname -a"
	content = {}
	if (Core.getSection(fileOpen, section, content)):
		for line in content:
			if content[line] != "":
				foundVersion = content[line].split(" ")[2]
#	print "compareKernel: Given version            = " + str(kernelVersion)
#	print "compareKernel: Version in Supportconfig = " + str(foundVersion)
	return Core.compareVersions(foundVersion, kernelVersion)

def getHostInfo():
	"""
	Gets information about the server

	Args:		None
	Returns:	Dictionary with keys
		Hostname (String) - The hostname of the server analyzed
		KernelVersion (String) - The running kernel version
		Architecture (String)
		Distro (String) - The name of the distribution
		DistroVersion (Int) - The major distribution version number
		DistroPatchLevel (Int) - The distribution service patch level
	Example:

	import re
	SERVER = SUSE.getHostInfo()
	SLE = re.compile(r"SUSE Linux Enterprise Server", re.IGNORECASE)
	if SLE.search(SERVER['Distro']):
		if( SERVER['DistroVersion'] >= 11 and SERVER['DistroVersion'] < 12 ):
			Core.updateStatus(Core.WARN, "SLES" + str(SERVER['DistroVersion']) + "SP" + str(SERVER['DistroPatchLevel']) + ": Testing required")
		else:
			Core.updateStatus(Core.IGNORE, "SLES" + str(SERVER['DistroVersion']) + "SP" + str(SERVER['DistroPatchLevel']) + ": No Testing Needed")
	else:
		Core.updateStatus(Core.ERROR, SERVER['Distro'] + ": Invalid Distribution for Test Case")
	"""
	SERVER_DICTIONARY = { 
		'Hostname': '',
		'KernelVersion': '',
		'Architecture': '',
		'Distro': '',
		'DistroVersion': -1,
		'DistroPatchLevel': 0,
	}
	FILE_OPEN = "basic-environment.txt"
	CONTENT = {}
	IDX_HOSTNAME = 1
	IDX_VERSION = 2
	IDX_PATCHLEVEL = 1
	IDX_DISTRO = 0
	IDX_OSDISTRO = 1
	IDX_ARCH = -2
	IDX_VALUE = 1
	IDX_MAJOR = 0
	UNAME_FOUND = False
	OSRELEASE_FOUND = False
	RELEASE_FOUND = False
	RELEASE_LINE = 0

	try:
		FILE = open(Core.path + "/" + FILE_OPEN, "rt", errors="ignore")
	except Exception as error:
#		print "getHostInfo: Error opening file: %s" % error
		Core.updateStatus(Core.ERROR, "ERROR: Cannot open " + FILE_OPEN)

	OSRELEASE = re.compile(r'/etc/os-release', re.IGNORECASE)
	RELEASE = re.compile(r'/etc/SuSE-release', re.IGNORECASE)
	for LINE in FILE:
		if UNAME_FOUND:
			SERVER_DICTIONARY['Hostname'] = LINE.split()[IDX_HOSTNAME]
			SERVER_DICTIONARY['KernelVersion'] = LINE.split()[IDX_VERSION]
			SERVER_DICTIONARY['Architecture'] = LINE.split()[IDX_ARCH]
			UNAME_FOUND = False
		elif OSRELEASE_FOUND:
			RELEASE_LINE += 1
			if "#==[" in LINE:
				RELEASE_FOUND = False
			elif LINE.startswith('VERSION_ID'):
				VERSION_ID_INFO = LINE.replace('"', "").strip().split('=')[IDX_VALUE].split('.')
				if( len(VERSION_ID_INFO) > 1 ):
					SERVER_DICTIONARY['DistroVersion'] = int(VERSION_ID_INFO[IDX_MAJOR].strip('"'))
					SERVER_DICTIONARY['DistroPatchLevel'] = int(VERSION_ID_INFO[IDX_PATCHLEVEL].strip('"'))
				else:			
					SERVER_DICTIONARY['DistroVersion'] = int(VERSION_ID_INFO[IDX_MAJOR].strip('"'))
					SERVER_DICTIONARY['DistroPatchLevel'] = 0
			elif LINE.startswith('PRETTY_NAME'):
				SERVER_DICTIONARY['Distro'] = re.split(r'=', LINE)[IDX_OSDISTRO].strip()
		elif RELEASE_FOUND:
			RELEASE_LINE += 1
			if "#==[" in LINE:
				RELEASE_FOUND = False
			elif ( RELEASE_LINE == 1 ):
				SERVER_DICTIONARY['Distro'] = re.split(r'\(|\)', LINE)[IDX_DISTRO].strip()
			else:
				if LINE.startswith('VERSION'):
					SERVER_DICTIONARY['DistroVersion'] = int(LINE.split('=')[IDX_VALUE].strip())
				elif LINE.startswith('PATCHLEVEL'):
					SERVER_DICTIONARY['DistroPatchLevel'] = int(LINE.split('=')[IDX_VALUE].strip())
		elif "uname -a" in LINE:
			UNAME_FOUND = True
		elif OSRELEASE.search(LINE):
			OSRELEASE_FOUND = True
		elif RELEASE.search(LINE):
			RELEASE_FOUND = True

	FILE.close()
#	print "getHostInfo: SERVER_DICTIONARY = " + str(SERVER_DICTIONARY)
	return SERVER_DICTIONARY
	

def getSCInfo():
	"""
	Gets information about the supportconfig archive itself

	Args:		None
	Returns:	Dictionary with keys
					envValue (String) - Environment value
					kernelValue (Integer) - Kernel number based on its version
					cmdline (String) - Supportconfig's command line arguments
					config (String) - Supportconfig configuration options
					version (String) - Supportconfig version
					scriptDate (String) - Supportconfig script date
	Example:

	REQUIRED_VERSION = '2.25-173';
	SC_INFO = SUSE.getSCInfo();
	if( Core.compareVersions(SC_INFO['version'], REQUIRED_VERSION) >= 0 ):
		Core.updateStatus(Core.IGNORE, "Supportconfig v" + str(SC_INFO['version']) + " meets minimum requirement")
	else:
		Core.updateStatus(Core.WARN, "Supportconfig v" + str(SC_INFO['version']) + " NOT sufficient, " + str(REQUIRED_VERSION) + " or higher needed")	
	"""
	scInfo = {}
	fileOpen = "supportconfig.txt"
	section = "supportutils"
	content = {}
	tmpContent = {}
	if (Core.getSection(fileOpen, section, content)):
		for line in content:
			if "Environment Value" in content[line]:
				tmpContent = content[line].split(' ')
				scInfo['envValue'] = tmpContent[-2]
				scInfo['kernelValue'] = tmpContent[-1][1:-1]
			elif "Command with Args" in content[line]:
				scInfo['cmdline'] = content[line].split(':')[-1].strip()
			elif "Using Options" in content[line]:
				scInfo['config'] = content[line].split(':')[-1].strip()
			supportFile = open(Core.path	+ "/basic-environment.txt", 'r')
			supportFile.readline()
			supportFile.readline()
			scInfo['version'] = supportFile.readline().split(':')[-1].strip()
			scInfo['scriptDate'] =	supportFile.readline().split(':')[-1].strip()
	return scInfo

def securityAnnouncementPackageCheck(NAME, MAIN, LTSS, SEVERITY, TAG, PACKAGES):
	"""
	Specialty function for SUSE Security Announcements (http://lists.opensuse.org/opensuse-security-announce/) that checks the versions of the listed PACKAGES and displays a uniform output string. If any one of the packages listed is less than the fixed version in the PACKAGES dictionary, a hit is triggered. The MAIN is optional. If the MAIN package is installed the other PACKAGES are checked, otherwise no packages are checked. If MAIN is missing, all PACKAGES are checked.

	Args:		NAME (String) - The display name of the package group being checked
				MAIN (String) - The MAIN package that must be present as a condition of checking the others; leave blank to check all PACKAGES
				LTSS (Boolean) - True if an LTSS package, False if not
				SEVERITY (String) - The severity of the security announcement (ie 'Critical', 'Important', etc)
				TAG (String) - The specific security announcement tag (ie SUSE-SU-2012:0000-0)
				PACKAGES (Dictionary) - A dictionary of package names for keys and their fixed version number for values
	Returns:	True if at least one from PACKAGES was installed, False if no PACKAGES were installed
	Example:

	LTSS = False
	NAME = 'Firefox'
	MAIN = 'MozillaFirefox'
	SEVERITY = 'Important'
	TAG = 'SUSE-SU-2012:0000-0'
	PACKAGES = {}
	SERVER = SUSE.getHostInfo()

	if ( SERVER['DistroVersion'] == 11 and SERVER['DistroPatchLevel'] == 3 ):
		PACKAGES = {
			'libfreebl3': '3.16.1-0.8.1',
			'MozillaFirefox': '24.6.0esr-0.8.1',
			'MozillaFirefox-translations': '24.6.0esr-0.8.1',
			'mozilla-nspr': '4.10.6-0.3.1',
			'mozilla-nss': '3.16.1-0.8.1',
		}
		SUSE.securityAnnouncementPackageCheck(NAME, MAIN, LTSS, SEVERITY, TAG, PACKAGES)
	else:
		Core.updateStatus(Core.ERROR, "ERROR: " + NAME + " Security Announcement: Outside the distribution scope")
	"""
	FAILED = []
	INSTALLED = False
	CHECK_IT = False
	if( 'critical' in SEVERITY.lower() ):
		STATE = Core.CRIT
	else:
		STATE = Core.WARN
	if( LTSS ):
		TITLE = SEVERITY + " LTSS " + NAME
	else:
		TITLE = SEVERITY + " " + NAME

	if ( len(MAIN) > 0 ):
#		print "securityAnnouncementPackageCheck: MAIN initialized: " + str(MAIN)
		if( packageInstalled(MAIN) ):
#			print "securityAnnouncementPackageCheck: MAIN installed"
			CHECK_IT = True
#		else:
#			print "securityAnnouncementPackageCheck: MAIN not installed"
	else:
		CHECK_IT = True

	if ( CHECK_IT ):
		for I in PACKAGES:
			RPM_NAME = str(I)
			RPM_VERSION = str(PACKAGES[I])
			if packageInstalled(RPM_NAME):
#				print "securityAnnouncementPackageCheck: +Checking: " + RPM_NAME
				INSTALLED = True
				if( compareRPM(RPM_NAME, RPM_VERSION) < 0 ):
#					print "securityAnnouncementPackageCheck:  OUTDATED"
					FAILED.append(RPM_NAME + "-" + RPM_VERSION)
#				else:
#					print "securityAnnouncementPackageCheck:  Current"
#			else:
#				print "securityAnnouncementPackageCheck: -Missing:  " + str(RPM_NAME)
		if( INSTALLED ):
			if( len(FAILED) > 0 ):
				Core.updateStatus(STATE, TITLE + " Security Announcement " + str(TAG) + ", update system to apply: " + " ".join(FAILED))
			else:
				Core.updateStatus(Core.IGNORE, TITLE + " Security Announcement " + str(TAG) + " AVOIDED")
		else:
			Core.updateStatus(Core.ERROR, "ERROR: No " + TITLE + " affected packages installed, skipping security test")
	else:
		Core.updateStatus(Core.ERROR, "ERROR: " + TITLE + " not installed, skipping security test")

	return INSTALLED

def getSCRunTime():
	"""
	Gets information about when the supportconfig was run

	Requires: import datetime
	Args:			None
	Returns:	datetime object

	Example:

	import datetime
	SC_RUN_TIME = SUSE.getSCRunTime()
	if( SC_RUN_TIME < datetime.datetime.now() - datetime.timedelta(days=30) ):
		Core.updateStatus(Core.WARN, "Supportconfig data are older than 30 days, run a new supportconfig")
	else:
		Core.updateStatus(Core.IGNORE, "Supportconfig data are current")	
	"""
	#requires: import datetime
	fileOpen = "basic-environment.txt"
	section = "/date"
	content = {}
	EVENT = None
	if Core.getSection(fileOpen, section, content):
		for line in content:
			if( len(content[line]) > 0 ):
				#print "PROCESS = " + str(content[line])
				PART = content[line].split()
				del PART[4]
				PARTS = ' '.join(PART)
				#print "PARTS = " + str(PARTS) + "\n"
				EVENT = datetime.datetime.strptime(PARTS, "%c")
				#print "EVENT   = " + str(EVENT)
				break
	return EVENT				

def getSCCInfo():
	"""
	Gets information provided by the SUSEConnect --status command in SLE12

	Requires: None
	Args:			None
	Returns:	List of Dictionaries
	Keys:			The dictionary key names correspond to the field names from SUSEConnect command. The dictionaries are variable in length.

	Example:

	SCC_INFO = SUSE.getSCCInfo()
	UNREGISTERED_LIST = []
	if( SCC_INFO ):
		for I in range(len(SCC_INFO)):
			if( "registered" != str(SCC_INFO[I]['status'].lower()) ):
				UNREGISTERED_LIST.append(SCC_INFO[I]['identifier'])
		if( UNREGISTERED_LIST ):
			Core.updateStatus(Core.WARN, "Detected unregistered products: " + str(UNREGISTERED_LIST))
		else:
			Core.updateStatus(Core.IGNORE, "All products appear to be registered")
	else:
		Core.updateStatus(Core.ERROR, "ERROR: Missing SUSEConnect Information")
	"""
	fileOpen = "updates.txt"
	section = "SUSEConnect --status"
	content = {}
	INFO = []
	if Core.getSection(fileOpen, section, content):
		for line in content:
			if "identifier" in content[line].lower():
				#SUSEConnect --status generates output that looks like a python list of dictionaries, eval is used to convert it to just that: a list of dictionaries.
				#Since the source is not trusted, literal_eval is used to secure the evaluation.
				INFO = ast.literal_eval(content[line].replace(':null,', ':"",').replace(':null}', ':""}'))
	#for I in range(len(INFO)):
		#print "INFO[" + str(I) + "]: " + str(INFO[I])
	#print "\n"
	return INFO

def getZypperRepoList():
	"""
	Gathers zypper repos output into a list of dictionaries

	Args:			None
	Returns:	List of Dictionaries
	Keys:			The dictionary key names correspond to the field names from zypper repos command.
						Num - Repository number
						Alias
						Name
						Enabled - True (Yes) if the repository is enabled, otherwise False (No).
						Refresh - True (Yes) is the repository is set to refresh, otherwise False (No).

	Example:

	REPO_LIST = SUSE.getZypperRepoList()
	DISABLED_REPOS = []
	for I in range(len(REPO_LIST)):
		if( not REPO_LIST[I]['Enabled'] ):
			DISABLED_REPOS.append(REPO_LIST[I]['Name'])
	if( DISABLED_REPOS ):
		Core.updateStatus(Core.WARN, "Detected " + str(len(DISABLED_REPOS)) + " disabled repositories of " + str(len(REPO_LIST)) + " available: " + str(DISABLED_REPOS))
	else:
		Core.updateStatus(Core.IGNORE, "Not disabled repositories detected")	
	"""
	fileOpen = "updates.txt"
	section = r'/zypper\s--.*\srepos'
	startRepos = re.compile(r"^-*\+-*\+")
	endRepos = re.compile(r"^#==|^$")
	REPOS = []
	IN_REPOS = False
	content = {}
	if Core.getSection(fileOpen, section, content):
		for line in content:
			if( IN_REPOS ):
				if endRepos.search(content[line]):
					IN_REPOS = False
				else:
					ONE_REPO = content[line].split('|')
					for I in range(len(ONE_REPO)):
						ONE_REPO[I] = ONE_REPO[I].strip()
					#Converts ONE_REPO into a dictionary with the named keys
					ONE_DICT = dict(list(zip(['Num', 'Alias', 'Name', 'Enabled', 'Refresh'], ONE_REPO)))
					REPOS.append(ONE_DICT)
			elif startRepos.search(content[line]):
				IN_REPOS = True
	for I in range(len(REPOS)):
		if 'yes' in REPOS[I]['Enabled'].lower():
			REPOS[I]['Enabled'] = True
		else:
			REPOS[I]['Enabled'] = False
		if 'yes' in REPOS[I]['Refresh'].lower():
			REPOS[I]['Refresh'] = True
		else:
			REPOS[I]['Refresh'] = False
		#print REPOS[I]
	#print "\n"
	return REPOS

def getZypperProductList():
	"""
	Gathers zypper products output into a list of dictionaries

	Args:			None
	Returns:	List of Dictionaries
	Keys:			The dictionary key names correspond to the field names from zypper products command.
						Status (S) - Product status
						Repository
						InternalName
						Name
						Version
						Architecture (Arch)
						IsBase - True (Yes) is the product is a base product, otherwise False (No).

	Example:

	PRODUCT_LIST = SUSE.getZypperProductList()
	BASE_PRODUCTS = []
	for I in range(len(PRODUCT_LIST)):
		if( PRODUCT_LIST[I]['IsBase'] ):
			BASE_PRODUCTS.append(PRODUCT_LIST[I]['Name'])
	if( BASE_PRODUCTS ):
		Core.updateStatus(Core.SUCC, "Base products found: " + str(BASE_PRODUCTS))
	else:
		Core.updateStatus(Core.CRIT, "No base products found")	
	"""
	fileOpen = "updates.txt"
	section = r'/zypper\s--.*\sproducts'
	startProducts = re.compile(r"^-*\+-*\+")
	endProducts = re.compile(r"^#==|^$")
	PRODUCTS = []
	IN_PRODUCTS = False
	content = {}
	if Core.getSection(fileOpen, section, content):
		for line in content:
			if( IN_PRODUCTS ):
				if endProducts.search(content[line]):
					IN_PRODUCTS = False
				else:
					ONE_PRODUCT = content[line].split('|')
					for I in range(len(ONE_PRODUCT)):
						ONE_PRODUCT[I] = ONE_PRODUCT[I].strip()
					#Converts ONE_PRODUCT into a dictionary with the named keys
					ONE_DICT = dict(list(zip(['Status', 'Respository', 'InternalName', 'Name', 'Version', 'Architecture', 'IsBase'], ONE_PRODUCT)))
					PRODUCTS.append(ONE_DICT)
			elif startProducts.search(content[line]):
				IN_PRODUCTS = True
	for I in range(len(PRODUCTS)):
		if 'yes' in PRODUCTS[I]['IsBase'].lower():
			PRODUCTS[I]['IsBase'] = True
		else:
			PRODUCTS[I]['IsBase'] = False
		#print PRODUCTS[I]
	#print "\n"
	return PRODUCTS

def getBasicVirtualization():
	"""
	Gathers Virtualization section of the basic-environment.txt file.

	Args:			None
	Returns:	Dictionary

	Converts the basic-environment.txt section from this:

	#==[ System ]=======================================#
	# Virtualization
	Manufacturer:  HP
	Hardware:      ProLiant DL380 Gen9
	Hypervisor:    None
	Identity:      Not Detected

	to this dictionary:

  {'Hardware': 'ProLiant DL380 Gen9', 'Hypervisor': 'None', 'Identity': 'Not Detected', 'Manufacturer': 'HP'} 

	Example:
	SYSTEM = SUSE.getBasicVirtualization()
	if "hp" in SYSTEM['Manufacturer'].lower():
		Core.updateStatus(Core.WARN, "Detected HP hardware")
	else:
		Core.updateStatus(Core.IGNORE, "No HP hardware found")	
	"""
	FILE_OPEN = "basic-environment.txt"
	SECTION = "Virtualization"
	CONTENT = []
	DICTIONARY = {}
	if Core.getRegExSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if ":" in LINE:
				TMP = LINE.split(":", 1)
				DICTIONARY[TMP[0]] = TMP[1].strip()

#	print "DICTIONARY", DICTIONARY
	return DICTIONARY

def getProcCmdLine():
	"""
	Gathers the /proc/cmdline and assigns each value to a list element.

	Args:			None
	Returns:	List
	Example:

	CMDLINE = SUSE.getProcCmdLine()
	CRASH_DEFINED = False
	for OPTION in CMDLINE:
		if "crashkernel=" in OPTION:
			CRASH_DEFINED = True
	if( CRASH_DEFINED ):
		Core.updateStatus(Core.IGNORE, "Kernel crash memory is defined")
	else:
		Core.updateStatus(Core.REC, "Consider configuring the server for a kernel core dump")
	"""
	FILE_OPEN = "boot.txt"
	SECTION = "/proc/cmdline"
	CONTENT = []
	LIST = []
	if Core.getRegExSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			LIST = LINE.split()
	return LIST

def getFileSystems():
	"""
	Gets all fields from the mounted and unmountd file systems with their associated fstab file and df command output.

	Args:			None
	Returns:	List of Dictionaries
	Keys:
		ActiveDevice  = The active device path
		MountedDevice = The device path from the mount command
		FstabDevice   = The device path from /etc/fstab
		MountPoint    = The mount point
		Type          = File system type
		MountOptions  = Options used when mounted as shown by the mount command
		FstabOptions  = Options defined in the /etc/fstab
		Dump          = /etc/fstab dump field, '' if unknown
		fsck          = /etc/fstab fsck field, '' if unknown
		Mounted       = False = Not mounted, True = Mounted
		Size          = File system size in bytes, '' if unknown
		UsedSpace     = File system space used in bytes, '' if unknown
		AvailSpace    = file system space available in bytes, '' if unknown
		PercentUsed   = file system percent used, -1 if unknown

	Example:
	UNMOUNTED = []
	FSLIST = SUSE.getFileSystems()
	for FS in FSLIST:
		if( not FS['Mounted'] ):
			UNMOUNTED.append(FS['MountPoint'])
	if( UNMOUNTED ):
		Core.updateStatus(Core.WARN, "Detected unmounted filesystems: " + ' '.join(UNMOUNTED))
	else:
		Core.updateStatus(Core.IGNORE, "All filesystems appear to be mounted")
	"""
	MOUNTS = []
	FSTAB = []
	DFDATA = []
	DFDATA_NORMALIZED = []
	FSLIST = []
	ENTRY = []
	if( Core.getRegExSection('fs-diskio.txt', '/bin/mount', MOUNTS) and Core.getRegExSection('fs-diskio.txt', '/etc/fstab', FSTAB) and Core.getRegExSection('basic-health-check.txt', 'df -h', DFDATA) ):
		#normalize df data for later use
		LINE_WRAPPED = False
		THIS_ENTRY = []
		for DFLINE in DFDATA:
			LINE = DFLINE.strip().split()
			if "Filesystem" in LINE[0]:
				continue
			else:
				LENLINE = len(LINE)
				if( LENLINE == 6 ):
					DFDATA_NORMALIZED.append(LINE)
				elif( LENLINE == 1 ): # Line wraps because the first field is a very long device name
					THIS_ENTRY = LINE
				elif( LENLINE < 6 ): # Adds the rest of the fields to the device from the first line
					THIS_ENTRY.extend(LINE)
					if( len(THIS_ENTRY) == 6 ):
						DFDATA_NORMALIZED.append(THIS_ENTRY)
					THIS_ENTRY = []
			for DFLIST in DFDATA_NORMALIZED:
				TMP = DFLIST[4].replace('%', '')
				DFLIST[4] = TMP

		#compile mounted filesystem data with merged fstab and df data
		for MOUNT in MOUNTS: #load each mount line output into the ENTRY list
			MOUNT = MOUNT.replace("(", '').replace(")", '')
			ENTRY = MOUNT.split()
			if( len(ENTRY) != 6 ): #ignore non-standard mount entries. They should only have six fields.
				ENTRY = []
				continue
#			print "ENTRY mount", ENTRY

			#add fstab entries to mounted filesystems
			MATCHED = False
			for FSENTRY in FSTAB: #check each FSENTRY to the current MOUNT
				THIS_ENTRY = FSENTRY.split()
				if( len(THIS_ENTRY) != 6 ): #consider non-standard entries as not MATCHED
					break
				if( THIS_ENTRY[1] == ENTRY[2] ): #mount points match
					MATCHED = True
					ENTRY.append(THIS_ENTRY[0]) #fstab device
					ENTRY.append(THIS_ENTRY[3]) #fstab options
					ENTRY.append(int(THIS_ENTRY[4])) #dump
					ENTRY.append(int(THIS_ENTRY[5])) #fsck
					break
			if( not MATCHED ): #mounted, but not defined in /etc/fstab
				ENTRY.append('') #no fstab device
				ENTRY.append('') #fstab options
				ENTRY.append(-1) #dump
				ENTRY.append(-1) #fsck
#			print "ENTRY mount+fstab", ENTRY

			#add df info to mounted filesystems
			MATCHED = False
			for DF in DFDATA_NORMALIZED: #check each DF entry to the current MOUNT
				if( DF[5] == ENTRY[2] ): #mount points match
					MATCHED = True
					ENTRY.append(DF[1]) #size
					ENTRY.append(DF[2]) #used
					ENTRY.append(DF[3]) #available
					ENTRY.append(DF[4]) #percent used
			if( not MATCHED ): #DF doesn't match MOUNT, so use undefined values
				ENTRY.append('') #size
				ENTRY.append('') #used
				ENTRY.append('') #available
				ENTRY.append(-1) #percent used
			MATCHED = False
#			print "ENTRY mount+fstab+df", len(ENTRY), ":", ENTRY
			if( len(ENTRY) == 14 ): #add valid filesystems to the returnable list
				FSLIST.append({'ActiveDevice': ENTRY[0], 'MountedDevice': ENTRY[0], 'FstabDevice': ENTRY[6], 'MountPoint': ENTRY[2], 'Type': ENTRY[4], 'MountOptions': ENTRY[5], 'FstabOptions': ENTRY[7], 'Dump': ENTRY[8], 'fsck': ENTRY[9], 'Mounted': True, 'Size': ENTRY[10], 'UsedSpace': ENTRY[11], 'AvailSpace': ENTRY[12], 'PercentUsed': int(ENTRY[13]) })

		#now add any unmounted filesystems
		UNMOUNTED = []
		ENTRY = []
		SWAP = []
		for FSENTRY in FSTAB: #check each FSENTRY for unmounted devices
			ENTRY = FSENTRY.split()
			if( len(ENTRY) != 6 ): #consider non-standard entries as not MATCHED
				continue
			else:
				MISSING = True
				for FS in FSLIST: #check FSENTRY in each mounted FSLIST
					if( ENTRY[1] == FS['MountPoint'] ): #FSENTRY must be mounted
						MISSING = False
						break
				if( MISSING ): #the fstab entry was not found in the list of mounted filesystems
					if( ENTRY[1].lower() == "swap" ): # If there is more than one swap device, the same free -k swap information is used for each one.
						if( Core.getRegExSection('memory.txt', 'free -k', SWAP) ):
							for LINE in SWAP: #swap sizes are in the memory.txt file, not df command
								if LINE.startswith("Swap:"):
									TMP = LINE.split()
									break
#							print "SWAP", TMP
							PCTSWAP = (int(TMP[2]) * 100 / int(TMP[1]))
							if( int(TMP[1]) > 0 ): #if the swap size is greater than 0 assume all swap devices are mounted
								UNMOUNTED.append({'ActiveDevice': ENTRY[0], 'MountedDevice': '', 'FstabDevice': ENTRY[0], 'MountPoint': ENTRY[1], 'Type': ENTRY[2], 'MountOptions': '', 'FstabOptions': ENTRY[3], 'Dump': ENTRY[4], 'fsck': ENTRY[5], 'Mounted': True, 'Size': TMP[1], 'UsedSpace': TMP[2], 'AvailSpace': TMP[3], 'PercentUsed': PCTSWAP })
							else: #the swap size is zero, assume all swap devices are not mounted
								UNMOUNTED.append({'ActiveDevice': ENTRY[0], 'MountedDevice': '', 'FstabDevice': ENTRY[0], 'MountPoint': ENTRY[1], 'Type': ENTRY[2], 'MountOptions': '', 'FstabOptions': ENTRY[3], 'Dump': ENTRY[4], 'fsck': ENTRY[5], 'Mounted': False, 'Size': TMP[1], 'UsedSpace': TMP[2], 'AvailSpace': TMP[3], 'PercentUsed': PCTSWAP })
						else: #swap size information is not found
							UNMOUNTED.append({'ActiveDevice': ENTRY[0], 'MountedDevice': '', 'FstabDevice': ENTRY[0], 'MountPoint': ENTRY[1], 'Type': ENTRY[2], 'MountOptions': '', 'FstabOptions': ENTRY[3], 'Dump': ENTRY[4], 'fsck': ENTRY[5], 'Mounted': False, 'Size': '', 'UsedSpace': '', 'AvailSpace': '', 'PercentUsed': -1 })
					else: #not a swap device
						UNMOUNTED.append({'ActiveDevice': ENTRY[0], 'MountedDevice': '', 'FstabDevice': ENTRY[0], 'MountPoint': ENTRY[1], 'Type': ENTRY[2], 'MountOptions': '', 'FstabOptions': ENTRY[3], 'Dump': ENTRY[4], 'fsck': ENTRY[5], 'Mounted': False, 'Size': '', 'UsedSpace': '', 'AvailSpace': '', 'PercentUsed': -1 })
		if( UNMOUNTED ):
			FSLIST.extend(UNMOUNTED)
	else:
		Core.updateStatus(Core.ERROR, "ERROR: getFileSystems: Cannot find /bin/mount(fs-diskio.txt), /etc/fstab(fs-diskio.txt), df -h(basic-health-check.txt) sections")

#	for FS in FSLIST:
#		print "{0:20}: {1}\n".format(FS['MountPoint'], FS)
#	print "TOTAL", len(FSLIST)
	del MOUNTS
	del FSTAB
	del DFDATA
	del DFDATA_NORMALIZED
	del SWAP
	return FSLIST

def getGrub2Config():
	"""
	Returns a dictionary of the key/value pairs found in /etc/default/grub.
	Supportconfigs from SLE12 minimum required

	Args:			None
	Returns:	Dictionary
	Keys:			As defined in /etc/default/grub. All keys are forced to uppercase, values are left as is.

	Example:

	CONFIG = SUSE.getGrub2Config()
	if( "splash=silent" in CONFIG['GRUB_CMDLINE_LINUX_DEFAULT'].lower() ):
		Core.updateStatus(Core.REC, "Use splash=native for more screen output")
	else:
		Core.updateStatus(Core.IGNORE, "Additional screen output ignored")
	"""
	CONFIG = []
	VALUES = {}
	if( Core.getRegExSection('boot.txt', '/etc/default/grub', CONFIG) ):
		for LINE in CONFIG:
			TMP = LINE.split("=", 1)
			VALUES[TMP[0].upper()] = TMP[1].strip('"').strip()
#	print VALUES
	return VALUES

def getBasicFIPSData():
	"""
	Returns a dictionary of state of key FIPS data values.
	Supportconfigs from SLE12 minimum required

	Args:			None
	Returns:	Dictionary
	Keys:
		Installed = FIPS packages are installed
		Enabled   = FIPS is enabled per /proc/sys/crypto/fips_enabled
		GrubFips  = fips=1 found in /etc/default/grub for GRUB2
		GrubBoot  = boot= found in /etc/default/grub for GRUB2
		KernFips  = fips=1 found in /proc/cmdline
		KernBoot  = boot= found in /proc/cmdline
		Initrd    = fips module included in the ramdisk of the running kernel
								Note: This key is present only if the supportconfig has the lsinitrd output in boot.txt

	Example:

	FIPS = SUSE.getBasicFIPSData()
	if( FIPS['Installed'] ):
		Core.updateStatus(Core.IGNORE, "FIPS installed")
	else:		
		Core.updateStatus(Core.REC, "Consider installing FIPS")
	"""
	FIPS = {'Installed': False, 'Enabled': False, 'GrubFips': False, 'GrubBoot': False, 'KernFips': False, 'KernBoot': False}
	
	if( packageInstalled('dracut-fips') ):
		FIPS['Installed'] = True

	CONTENT = []
	if Core.getRegExSection('proc.txt', '/proc/sys/crypto/fips_enabled', CONTENT):
		for LINE in CONTENT:
			if( LINE.isdigit() ):
				if( int(LINE) > 0 ):
					FIPS['Enabled'] = True

	GRUB2 = getGrub2Config()
	if( 'GRUB_CMDLINE_LINUX_DEFAULT' in list(GRUB2.keys()) ):
		if( "fips=1" in GRUB2['GRUB_CMDLINE_LINUX_DEFAULT'].lower() ):
			FIPS['GrubFips'] = True
		if( "boot=" in GRUB2['GRUB_CMDLINE_LINUX_DEFAULT'].lower() ):
			FIPS['GrubBoot'] = True

	if( 'GRUB_CMDLINE_LINUX' in list(GRUB2.keys()) ):
		if( "fips=1" in GRUB2['GRUB_CMDLINE_LINUX'].lower() ):
			FIPS['GrubFips'] = True
		if( "boot=" in GRUB2['GRUB_CMDLINE_LINUX'].lower() ):
			FIPS['GrubBoot'] = True

	CMDLINE = getProcCmdLine()
	for OPTION in CMDLINE:
		TEST = OPTION.lower()
		if "fips=1" in TEST:
			FIPS['KernFips'] = True
		elif "boot=" in TEST:
			FIPS['KernBoot'] = True

	if Core.getRegExSection('boot.txt', '/bin/lsinitrd', CONTENT):
		FOUND = False
		MODS = False
		for LINE in CONTENT:
			TEST = LINE.lower()
			if( MODS ):
				if TEST.startswith("=="):
					MODS = False
					break
				elif TEST.startswith("fips"):
					FOUND = True
					break
			elif TEST.startswith("dracut modules:"):
				MODS = True
		if( FOUND ):
			FIPS['Initrd'] = True
		else:
			FIPS['Initrd'] = False

#	print "FIPS", FIPS
	return FIPS

def getConfigFileLVM(PART):
	"""
	Returns a dictionary of the /etc/lvm/lvm.conf file from the lvm.txt file in supportconfig.

	Args:			PART
		If PART is set to '' or 'all', the entire lvm.conf file will be returned in a dictionary of dictionaries.
		If PART is set to a specific lvm.conf section, like 'log' or 'activation', only that section will be returned as a dictionary.
		If PART is set, but not found among the lvm.conf sections, an empty dictionary is returned.
	Returns:	Dictionary
	Keys:			Returned from the lvm.conf itself

	Example 1:
	LVM_CONFIG = SUSE.getConfigFileLVM('log')
	if( int(LVM_CONFIG['verbose']) > 0 ):
		Core.updateStatus(Core.WARN, "LVM logging set to greater verbosity")
	else:		
		Core.updateStatus(Core.IGNORE, "LMV logging is not verbose")

	Example 2:
	LVM_CONFIG = SUSE.getConfigFileLVM('ALL')
	if( int(LVM_CONFIG['log']['verbose']) > 0 ):
		Core.updateStatus(Core.WARN, "LVM logging set to greater verbosity")
	else:		
		Core.updateStatus(Core.IGNORE, "LMV logging is not verbose")
	"""
	FILE_OPEN = "lvm.txt"
	SECTION = "lvm.conf"
	CONTENT = []
	LVM_CONFIG = {}
	LVM_CONFIG_ALL = {}
	IN_PART = False
	IN_ARRAY = False
	ARRAY_VALUES = []
	ARRAY_KEY = ''
	LVM_SECTION_NAME = ''
	LVM_SECTION = re.compile(r"^\S*\s*{", re.IGNORECASE)
	SKIP_LINE = re.compile(r"^\s*#|^\s*$", re.IGNORECASE)
	if Core.getRegExSection(FILE_OPEN, SECTION, CONTENT):
		for LINE in CONTENT:
			if SKIP_LINE.search(LINE):
				continue
			THIS = LINE.strip().lower()
			if( IN_PART ):
				if "}" in THIS: #end of lvm config file part
#					print " Leaving: '" + LVM_SECTION_NAME + "'"
					IN_PART = False
					LVM_CONFIG_ALL[LVM_SECTION_NAME] = LVM_CONFIG
					LVM_CONFIG = {}
					LVM_SECTION_NAME = ''
				else:
					TMP = THIS.split("=", 1)
					if( len(TMP) > 1 ):
						KEY = TMP[0].strip()
						VALUE = TMP[1].strip()
					else:
						KEY = ''
						VALUE = TMP[0].strip()

					if( IN_ARRAY ):
						if( "]" in THIS ):
#							print " End array:", TMP[0], "Length", len(THIS)
							IN_ARRAY = False
							TMP2 = VALUE.strip("[ ] ").split(",")
							for VALUE in TMP2:
								ARRAY_VALUES.append(VALUE.strip('" \' '))
							ARRAY_VALUES = [_f for _f in ARRAY_VALUES if _f]
							LVM_CONFIG[ARRAY_KEY.strip()] = sorted(ARRAY_VALUES)
						else:
#							print "  Add to array:", TMP[0], "Length", len(THIS)
							TMP2 = THIS.strip("[ ] ").split(",")
							for VALUE in TMP2:
								ARRAY_VALUES.append(VALUE.strip('" \' '))
					elif( "[" in THIS and "]" in THIS ):
#						print " Complete array:", TMP[0], TMP[1]
						TMP2 = TMP[1].strip("[ ] ").split(",")
						VALUES = []
						for VALUE in TMP2:
							VALUES.append(VALUE.strip('" \' '))
						LVM_CONFIG[TMP[0].strip()] = VALUES
					elif( "[" in THIS ):
#						print " Start array:", TMP[0], TMP[1]
						IN_ARRAY = True
						ARRAY_KEY = TMP[0]
						ARRAY_VALUES = []
						TMP2 = TMP[1].strip("[ ] ").split(",")
						for VALUE in TMP2:
							ARRAY_VALUES.append(VALUE.strip('" \' '))
					else:
#						print " Normal:", TMP[0], TMP[1].strip('" \' ')
						LVM_CONFIG[TMP[0].strip()] = TMP[1].strip('" \' ')
			elif LVM_SECTION.search(THIS):
				LVM_SECTION_NAME = THIS.strip().split()[0].strip()
				IN_PART = True
#				print "Entering LVM Section: '" + LVM_SECTION_NAME + "'"

#		print
#		print "KEYS", LVM_CONFIG_ALL.keys()
#		print
		if( len(PART) > 0 ):
			if( PART.lower() == "all" ):
				LVM_CONFIG = LVM_CONFIG_ALL
#				print 'ALL:', LVM_CONFIG
			elif PART in list(LVM_CONFIG_ALL.keys()):
				LVM_CONFIG = LVM_CONFIG_ALL[PART]
#				print PART + ":", LVM_CONFIG
			else:
				LVM_CONFIG = {}
#				print "KEY_NOT_FOUND:", PART
		else:
			LVM_CONFIG = LVM_CONFIG_ALL
#			print 'ALL:', LVM_CONFIG
#		print
	return LVM_CONFIG

def getNetworkInterfaces():
	"""
	Merges network interface data from ip addr, eththool -k and /etc/sysconfig/network/ifcfg-* output.

	Args:			None
	Returns:	Dictionary of Dictionaries and Lists as NIC_LIST
	Keys:
		Data example from 'ip addr'
			8: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
			  link/ether 24:6e:96:7e:48:f8 brd ff:ff:ff:ff:ff:ff
			  inet 10.9.14.110/23 brd 10.9.15.255 scope global br0
			    valid_lft forever preferred_lft forever
			  inet6 fdc8:123f:e31f:14:5ccb:3994:853a:81e4/64 scope global temporary dynamic 
			    valid_lft 532496sec preferred_lft 13580sec
			  inet6 fdc8:123f:e31f:14:6572:bcd9:387:b215/64 scope global temporary deprecated dynamic 
			    valid_lft 446615sec preferred_lft 0sec

			Each interface is the key to the dictionary and lists associated with that interface (ie br0)
			Active interface flags are set to true if defined with the name as the key per netdevice(7) [ie {'BROADCAST': True, 'MULTICAST': True, 'UP': True, 'LOWER_UP': True, ...}]
			The mtu and state are extracted from the interface line as well, (ie {'mtu': 1500, 'state': 'UNKNOWN'}), If the mtu or state are missing the value is "?".
			The mac address is extracted from the link line (ie {'mac': '24:6e:96:7e:48:f8'})
			Since there can be more than one internet address per network interface, they are stored in a list with the keys addr4 and addr6
				(ie {'addr4': ['10.9.14.110/23'], 'addr6': ['fdc8:123f:e31f:14:5ccb:3994:853a:81e4/64', 'fdc8:123f:e31f:14:6572:bcd9:387:b215/64', ...]})

		Data example from 'ethtool -k br0'
			Features for br0: # This line is skipped
			rx-checksumming: off [fixed]
			tx-checksumming: on
				tx-checksum-ipv4: off [fixed]
				tx-checksum-ip-generic: on
			...
			scatter-gather: on
			...

			Each key/value pair from 'ethtool -k <interface>' is assigned as well.
				(ie {'rx-checksumming': False, 'tx-checksumming': True, 'tx-checksum-ipv4': False, 'tx-checksum-ip-generic': True, 'scatter-gather': True, ...}

		Data example from /etc/sysconfig/network/ifcfg-br0
			STARTMODE='auto'
			BOOTPROTO='dhcp'
			OVS_BRIDGE='yes'
			OVS_BRIDGE_PORT_DEVICE_1='bond0'
			POST_UP_SCRIPT='wicked:/etc/sysconfig/network/scripts/ifup-br0'

		Each key/value pair in the network configuration file is added to the device dictionary.
			(ie {'STARTMODE': 'auto', 'BOOTPROTO': 'dhcp', 'OVS_BRIDGE': 'yes', "OVS_BRIDGE_PORT_DEVICE_1': 'bond0', 'POST_UP_SCRIPT": 'wicked:/etc/sysconfig/network/scripts/ifup-br0'})

	Example:

	NETWORKS = SUSE.getNetworkInterfaces()
	MISSING_SG = []
	FEATURE = 'scatter-gather'

	for DEVICE in NETWORKS.keys():
		if( FEATURE in NETWORKS[DEVICE] ):
			if( not NETWORKS[DEVICE][FEATURE] ):
				MISSING_SG.append(DEVICE)
	if( len(MISSING_SG) > 0 ):
		Core.updateStatus(Core.WARN, "Network devices with " + str(FEATURE) + " disabled: " + ' '.join(MISSING_SG))
	else:
		Core.updateStatus(Core.IGNORE, "All network devices have " + str(FEATURE) + " enabled")

	"""
	NETWORK_FILE = 'network.txt'
	IPADDR = []
	IPROUTE = []
	NIC_LIST = {}
	DEV = ''

	if( Core.isFileActive(NETWORK_FILE) ):
		STARTNIC = re.compile(r"\d:.*: <.*>.* mtu ")
		if( Core.getRegExSection(NETWORK_FILE, '/ip addr', IPADDR) ):
			for LINE in IPADDR:
				if STARTNIC.search(LINE):
#					print("Processing: " + str(LINE))
					# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master br0 state UP group default qlen 1000
					LINE_PARTS = LINE.split()
					DEV = LINE_PARTS[1][:-1]
					NIC_LIST[DEV] = {}
					NIC_LIST[DEV]['addr4'] = [] # holds all IPv4 internet addresses
					NIC_LIST[DEV]['addr6'] = [] # holds all IPv6 internet addresses
					NIC_LIST[DEV]['mtu'] = '?'
					NIC_LIST[DEV]['state'] = '?'
					for i in range(len(LINE_PARTS)):
						if( LINE_PARTS[i] == "mtu" ):
							NIC_LIST[DEV]['mtu'] = LINE_PARTS[i+1]
						elif( LINE_PARTS[i] == "state" ):
							NIC_LIST[DEV]['state'] = LINE_PARTS[i+1]
					FLAGS = LINE_PARTS[2][1:][:-1].upper().split(',')
					for FLAG in FLAGS:
						NIC_LIST[DEV][FLAG] = True
				elif( LINE.strip().startswith("link") ):
					# link/ether 00:25:b5:05:03:7e brd ff:ff:ff:ff:ff:ff
					NIC_LIST[DEV]['mac'] = LINE.split()[1]
				elif( LINE.strip().startswith("inet ") ):
					# inet 192.168.0.236/24 brd 192.168.0.255 scope global eth0
					NIC_LIST[DEV]['addr4'].append(LINE.split()[1])
				elif( LINE.strip().startswith("inet6 ") ):
					# inet6 fe80::5054:ff:fea4:12da/64 scope link
					NIC_LIST[DEV]['addr6'].append(LINE.split()[1])
		for DEV in list(NIC_LIST.keys()):
			ETHTOOL = []
			NETCONFIG = []
			if( Core.getRegExSection(NETWORK_FILE, "ethtool -k " + str(DEV), ETHTOOL) ):
				for LINE in ETHTOOL[1:]:
					ETHTOOL_PARTS = LINE.split()
					OPTION = ETHTOOL_PARTS[0][:-1]
					if( ETHTOOL_PARTS[1].lower() == "on" ):
						NIC_LIST[DEV][OPTION] = True
					else:
						NIC_LIST[DEV][OPTION] = False
			if( Core.getRegExSection(NETWORK_FILE, "/etc/sysconfig/network/ifcfg-" + str(DEV), NETCONFIG) ):
				for LINE in NETCONFIG:
					(KEY, VALUE) = LINE.split('=', 1)
					NIC_LIST[DEV][KEY] = VALUE[1:][:-1]

#	for NIC in NIC_LIST.keys():
#		print("\n" + str(NIC) + " : " + str(NIC_LIST[NIC]))
#	print

	return NIC_LIST

