'''
Supportconfig Analysis Library for Core python patterns

Core library of functions for creating and processing python patterns
'''
##############################################################################
#  Copyright (C) 2023 SUSE LLC
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
##############################################################################
__author__        = 'Jason Record <jason.record@suse.com>'
__date_modified__ = '2023 Oct 05'
__version__       = '2.0.0_dev3'

import sys
import os
import re
from distutils.version import LooseVersion
path = ''

STATUS_TEMPORARY = -2
STATUS_PARTIAL = -1
STATUS_SUCCESS = 0
STATUS_RECOMMEND = 1
STATUS_PROMOTION = 2
STATUS_WARNING = 3
STATUS_CRITICAL = 4
STATUS_ERROR = 5
STATUS_IGNORE = 6

TEMP = STATUS_TEMPORARY
PART = STATUS_PARTIAL
SUCC = STATUS_SUCCESS
REC = STATUS_RECOMMEND
WARN = STATUS_WARNING
CRIT = STATUS_CRITICAL
ERROR = STATUS_ERROR
IGNORE = STATUS_IGNORE

PASS = 0
EXIT = 5

def is_file_active(file_open):
    '''
    Checks if the suportconfig file is at least MIN_FILE_SIZE_BYTES.
    file_open must be the full supportconfig path and filename
    '''
    MIN_FILE_SIZE_BYTES=500 #most inactive files are less than this, but it's not exact

    try:
        file_stat = os.stat(file_open)
    except Exception as error:
        return False

#    print FILE.st_size
    if( file_stat.st_size > MIN_FILE_SIZE_BYTES ):
        return True
    else:
        return False

def get_entire_file(file_open):
    '''
    Loads the entire supportconfig file

    Args:        file_open (String) - The supportconfig path and filename to open
    Returns:    File content list
    '''
    content = []
    try:
        with open(file_open, "rt", errors='ignore') as f:
            for line in f.readlines():
                line = line.strip("\n")
                content.append(line)
    except Exception as error:
        print("Error: Cannot open file - {}: {}".format(_file, str(error)))
        sys.exit(3)

    return content

def get_sections_in_file(file_open):
    '''
    Extracts all section names from file_open and returns section_list.

    Args:       file_open (String) - The supportconfig path and filename to open
    Returns:    list of section names
    '''
    section_list = []
    in_section = False
    section = re.compile(r'^#==[')

    entire_file = get_entire_file(_file)

    for line in entire_file:
        if in_section:
            section_list.append(re.sub('^#\s+', '', line))
            in_section = False
        elif section.search(line):
            in_section = True

    del entire_file
    return section_list

def get_content_section(_content, _section, include_commented_lines=False):
    '''
    Extracts the first section of a supportconfig file _content list matching _section.
    '''
    section_found = False
    section_name = ''
    section_content = []
    section_tag = re.compile(_section)
    commented_line = re.compile(r"^#|^\s+#")

    for line in _content:
        line = line.strip("\n")
        if line.startswith('#==['):
            section_name = ''
            if section_found:
                break
        elif ( section_name == '' ):
            section_name = re.sub('^#', '', line).strip()
        elif section_tag.search(section_name):
            if( len(line) > 0 ):
                if include_commented_lines:
                    section_content.append(line)
                    section_found = True
                else:
                    if commented_line.search(line):
                        continue
                    else:
                        section_content.append(line)
                        section_found = True

    return section_content

def get_file_section(_file, _section, include_commented_lines=False):
    '''
    Extracts the first section of a supportconfig file matching _section.
    '''
    section_content = []
    entire_file = get_entire_file(_file)
    section_content = get_content_section(entire_file, _section, include_commented_lines)

    del entire_file
    return section_content

def normalize_version_string(version_to_normalize):
    '''
    Converts a version string to a list of version elements

    Args:        version_to_normalize
    Returns:     A list of version string elements
    '''
    version_to_normalize = re.sub(r"[\.,\-,_,+]", "|", version_to_normalize)
    version_to_normalize = re.sub(r"([A-Z,a-z]+)", "|\\1|", version_to_normalize)
    version_to_normalize = version_to_normalize.lstrip("0")
    version_to_normalize = re.sub(r"\|\|", "|", version_to_normalize)
    version_to_normalize = version_to_normalize.rstrip("|")

    return version_to_normalize.split("|")

def compare_loose_versions(version1, version2):
    '''
    Compares two version strings using LooseVersion

    Args:        version1 (String) - The first version string
                version2 (String) - The second version string
    Returns:    -1, 0, 1
                    -1    version1 is older than version2
                     0    version1 is the same as version2
                     1    version1 is newer than version2
    Example:

    thisVersion = '1.1.0-2'
    thatVersion = '1.2'
    if( Core.compare_loose_versions(thisVersion, thatVersion) > 0 ):
        Core.updateStatus(Core.WARN, "The version is too old, update the system")
    else:
        Core.updateStatus(Core.IGNORE, "The version is sufficient")
    '''
    if(LooseVersion(version1) > LooseVersion(version2)):
        return 1
    elif (LooseVersion(version1) < LooseVersion(version2)):
        return -1
    return 0

def compare_versions(version1, version2):
    '''
    Compares the left most significant version string elements

    Args:        version1 (String) - The first version string
                version2 (String) - The second version string
    Returns:    -1, 0, 1
                    -1    version1 is older than version2
                     0    version1 is the same as version2
                     1    version1 is newer than version2
    Example:

    thisVersion = '1.1.0-2'
    thatVersion = '1.2'
    if( compare_versions(thisVersion, thatVersion) > 0 ):
        Core.updateStatus(Core.WARN, "The version is too old, update the system")
    else:
        Core.updateStatus(Core.IGNORE, "The version is sufficient")
    '''
    total_elements = 0
    if( str(version1) == str(version2) ):
        return 0
    else:
        first_version = normalize_version_string(version1)
        second_version = normalize_version_string(version2)
        if( len(first_version) <= len(second_version) ):
            total_elements = len(first_version)
        else:
            total_elements = len(second_version)
        for i in range(total_elements):
            if( first_version[i].isdigit() and second_version[i].isdigit() ):
                if( int(first_version[i]) > int(second_version[i]) ):
                    return 1
                elif( int(first_version[i]) < int(second_version[i]) ):
                    return -1
            else:
                if( str(first_version[i]) > str(second_version[i]) ):
                    return 1
                elif( str(first_version[i]) < str(second_version[i]) ):
                    return -1
    return 0

