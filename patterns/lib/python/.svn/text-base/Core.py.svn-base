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
#     Modified: 2013 Oct 16
#
#
##############################################################################

import sys, re, distutils.version
from distutils.version import LooseVersion
global path

STATUS_TEMPORARY = -2
STATUS_PARTIAL = -1
STATUS_SUCCESS = 0
STATUS_RECOMMEND = 1
STATUS_PROMOTION = 2
STATUS_WARNING = 3
STATUS_CRITICAL = 4
STATUS_ERROR = 5

TEMP = STATUS_TEMPORARY
PART = STATUS_PARTIAL
SUCC = STATUS_SUCCESS
REC = STATUS_RECOMMEND
WARN = STATUS_WARNING
CRIT = STATUS_CRITICAL
ERROR = STATUS_ERROR

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
  global OVERALL_INFO
  global OVERALL
  global TMP
  global EXIT
  syncVar()
  if(TMP < overAll):
    OVERALL = overAll
  OVERALL_INFO = overAllInfo
  if(OVERALL >= EXIT):
    printPatternResults()
    sys.exit()
    
def syncVar() :
  global OVERALL
  global TMP
  TMP = OVERALL
  
def setStatus(overAll, overAllInfo):
  global OVERALL_INFO
  global OVERALL
  OVERALL = overAll
  OVERALL_INFO = overAllInfo
  

def processOptions():
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

def getPath():
  return path

#get Section of supportconfig
def getSection(FILE_OPEN, SECTION, CONTENT):
  FoundSectionTag = False
  FoundSection = False
  i = 0
  global path
  try:
    FILE = open(path + "/" + FILE_OPEN)
  except Exception:
    updateStatus(ERROR, "ERROR: Cannot open " + FILE_OPEN)
  for line in FILE:
    if FoundSection and not (line.startswith( '#==[' )) and not FoundSectionTag:
      line = line.strip();
      if not (line == ""):
        CONTENT[i] = line
        i = i + 1
    if FoundSectionTag:
      if SECTION in line:
	FoundSection = True
	FoundSectionTag = False
    if line.startswith( '#==[' ):
      FoundSectionTag = True
  FILE.close()
  return FoundSection

def compareVersions(version1, version2):
  if(LooseVersion(version1) > LooseVersion(version2)):
    return 1
  elif (LooseVersion(version1) < LooseVersion(version2)):
    return -1
  return 0

def addBug(URL):
  global OTHER_LINKS
  OTHER_LINKS = OTHER_LINKS + "|META_LINK_BUG=" + URL
