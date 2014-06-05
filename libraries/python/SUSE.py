"""
Supportconfig Analysis Library for SUSE python patterns

Library of functions for creating python patterns specific to SUSE
"""
##############################################################################
#  Copyright (C) 2013,2014 SUSE LLC
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
#    David Hamner (dhamner@novell.com)
#    Jason Record (jrecord@suse.com)
#
#  Modified: 2014 Feb 21
#
##############################################################################

import sys, re, Core, string

global path
SLE9GA       = '2.6.5-7.97'
SLE9SP1      = '2.6.5-7.139'
SLE9SP2      = '2.6.5-7.191'
SLE9SP3      = '2.6.5-7.244'
SLE9SP4      = '2.6.5-7.308'
SLE9SP5      = '2.6.5-8' #Update when/if actual version ships
SLE10GA      = '2.6.16.21-0.8'
SLE10SP1     = '2.6.16.46-0.12'
SLE10SP2     = '2.6.16.60-0.21'
SLE10SP3     = '2.6.16.60-0.54.5'
SLE10SP4     = '2.6.16.60-0.85.1'
SLE10SP5     = '2.6.17' #Update to actual version when/if ready
SLE11GA      = '2.6.27.19-5'
SLE11SP1     = '2.6.32.12-0.7'
SLE11SP2     = '3.0.13-0.27'
SLE11SP3     = '3.0.76-0.11.1'
SLE11SP4     = '3.1' #Update to actual version when/if ready
SLE12GA      = '3.999' #Update to actual version when applicable

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
	if len(rpmInfo) > 0:
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
	section = "{NAME}"
	content = {}
	tmpContent = {}
	#get name version and vendor
	if (Core.getSection(fileOpen, section, content)):
		for line in content:
			if content[line].startswith(PackageName + " "):
				tmpContent = re.sub(' +', ' ', content[line])
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

def packageVerify(FILE_OPEN, PKG_NAME, EXCEPTION_LIST):
	return True

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
					RunLevelStatus (Integer) - 0=Service is turned off for the current runlevel, 1=Service is turned on for the current runlevel
	Example:

	SERVICE = 'cups'
	SERVICE_INFO = SUSE.getServiceInfo(SERVICE)
	if( SERVICE_INFO['Running'] > 0 ):
		Core.updateStatus(Core.IGNORE, "Service is running: " + str(SERVICE_NAME));
	else:
		Core.updateStatus(Core.WARN, "Service is down: " + str(SERVICE_NAME));
	"""
	SERVICE_TABLE = {
		'novell-afptcpd': 'novell-afp.txt',
		'novell-ncs': 'novell-ncs.txt',
		'auditd': 'security-audit.txt',
		'smt': 'smt.txt',
		'rcd': 'updates-daemon.txt',
		'novell-zmd': 'updates-daemon.txt',
		'novell-nss': 'novell-nss.txt',
		'novell-smdrd': 'novell-sms.txt',
		'novell-afptcpd': 'novell-afp.txt',
		'novell-cifs': 'novell-cifs.txt',
		'novell-ipsmd': 'plugin-iPrint.txt',
		'namcd': 'novell-lum.txt',
		'cron': 'cron.txt',
		'atd': 'cron.txt',
		'multipathd': 'mpio.txt',
		'network': 'network.txt',
		'nscd': 'network.txt',
		'iscsitarget': 'fs-iscsi.txt',
		'open-iscsi': 'fs-iscsi.txt',
		'nfs': 'nfs.txt',
		'nfsserver': 'nfs.txt',
		'portmap': 'nfs.txt',
		'nfslock': 'nfs.txt',
		'xntpd': 'ntp.txt',
		'ntp': 'ntp.txt',
		'kdump': 'crash.txt',
		'autofs': 'fs-autofs.txt',
		'xend': 'xen.txt',
		'boot.subdomain': 'security-apparmor.txt',
		'openais': 'ha.txt',
		'heartbeat': 'ha.txt',
		'slpd': 'slp.txt',
		'o2cb': 'ocfs2.txt',
		'ocfs2': 'ocfs2.txt',
		'smb': 'samba.txt',
		'nmb': 'samba.txt',
		'winbind': 'samba.txt',
		'smartd': 'fs-smartmon.txt',
		'ldap': 'ldap.txt',
		'sshd': 'ssh.txt',
		'slert': 'slert.txt',
		'cset': 'slert.txt',
		'cset.init.d': 'slert.txt',
		'cups': 'print.txt',
		'named': 'dns.txt',
		'novell-named': 'dns.txt',
		'dhcpd': 'dhcp.txt',
		'owcimomd': 'cimom.txt',
		'sfcb': 'cimom.txt',
		'openibd': 'ib.txt',
		'apache2': 'web.txt',
		'novell-httpstkd': 'web.txt',
	}
	SERVICE_INFO = {
		'Name': SERVICE_NAME,
		'Running': -1,
		'BootLevels': '',
		'RunLevel': '',
		'RunLevelStatus': 0,
	}
	if ( SERVICE_TABLE[SERVICE_NAME] ):
		FILE_OPEN = SERVICE_TABLE[SERVICE_NAME]
	else:
		FILE_OPEN = ''

	SECTION = ''
	CONTENT = {}
	LINE_CONTENT = {}
	TMP = ''

	if ( $FILE_OPEN ):
		SERVICE_INFO['Running'] = 0
		SECTION = "/etc/init.d/" + SERVICE_NAME + "status";
		if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
			foreach $_ (@CONTENT) {
				next if ( /^\s*$/ );                   # Skip blank lines
				if ( /running/i ) {
					SDP::Core::printDebug("  getServiceInfo PROCESSING", $_);
					$SERVICE_INFO{'running'} = 1;
				}
			}
		}
	} else {
		$FILE_OPEN = 'basic-health-check.txt';
		$SECTION = '/bin/ps';
		if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
			foreach $_ (@CONTENT) {
				next if ( /^\s*$/ );                   # Skip blank lines
				if ( /$SERVICE_NAME/ ) {
					SDP::Core::printDebug("  getServiceInfo PROCESSING", $_);
					@LINE_CONTENT = split(/\s+/, $_);
					if ( $LINE_CONTENT[9] =~ /$SERVICE_NAME/ ) {
						$SERVICE_INFO{'running'} = 1;
						last;
					}
				}
			}
		}
	}

	$FILE_OPEN = 'boot.txt';
	$SECTION = "boot.msg";
	@CONTENT = ();
	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( /^\s*$/ );                   # Skip blank lines
			if ( /Master Resource Control: runlevel (.) has been reached/i ) {
				SDP::Core::printDebug("  getServiceInfo PROCESSING", $_);
				$SERVICE_INFO{'runlevel'} = $1;
			}
		}
	}

	$FILE_OPEN = 'chkconfig.txt';
	$SECTION = "chkconfig --list";
	@CONTENT = ();
	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( /^\s*$/ );                   # Skip blank lines
			if ( /^$SERVICE_NAME\s/ ) {
				SDP::Core::printDebug("  getServiceInfo CHKCONFIG", $_);
				@LINE_CONTENT = split(/\s+/, $_);
				for $TMP (1..7) {
					SDP::Core::printDebug("  getServiceInfo LINE_CONTENT[$TMP]", "$LINE_CONTENT[$TMP]");
					if ( $LINE_CONTENT[$TMP] =~ /(\d)\:on/i ) {
						SDP::Core::printDebug("  getServiceInfo --bootlevels", "Appending '$1' to '$SERVICE_INFO{'bootlevels'}'");
						$SERVICE_INFO{'bootlevels'} = $SERVICE_INFO{'bootlevels'} . $1;
						$SERVICE_INFO{'runlevelstatus'} = 1 if ( $SERVICE_INFO{'runlevel'} == $1 );
					}
				}
			}
		}
	}

	my ($key, $value);
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		print('%SERVICE_INFO = ');
		while ( ($key, $value) = each(%SERVICE_INFO) ) {
			print("$key => \"$value\"  ");
		}
		print("\n");
	}
	SDP::Core::printDebug("< getServiceInfo", "$SERVICE_INFO{'name'}=$SERVICE_INFO{'running'}");
	return %SERVICE_INFO;

def getServiceHealth(SERVICE_NAME):
	return True

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
			Core.updateStatus(Core.CRIT, "Bug detected in " + RPM_VERSION + ", update server for fixes")
		else:
			Core.updateStatus(Core.IGNORE, "Bug fixes applied for " + RPM_VERSION)
	else:
		Core.updateStatus(Core.ERROR, "ERROR: " + RPM_NAME + " not installed")
	"""
	try:
		#get package version
		packageVersion = getRpmInfo(package)['version']
#		print "compareRPM: Package                  = " + str(package)
#		print "compareRPM: Given version            = " + str(kernelVersion)
#		print "compareRPM: Version in Supportconfig = " + str(foundVersion)

		return Core.compareVersions(packageVersion, versionString)
	except Exception:
		#error out...
		Core.updateStatus(Core.ERROR, "ERROR: Package not found")

def compareKernel(kernelVersion):
	"""
	Checks if kernel version is newer then given version
	Args:		kernelVersion - The kernel version string to compare
	Returns:	-1, 0, 1
					-1	if Installed kernel version older than kernelVerion
					0	if Installed kernel version equals kernelVerion
					1	if Installed kernel version newer than kernelVerion
	Example:

	KERNEL_VERSION = '3.0.93'
	INSTALLED_VERSION = SUSE.compareKernel(KERNEL_VERSION)
	if( INSTALLED_VERSION < 0 ):
		Core.updateStatus(Core.CRIT, "Bug detected in kernel version " + KERNEL_VERSION + " or before, update server for fixes")
	else:
		Core.updateStatus(Core.IGNORE, "Bug fixes applied for " + KERNEL_VERSION)
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


def getScInfo():
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
	global path
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
			supportFile = open(Core.path	+ "basic-environment.txt", 'r')
			supportFile.readline()
			supportFile.readline()
			scInfo['version'] = supportFile.readline().split(':')[-1].strip()
			scInfo['scriptDate'] =	supportFile.readline().split(':')[-1].strip()
	return scInfo

