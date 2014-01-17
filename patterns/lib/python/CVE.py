"""
Supportconfig Analysis Library for CVE generated patterns

This module is used to automaticall generate CVE patterns from the 
CVE web site and is not used for custom patterns.
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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Authors/Contributors:
#     David Hamner (dhamner@novell.com)
#     Modified: 2014 Jan 17
#
##############################################################################

import sys, re, Core, SUSE, string

global path
  
#check if suse versions are the same
def checkVersion(systemName, architecture):
  compareVersion = SUSE.normalizeVersionName(systemName).split(" ")
  myVersion = SUSE.getVersion().split(" ")
  
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


# generates SCA pattern from CVE input string
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

