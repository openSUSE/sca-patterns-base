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

def packageInstalled(PackageName):
  rpmInfo = getRpmInfo(PackageName)
  if len(rpmInfo) > 0:
    return True
  return False
  
  
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
  fileOpen = "rpm.txt"
  section = "rpm -qa --last"
  content = {}
  if (Core.getSection(fileOpen, section, content)):
    for line in content:
      if content[line].startswith(PackageName):
	rpmInfo['installTime'] = content[line].split(' ',1)[1].strip()
  return rpmInfo

# takes a driver/module name
# returns a python dictionary of driver information
# driver keys: name loaded filename version license description srcversion supported vermagic
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

#takes a package name and version. 
#package must be installed!
#returns -1 if package is older then versionString
#returns 0 if package is the same version as versionString
#returns 1 if package is newer then versionString
def compareRPM(package, versionString):
  try:
    #get package version
    packageVersion = getRpmInfo(package)['version']
    #print "packageVersion = " + packageVersion + ", versionString = " + versionString
    
    return Core.compareVersions(packageVersion, versionString)
  except Exception:
    #error out...
    Core.updateStatus(Core.ERROR, "ERROR: Package not found")
    
#check if kernel version is newer then given version:
#returns a 1 if kernel is newer then given kernel version
#returns a -1 if kernel is older then given kernel version
#returns a 0 if kernel is the same as a given kernel verion
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
  
#check if suse versions are the same
def checkVersion(systemName, architecture):
  compareVersion = normalizeVersionName(systemName).split(" ")
  myVersion = getVersion().split(" ")
  
  #check if supportconfig version info is the same(ish) as systemName given.
  for line in range (0, len(myVersion) - 1):
    if compareVersion[line] in myVersion[line]:
      continue
    else:
      #system version is wrong
      return False
  #check if architecture is the same
  if architecture in myVersion[len(myVersion) - 1] or architecture == "all":
    #version looks right :)
    return True
  #architecture is wrong
  return "False"



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

#normalize release info
def normalizeVersionName(versionString):
  versionString = versionString.replace("SUSE Linux Enterprise Server", "SLES")
  versionString = versionString.replace("SUSE Linux Enterprise Desktop", "SLED")
  return versionString


def cve(cveString):
  cveInfo = cveString.split(":")
  system = cveInfo[0].strip(";").split(";")
  package = cveInfo[1].strip(";").split(";")
  for i in range (0, len(system)):
    subSystem = system[i].split("~")
    if not checkVersion(subSystem[0], subSystem[1]):
      #version of CVE dose not match
      return False
  for i in range (0, len(package)):
    rpmInfo = getRpmInfo(package[i].split(" >= ")['name'])
    #if package installed
    if len(rpmInfo) > 0:
      #If CVE hit
      if (Core.compareVersions(rpmInfo['version'], package[i].split(" >= ")[1]) < 0):
	#print warning and exit pattern
	Core.updateStatus(Core.WARN, rpmInfo['name'] + " vulnerability: " + rpmInfo['version'] + " < " + package[i].split(" >= ")[1]  + ", update system")
	Core.printPatternResults()
	sys.exit()
    #pacage not installed. continue
    continue
