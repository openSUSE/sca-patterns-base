##############################################################################
#  Copyright (C) 2013 SUSE LINUX Products GmbH
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
#     David Hamner (dhamner@novell.com)
#     Jason Record (jrecord@suse.com)
#     Modified: 2013 Nov 12
#
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

# Function:    packageInstalled
# Description: The PackageName is installed on the server
# Input:       PackageName
# Output:      True or False
# Example:
#
#	PACKAGE_NAME = 'bind'
#	if ( SUSE.packageInstalled(PACKAGE_NAME) ):
#		Core.updateStatus(Core.WARN, "The package " + PACKAGE_NAME + " is installed")
#	else:
#		Core.updateStatus(Core.IGNORE, "The package " + PACKAGE_NAME + " is NOT installed")
#
def packageInstalled(PackageName):
  rpmInfo = getRpmInfo(PackageName)
  if len(rpmInfo) > 0:
    return True
  return False


# Function:    getRpmInfo
# Description: Gets PackageName information
# Requires:    PackageName must be unique
# Input:       PackageName
# Output:      Dictionary of RPM package information
#  Keys:       name, version, vendor, installTime
# Example:
#
#	RPM_NAME = 'kernel-xen'
#	RPM_INFO = SUSE.getRpmInfo(RPM_NAME)
#	if( len(RPM_INFO) > 0 ):
#		Core.updateStatus(STATUS_IGNORE, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is installed")
#	else:
#		Core.updateStatus(STATUS_WARNING, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is missing, install it")
#
def getRpmInfo(PackageName):
  rpmInfo = {}
  fileOpen = "rpm.txt"
  section = "{NAME}"
  content = {}
  tmpContent = {}
  #get name version and vendor
  if (Core.getSection(fileOpen, section, content)):
    for line in content:
      if content[line].startswith(PackageName + " "):
	tmpContent = content[line].split(' ')
	rpmInfo['name'] = tmpContent[0] #name
	rpmInfo['version'] = tmpContent[-1] #version
	tmpContent.pop(0)
	tmpContent.pop()
	rpmInfo['vendor'] = ' '.join(tmpContent).strip() #vendor
	#rpmInfo[1] = tmpContent[1,-2]	    

	#get install time
	section = "rpm -qa --last"
	content = {}
	if (Core.getSection(fileOpen, section, content)):
		for line in content:
			if content[line].startswith(PackageName):
				rpmInfo['installTime'] = content[line].split(' ',1)[1].strip()
	return rpmInfo


# Function:    getDriverInfo
# Description: Gets information about the specified kernel driver
# Requires:    DRIVER_NAME must be unique
# Input:       DRIVER_NAME
# Output:      Dictionary of kernel driver information
#  Keys:       name, loaded, filename, version, license, description, srcversion, supported, vermagic
# Example:
#
#	DRIVER_NAME = 'zapi'
#	DRIVER_INFO = SUSE.getDriverInfo(DRIVER_NAME)
#	if( DRIVER_INFO['loaded'] ):
#		Core.updateStatus(STATUS_IGNORE, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is installed")
#	else:
#		Core.updateStatus(STATUS_WARNING, "Package " + RPM_INFO['name'] + str(RPM_INFO['version']) + " is missing, install it")
#
def getDriverInfo( DRIVER_NAME ):
	FILE_OPEN = "modules.txt"
	SECTION = "modinfo " + DRIVER_NAME
	DRIVER_KEYS_MISSING = [ 'filename', 'version', 'license', 'description', 'srcversion', 'supported', 'vermagic' ]
	DRIVER_DICTIONARY = { 'name': DRIVER_NAME, 'loaded': 1, DRIVER_KEYS_MISSING[0]: '', DRIVER_KEYS_MISSING[1]: '', DRIVER_KEYS_MISSING[2]: '', DRIVER_KEYS_MISSING[3]: '', DRIVER_KEYS_MISSING[4]: '', DRIVER_KEYS_MISSING[5]: 'no', DRIVER_KEYS_MISSING[6]: '' }
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
		DRIVER_DICTIONARY['loaded'] = 0
	return DRIVER_DICTIONARY


# Function:    compareRPM
# Description: Compares the RPM_VERSION to the installed RPM_NAME's version
# Requires:    RPM_NAME must be unique and installed
# Input:       RPM_NAME, RPM_VERSION
# Output:      -1, 0, 1
#  -1 if RPM_NAME older than RPM_VERSION
#   0 if RPM_NAME equals RPM_VERSION
#   1 if RPM_NAME newer than RPM_VERSION
# Example:
#
#	RPM_NAME = 'mypackage'
#	RPM_VERSION = '1.1.0'
#	if( SUSE.packageInstalled(RPM_NAME) ):
#		INSTALLED_VERSION = SUSE.compareRPM(RPM_NAME, RPM_VERSION)
#		if( INSTALLED_VERSION <= 0 ):
#			Core.updateStatus(Core.CRIT, "Bug detected in " + RPM_VERSION + ", update server for fixes")
#		else:
#			Core.updateStatus(Core.IGNORE, "Bug fixes applied for " + RPM_VERSION)
#	else:
#		Core.updateStatus(Core.ERROR, "ERROR: " + RPM_NAME + " not installed")
#
def compareRPM(package, versionString):
  try:
    #get package version
    packageVersion = getRpmInfo(package)['version']
    #print "packageVersion = " + packageVersion + ", versionString = " + versionString
    
    return Core.compareVersions(packageVersion, versionString)
  except Exception:
    #error out...
    Core.updateStatus(Core.ERROR, "ERROR: Package not found")


# Function:    compareKernel
# Description: Checks if kernel version is newer then given version
# Input:       KERNEL_VERSION
# Output:      -1, 0, 1
#  -1 if Installed kernel version older than KERNEL_VERSION
#   0 if Installed kernel version equals KERNEL_VERSION
#   1 if Installed kernel version newer than KERNEL_VERSION
# Example:
#
#	KERNEL_VERSION = '3.0.93'
#	INSTALLED_VERSION = SUSE.compareKernel(KERNEL_VERSION)
#	if( INSTALLED_VERSION < 0 ):
#		Core.updateStatus(Core.CRIT, "Bug detected in kernel version " + KERNEL_VERSION + " or before, update server for fixes")
#	else:
#		Core.updateStatus(Core.IGNORE, "Bug fixes applied for " + KERNEL_VERSION)
#
def compareKernel(kernelVerion):
  foundVerion = ""
  fileOpen = "basic-environment.txt"
  section = "uname -a"
  content = {}
  if (Core.getSection(fileOpen, section, content)):
    for line in content:
      if content[line] != "":
	foundVerion = content[line].split(" ")[2]
  return Core.compareVersions(foundVerion, kernelVerion)


# Function:    getScInfo
# Description: Gets information about the supportconfig archive itself
# Input:       None
# Output:      Dictionary of supportconfig archive information
#  Keys:       envValue, kernelValue, cmdline, config, version, scriptDate
# Example:
#
#	REQUIRED_VERSION = '2.25-173';
#	SC_INFO = SUSE.getSCInfo();
#	if( Core.compareVersions(SC_INFO['version'], REQUIRED_VERSION) >= 0 ):
#		Core.updateStatus(Core.IGNORE, "Supportconfig v" + str(SC_INFO['version']) + " meets minimum requirement")
#	else:
#		Core.updateStatus(Core.WARN, "Supportconfig v" + str(SC_INFO['version']) + " NOT sufficient, " + str(REQUIRED_VERSION) + " or higher needed")
#
def getScInfo():
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


    supportFile = open(Core.path  + "basic-environment.txt", 'r')
    supportFile.readline()
    supportFile.readline()
    scInfo['version'] = supportFile.readline().split(':')[-1].strip()
    scInfo['scriptDate'] =  supportFile.readline().split(':')[-1].strip()
    return scInfo


# Function:    getVersion
#%%
# Description: Compares the RPM_VERSION to the installed RPM_NAME's version
# Requires:    RPM_NAME must be unique and installed
# Input:       RPM_NAME, RPM_VERSION
# Output:      -1 if RPM_NAME older than RPM_VERSION, 0 if RPM_NAME equals RPM_VERSION, 1 if RPM_NAME newer than RPM_VERSION
# Example:
#
#	RPM_NAME = 'mypackage'
#	RPM_VERSION = '1.1.0'
#	if( SUSE.packageInstalled(RPM_NAME) ):
#		INSTALLED_VERSION = SUSE.compareRPM(RPM_NAME, RPM_VERSION)
#		if( INSTALLED_VERSION <= 0 ):
#			Core.updateStatus(Core.CRIT, "Bug detected in " + RPM_VERSION + ", update server for fixes")
#		else:
#			Core.updateStatus(Core.IGNORE, "Bug fixes applied for " + RPM_VERSION)
#	else:
#		Core.updateStatus(Core.ERROR, "ERROR: " + RPM_NAME + " not installed")
#
#return suse release info (SLES 11 SP3)
def getVersion():
  content = {}
  returnVersion = ""
  Core.getSection("basic-environment.txt", "SuSE-release", content)
  for line in content:
     if "SUSE Linux Enterprise Server" in content[line]:
       returnVersion = "SLES"
       tmp = content[line].split(" ")
       returnVersion += " " + tmp[len(tmp) - 2]
       architecture = tmp[len(tmp) - 1].strip("(")
       architecture = architecture.strip(")")
     elif "SUSE Linux Enterprise Desktop" in content[line]:
       returnVersion = "SLED"
       tmp = content[line].split(" ")
       returnVersion += " " + tmp[len(tmp) - 2]
       architecture = tmp[len(tmp) - 1].strip("(")
       architecture = architecture.strip(")")
     if "PATCHLEVEL" in content[line]:
       returnVersion = returnVersion + " SP" + content[line].split(" = ")[1] + " " + architecture
  return returnVersion


# Function:    normalizeVersionName
#%%
# Description: Compares the RPM_VERSION to the installed RPM_NAME's version
# Requires:    RPM_NAME must be unique and installed
# Input:       RPM_NAME, RPM_VERSION
# Output:      -1 if RPM_NAME older than RPM_VERSION, 0 if RPM_NAME equals RPM_VERSION, 1 if RPM_NAME newer than RPM_VERSION
# Example:
#
#	RPM_NAME = 'mypackage'
#	RPM_VERSION = '1.1.0'
#	if( SUSE.packageInstalled(RPM_NAME) ):
#		INSTALLED_VERSION = SUSE.compareRPM(RPM_NAME, RPM_VERSION)
#		if( INSTALLED_VERSION <= 0 ):
#			Core.updateStatus(Core.CRIT, "Bug detected in " + RPM_VERSION + ", update server for fixes")
#		else:
#			Core.updateStatus(Core.IGNORE, "Bug fixes applied for " + RPM_VERSION)
#	else:
#		Core.updateStatus(Core.ERROR, "ERROR: " + RPM_NAME + " not installed")
#
#normalize release info
def normalizeVersionName(versionString):
  versionString = versionString.replace("SUSE Linux Enterprise Server", "SLES")
  versionString = versionString.replace("SUSE Linux Enterprise Desktop", "SLED")
  return versionString



