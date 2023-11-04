'''
Supportconfig Analysis Library for SUSE python patterns

Library of functions for creating python patterns specific to SUSE
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
__date_modified__ = '2023 Nov 02'
__version__       = '2.0.0_dev6'

import re
import os
import sys
import suse_core2 as core
import datetime
import ast

# Kernel version constants
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
SLE15SP5     = '5.14.21-150500.46.4'
SLE15SP6     = '5.999' #Update to actual version when/if applicable
ALP1SP0      = '6.0' #Update to actual version when/if applicable

def package_is_installed(package_name, _pat):
    '''
    The package_name is installed on the server
    Args:        package_name - The RPM package name to check if installed
    Returns:    True or False
                    True    package_name is installed
                    False    package_name is NOT installed
    Example:

    PACKAGE_NAME = 'bind'
    if ( SUSE.package_is_installed(PACKAGE_NAME) ):
        Core.updateStatus(Core.WARN, 'The package ' + PACKAGE_NAME + ' is installed')
    else:
        Core.updateStatus(Core.IGNORE, 'The package ' + PACKAGE_NAME + ' is NOT installed')    
    '''
    rpm_info = get_rpm_info(package_name, _pat)
    if 'version' in rpm_info:
        return True
    return False

def compare_rpm(package, version_to_compare, _pat):
    try:
        version_from_package = get_rpm_info(package, _pat)['version']
        return core.compare_versions(version_from_package, version_to_compare)
    except Exception as error:
        #error out...
        _pat.update_status(core.ERROR, "ERROR: Package info not found -- " + str(error))

def compare_kernel(version_to_compare, _pat):
    IDX_KERNEL_VERSION = 2
    version_running_kernel = ""
    uname_section = core.get_file_section(_pat.get_supportconfig_path('basic-environment.txt'), 'uname -a')
    if len(uname_section) > 0:
        for line in uname_section:
            if line != "":
                version_running_kernel = line.split()[IDX_KERNEL_VERSION]
    else:
        _pat.update_status(core.ERROR, "ERROR: Missing uname section, no kernel version found")

    return core.compare_versions(version_running_kernel, version_to_compare)


def get_rpm_info(package_name, _pat):
    '''
    Retrieves RPM package information from supportconfig files using the specified package_name
    '''
    IDX_NAME = 0
    IDX_VERSION = -1
    rpm_info = {}
    fileOpen = 'rpm.txt'
    content = {}
    tmp_content = {}

    rpm_file = core.get_entire_file(_pat.get_supportconfig_path('rpm.txt'))
    content = core.get_content_section(rpm_file, '[0-9]{DISTRIBUTION}')

    #get name version and vendor
    if len(content) > 0:
        for line in content:
            if line.startswith(package_name + ' '):
                tmp_content = re.sub(' +', ' ', line)
                tmp_content = tmp_content.split(' ')
                rpm_info['name'] = tmp_content[IDX_NAME]
                rpm_info['version'] = tmp_content[IDX_VERSION]
                tmp_content.pop(0)
                tmp_content.pop()
                rpm_info['vendor'] = ' '.join(tmp_content).strip() #vendor
                #rpm_info[1] = tmp_content[1,-2]

    #get install time
    content = core.get_content_section(rpm_file, 'rpm -qa --last')
    if len(content) > 0:
        for line in content:
            if line.startswith(package_name):
                rpm_info['install_time'] = line.split(' ',1)[1].strip()

    del rpm_file
    return rpm_info

class SCAPattern():
    TID_BASE = 'https://www.suse.com/support/kb/doc.php?id='
    BUG_BASE = 'https://bugzilla.suse.com/show_bug.cgi?id='
    CVE_BASE = 'https://www.suse.com/security/cve/'
    meta = {'id': '', 'primary_link': '', 'overall': core.TEMP, 'overall_info': '', 'other_links': {}, 'scpath': ''}
    
    def __init__(self, meta_class, meta_category, meta_component):
        self.meta['class'] = meta_class
        self.meta['category'] = meta_category
        self.meta['component'] = meta_component

    def __str__ (self):
        pattern = '''
Class instance of {}
  class = {}
  category = {}
  component = {}
  id = {}
  primary_link = {}
  overall = {}
  overall_info = {}
  other_links = {}
  scpath = {}

'''
        return pattern.format(self.__class__.__name__, self.meta['class'], self.meta['category'], self.meta['component'], self.meta['id'], self.meta['primary_link'], self.meta['overall'], self.meta['overall_info'], self.meta['other_links'], self.meta['scpath'])

    def set_id(self, pattern_id):
        self.meta['id'] = pattern_id

    def set_primary_link(self, tag):
        self.meta['primary_link'] = tag

    def add_solution_link(self, tag, url, set_primary=False):
        link_tag = 'META_LINK_' + str(tag)
        self.meta['other_links'][link_tag] = url
        if set_primary:
            self.set_primary_link(link_tag)

    def set_tid(self, tid_id, is_primary=True):
        self.add_solution_link('TID', self.TID_BASE + str(tid_id), set_primary=is_primary)

    def set_bug(self, bug_id, is_primary=False):
        self.add_solution_link('BUG', self.BUG_BASE + str(bug_id), set_primary=is_primary)

    def set_cve(self, cve_id, is_primary=False):
        self.add_solution_link('CVE', self.CVE_BASE + str(cve_id), set_primary=is_primary)

    def set_supportconfig_path(self, path):
        if path.endswith('/'):
            self.meta['scpath'] = path
        else:
            self.meta['scpath'] = path + '/'

    def set_status(self, severity, description):
        self.meta['overall'] = severity
        self.meta['overall_info'] = description

    def update_status(self, severity, description):
        if severity > self.meta['overall']:
            self.meta['overall'] = severity
            self.meta['overall_info'] = description

    def get_supportconfig_path(self, scfile):
        file_path = self.meta['scpath'] + scfile
        if os.path.exists(file_path):
            return file_path
        else:
            print('Error: File not found - {}'.format(file_path))
            sys.exit(2)

    def print_results(self):
        result_list = []
        all_links = []
        empty_keys = []
        for key, value in self.meta.items():
            if len(str(value)) < 1:
                empty_keys.append(str(key))
        for key, value in self.meta['other_links'].items():
            all_links.append(str(key) + '=' + value)

        if len(empty_keys) > 0:
            print('Error: Missing SCAPattern instance result value(s): {}'.format(' '.join(empty_keys)))
            sys.exit(2)
        elif len(all_links) < 1:
            print('Error: Missing solution links')
            sys.exit(2)
        else:
            result_list.append('META_CLASS=' + self.meta['class'])
            result_list.append('META_CATEGORY=' + self.meta['category'])
            result_list.append('META_COMPONENT=' + self.meta['component'])
            result_list.append('PATTERN_ID=' + self.meta['id'])
            result_list.append('PRIMARY_LINK=' + self.meta['primary_link'])
            result_list.append('OVERALL=' + str(self.meta['overall']))
            result_list.append('OVERALL_INFO=' + self.meta['overall_info'])
            result_list.append('OTHER_LINKS=' + '|'.join(all_links))

            print('|'.join(result_list))

def get_systemd_service_data(service_name, _pat):
    '''
    Returns a dictionary of systemd service information for service_name
    '''

    serviced_dictionary = {}
    content = core.get_file_section(_pat.get_supportconfig_path('systemd.txt'), "systemctl show '{0}'".format(service_name))
    if( len(content) > 0 ):
        for line in content:
            element = line.split('=')
            key = element[0]
            # remove the key from the key/value pair
            del element[0]
            # assign the value to the dictionary key
            serviced_dictionary[key] = '='.join(element)
    return serviced_dictionary

def evaluate_systemd_service(service_name, _pat):
    '''
    Reports the health of the specified systemd service
    '''
    service_dictionary = get_systemd_service_data(service_name, _pat)
    if( not service_dictionary ):
        _pat.update_status(core.ERROR, 'Error: Service not found - {}'.format(service_name))
    elif( service_dictionary['LoadState'] == 'not-found' ):
        _pat.update_status(core.ERROR, 'Error: Service not found - {}'.format(service_name))
    elif( 'UnitFileState' in service_dictionary ):
        if( service_dictionary['UnitFileState'] == 'enabled' ):
            if( service_dictionary['SubState'] == 'running' ):
                _pat.update_status(core.IGNORE, 'Ignore: Turned on at boot and currently running: {}'.format(service_name))
            else:
                _pat.update_status(core.CRIT, 'Basic Service Health; Turned on at boot, but not running: {}'.format(service_name))
        elif( service_dictionary['UnitFileState'] == 'disabled' ):
            if( service_dictionary['SubState'] == 'running' ):
                _pat.update_status(core.WARN, 'Basic Service Health; Turned off at boot, but currently running: {}'.format(service_name))
            else:
                _pat.update_status(core.IGNORE, 'Ignore: Turned off at boot, not not running: {}'.format(service_name))
        elif( service_dictionary['UnitFileState'] == 'static' ):
            if( service_dictionary['SubState'] == 'running' ):
                _pat.update_status(core.IGNORE, 'Ignore: Static service is currently running: {}'.format(service_name))
            else:
                _pat.update_status(core.WARN, 'Basic Service Health; Static service SubState {0}: {1}'.format(service_name, service_dictionary['SubState']))
        else:
            _pat.update_status(core.ERROR, 'Error: Unknown UnitFileState: {0}'.format(service_dictionary['UnitFileState']))
    else:
        if( service_dictionary['ActiveState'] == 'failed' ):
              _pat.update_status(core.CRIT, 'Basic Service Health; Service failure detected: {}'.format(service_name))
        elif( service_dictionary['ActiveState'] == 'inactive' ):
              _pat.update_status(core.IGNORE, 'Basic Service Health; Service is not active: {}'.format(service_name))
        elif( service_dictionary['ActiveState'] == 'active' ):
            if( service_dictionary['SubState'] == 'running' ):
                  _pat.update_status(core.IGNORE, 'Basic Service Health; Service is running: {}'.format(service_name))
            else:
                  _pat.update_status(core.CRIT, 'Basic Service Health; Service is active, but not running: {}'.format(service_name))
        else:
            _pat.update_status(core.ERROR, 'Error: Unknown ActiveState: {}'.format(service_dictionary['ActiveState']))

    return _pat

def get_filesystem_data(_pat):
    '''
    Gets all fields from the mounted and unmountd file systems with their associated fstab file and df command output.

    Args:                    SCAPattern instance
    Returns:                 List of Dictionaries
    Keys:
        is_mounted           = The device is: False = Not mounted, True = Mounted
        dev_active           = The active device path
        dev_mounted          = The device path from the mount command
        dev_fstab            = The device path from /etc/fstab
        mount_point          = The mount point
        mount_options        = List of mount options used when mounted as shown by the mount command
        fstab_options        = List of mount options defined in the /etc/fstab
        fs_type              = File system type
        fs_dump              = /etc/fstab dump field, '' if missing
        fs_check             = /etc/fstab fsck field, '' if missing
        space_size           = File system size in bytes, '' if missing
        space_used           = File system space used in bytes, '' if missing
        space_avail          = file system space available in bytes, '' if missing
        space_percent_used   = file system percent used, -1 if unknown
    '''
    FREE_TOTAL = 1
    FREE_USED = 2
    FREE_AVAIL = 3

    DF_ELEMENTS_REQUIRED = 6
    DF_line_WRAP = 1
    DF_DEV = 0
    DF_SIZE = 1
    DF_USED = 2
    DF_AVAIL = 3
    DF_PERCENT_USED = 4
    DF_MOUNT_POINT = 5

    FSTAB_ELEMENTS_REQUIRED = 6
    FSTAB_DEV = 0
    FSTAB_MOUNT_POINT = 1
    FSTAB_TYPE = 2
    FSTAB_OPTIONS = 3
    FSTAB_DUMP = 4
    FSTAB_FSCK = 5

    MNT_ELEMENTS_REQUIRED = 6
    MNT_MOUNT_POINT = 2
    MNT_OPTIONS = 5
    MNT_DEV = 0
    MNT_TYPE = 4

    normalized_mount = []
    normalized_fstab = []
    normalized_df = []
    swap = {'total': 0, 'used': 0, 'free': 0, 'percent_used': 0, 'on': False}

    fs_list = [] # this list of filesysetm dictionaries to be returned

    diskio_file = core.get_entire_file(_pat.get_supportconfig_path('fs-diskio.txt'))
    health_file = core.get_entire_file(_pat.get_supportconfig_path('basic-health-check.txt'))
    section_mount = core.get_content_section(diskio_file, '/mount$')
    section_fstab = core.get_content_section(diskio_file, '/etc/fstab')
    section_df = core.get_content_section(health_file, 'df -h')
    section_free = core.get_content_section(health_file, 'free -k')
    del diskio_file
    del health_file

    if( len(section_mount) > 0 and len(section_fstab) > 0 and len(section_df) > 0 ):
        # gather swap information
        if len(section_free) > 0:
            for line_free in section_free: #swap sizes come from free -k, not df command
                if line_free.startswith("Swap:"):
                    entry_free = line_free.split()
                    swap['total'] = int(entry_free[FREE_TOTAL])
                    if  swap['total'] > 0:
                        swap['used'] = int(entry_free[FREE_USED])
                        swap['free'] = int(entry_free[FREE_AVAIL])
                        swap['percent_free'] = int(swap['used'] * 100 / swap['total'])
                        swap['on'] = True
                    break

        # normalize mount section
        for line_mount in section_mount: #load each mount line output into the entry list
            line_mount = line_mount.replace("(", '').replace(")", '')
            entry_mount = line_mount.split()
            if( len(entry_mount) != MNT_ELEMENTS_REQUIRED ): #ignore non-standard mount entries. They should only have six fields.
                entry_mount = []
                continue
            else:
                normalized_mount.append(entry_mount)

        # normalize fstab section
        for line_fstab in section_fstab: #check each line_fstab to the current line_mount
            entry_fstab = line_fstab.split()
            if( len(entry_fstab) != FSTAB_ELEMENTS_REQUIRED ): #consider non-standard entries as not mount_point_matches
                entry_fstab = []
                continue
            else:
                normalized_fstab.append(entry_fstab)

        # normalize df data
        this_entry = []
        for line_df in section_df:
            if line_df.startswith('Filesystem'):
                continue
            else:
                line_df = line_df.replace('%', '')
                entry_df = line_df.strip().split()
                line_len = len(entry_df)
                if( line_len == DF_ELEMENTS_REQUIRED ):
                    normalized_df.append(entry_df)
                elif( line_len == DF_line_WRAP ): # Line wraps because the first field is a very long device name
                    this_entry = entry_df
                elif( line_len < DF_ELEMENTS_REQUIRED ): # Adds the rest of the fields to the device from the first line
                    this_entry.extend(entry_df)
                    if( len(this_entry) == DF_ELEMENTS_REQUIRED ):
                        normalized_df.append(this_entry)

        # combine fstab and df data with matching mounted filesystems
        for list_mount in normalized_mount:
            this_fs = {
                'is_mounted': True, 
                'dev_active': list_mount[MNT_DEV], 
                'dev_mounted': list_mount[MNT_DEV], 
                'mount_point': list_mount[MNT_MOUNT_POINT], 
                'mount_options': list_mount[MNT_OPTIONS].split(','), 
                'fs_type': list_mount[MNT_TYPE]
            }
            mount_point_matches = False
            for list_fstab in normalized_fstab:
                if( list_fstab[FSTAB_MOUNT_POINT] == list_mount[MNT_MOUNT_POINT] ): #mount points match
                    mount_point_matches = True
                    this_fs['dev_fstab'] = list_fstab[FSTAB_DEV]
                    this_fs['fstab_options'] = list_fstab[FSTAB_OPTIONS].split(',')
                    this_fs['fs_dump'] = list_fstab[FSTAB_DUMP]
                    this_fs['fs_check'] = list_fstab[FSTAB_FSCK]
                    break
            if not mount_point_matches: #mounted, but not defined in /etc/fstab
                this_fs['dev_fstab'] = ''
                this_fs['fstab_options'] = []
                this_fs['fs_dump'] = ''
                this_fs['fs_check'] = ''

            mount_point_matches = False
            for list_df in normalized_df:
                if( list_df[DF_MOUNT_POINT] == list_mount[MNT_MOUNT_POINT] ): #mount points match
                    mount_point_matches = True
                    this_fs['space_size'] = list_df[DF_SIZE]
                    this_fs['space_used'] = list_df[DF_USED]
                    this_fs['space_avail'] = list_df[DF_AVAIL]
                    this_fs['space_percent_used'] = int(list_df[DF_PERCENT_USED])
            if( not mount_point_matches ): #entry_df_normalized doesn't match line_mount, so use undefined values
                this_fs['space_size'] = ''
                this_fs['space_used'] = ''
                this_fs['space_avail'] = ''
                this_fs['space_percent_used'] = -1
                
            fs_list.append(this_fs)

        #now add swap and any unmounted filesystems found in /etc/fstab
        for list_fstab in normalized_fstab:
            if( list_fstab[FSTAB_MOUNT_POINT].lower() == "swap" ): # If there is more than one swap device, the same free -k swap data is used for each
                fs_list.append({
                    'is_mounted': swap['on'], 
                    'dev_active': list_fstab[FSTAB_DEV], 
                    'dev_mounted': '', 
                    'mount_point': list_fstab[FSTAB_MOUNT_POINT], 
                    'mount_options': [], 
                    'fs_type': list_fstab[FSTAB_TYPE], 
                    'dev_fstab': list_fstab[FSTAB_DEV], 
                    'fstab_options': list_fstab[FSTAB_OPTIONS].split(','), 
                    'fs_dump': list_fstab[FSTAB_DUMP], 
                    'fs_check': list_fstab[FSTAB_FSCK], 
                    'space_size': swap['total'], 
                    'space_used': swap['used'], 
                    'space_avail': swap['free'], 
                    'space_percent_used': swap['percent_used'] 
                })
            # check for unmounted filesystems
            else:
                found_fstab_dev = False
                for this_fs in fs_list:
                    if this_fs['mount_point'] == list_fstab[FSTAB_MOUNT_POINT]:
                        found_fstab_dev = True
                        break
                if not found_fstab_dev:
                    fs_list.append({
                        'is_mounted': False, 
                        'dev_active': list_fstab[FSTAB_DEV], 
                        'dev_mounted': '', 
                        'mount_point': list_fstab[FSTAB_MOUNT_POINT], 
                        'mount_options': [], 
                        'fs_type': list_fstab[FSTAB_TYPE], 
                        'dev_fstab': list_fstab[FSTAB_DEV], 
                        'fstab_options': list_fstab[FSTAB_OPTIONS].split(','), 
                        'fs_dump': list_fstab[FSTAB_DUMP], 
                        'fs_check': list_fstab[FSTAB_FSCK], 
                        'space_size': '', 
                        'space_used': '', 
                        'space_avail': '', 
                        'space_percent_used': -1
                    })
    else:
        _pat.set_status(core.ERROR, "ERROR: get_filesystem_data: Cannot find /bin/mount(fs-diskio.txt), /etc/fstab(fs-diskio.txt), df -h(basic-health-check.txt) sections")

    del section_mount
    del section_fstab
    del section_df
    del section_free

    return fs_list

def get_scc_info(_pat):
    '''
    Gets information provided by the SUSEConnect --status command in SLE12

    Requires: None
    Args:      SCAPattern instance
    Returns:   List of Dictionaries
    Keys:      The dictionary key names correspond to the field names from SUSEConnect command. The dictionaries are variable in length.
    '''
    suseconnect_section = core.get_file_section(_pat.get_supportconfig_path('updates.txt'), 'SUSEConnect --status')
    scc_info = []
    for line in suseconnect_section:
        if "identifier" in line.lower():
            # SUSEConnect --status generates output that looks like a python list of dictionaries.
            # eval is used to convert it to just that: a list of dictionaries.
            # Since the source is not trusted, literal_eval is used to secure the evaluation.
            scc_info = ast.literal_eval(line.replace(':null,', ':"",').replace(':null}', ':""}'))
#    for i in range(len(scc_info)):
#        print('scc_info[{0}]: {1}'.format(i, scc_info[i]))
#    print()

    return scc_info

def get_server_info(_pat):
    '''
    Gets information about the server

    Args:        None
    Returns:    Dictionary with keys
        hostname (String) - The hostname of the server analyzed
        kernel_ver (String) - The running kernel version
        arch (String)
        distro_name (String) - The name of the distribution
        ver_major (Int) - The major distribution version number
        ver_minor (Int) - The distribution service patch level
    '''
 
    REQUIRED_ELEMENTS = 6
    IDX_HOSTNAME = 1
    IDX_VERSION = 2
    IDX_ARCH = -2
    IDX_KEY = 0
    IDX_VALUE = -1

    server_dictionary = {} 

    basic_env_file = core.get_entire_file(_pat.get_supportconfig_path('basic-environment.txt'))
    uname_section = core.get_content_section(basic_env_file, 'uname -a')
    os_release_section = core.get_content_section(basic_env_file, '/etc/os-release')
    del basic_env_file

    for line in uname_section:
        if "linux" in line.lower():
            server_dictionary['hostname'] = line.split()[IDX_HOSTNAME]
            server_dictionary['kernel_ver'] = line.split()[IDX_VERSION]
            server_dictionary['arch'] = line.split()[IDX_ARCH]

    for line in os_release_section:
        line = line.replace('"', '').strip()
        if line.startswith('VERSION_ID'):
            version_id_list = line.strip().split('=')[IDX_VALUE].split('.')
            if( len(version_id_list) > 1 ):
                server_dictionary['ver_major'] = int(version_id_list[IDX_KEY])
                server_dictionary['ver_minor'] = int(version_id_list[IDX_VALUE])
            else:            
                server_dictionary['ver_major'] = int(version_id_list[IDX_KEY])
                server_dictionary['ver_minor'] = 0
        elif line.startswith('PRETTY_NAME'):
            server_dictionary['distro_name'] = line.split('=')[IDX_VALUE]

    if len(server_dictionary) < REQUIRED_ELEMENTS:
        _pat.set_status(core.ERROR, "Error: <get_server_info> Cannot find complete server information")

    return server_dictionary
    
def get_basic_virt_info(_pat):
    '''
    Gathers Virtualization section of the basic-environment.txt file.

    Args:            None
    Returns:    Dictionary

    Converts the basic-environment.txt section from this:

    #==[ System ]=======================================#
    # Virtualization
    Manufacturer:  HP
    Hardware:      ProLiant DL380 Gen9
    Hypervisor:    None
    Identity:      Not Detected

    to this dictionary:

  {'Hardware': 'ProLiant DL380 Gen9', 'Hypervisor': 'None', 'Identity': 'Not Detected', 'Manufacturer': 'HP'} 
  if Hypervisor == None, is_virtual is set to False, otherwise is_virtual is True.
    '''

    virt_section = core.get_file_section(_pat.get_supportconfig_path('basic-environment.txt'), 'Virtualization')
    dictionary = {}
    for line in virt_section:
        if ":" in line:
            key, value = line.split(":", 1)
            dictionary[key] = value.strip()
    if dictionary['Hypervisor'] == "None":
        dictionary['is_virtual'] = False
    else:
        dictionary['is_virtual'] = True

    return dictionary

def get_proc_cmdline(_pat):
    '''
    Gathers the /proc/cmdline and assigns each value to a list element.

    Args:            None
    Returns:    List
    '''
    cmdline_section = core.get_file_section(_pat.get_supportconfig_path('boot.txt'), '/proc/cmdline')
    list = []
    for line in cmdline_section:
        list = line.split()

    return list

def get_zypper_repo_list(_pat):
    '''
    Gathers zypper repos output into a list of dictionaries

    Args:            None
    Returns:    List of Dictionaries
    Keys:            The dictionary key names correspond to the field names from zypper repos command.
                        Num - repository number
                        Alias
                        Name
                        Enabled - True (Yes) if the repository is enabled, otherwise False (No).
                        Refresh - True (Yes) is the repository is set to refresh, otherwise False (No).
    '''
    repos_section = core.get_file_section(_pat.get_supportconfig_path('updates.txt'), '/zypper\s--.*\srepos')
    startrepos = re.compile("^-*\+-*\+")
    endrepos = re.compile("^#==|^$")
    repos = []
    in_repos = False

    for line in repos_section:
        if in_repos:
            if endrepos.search(line):
                in_repos = False
            else:
                one_repo = line.split('|')
                for this_repo in range(len(one_repo)):
                    one_repo[this_repo] = one_repo[this_repo].strip()
                #Converts one_repo into a dictionary with the named keys
                one_dict = dict(list(zip(['Num', 'Alias', 'Name', 'Enabled', 'Refresh'], one_repo)))
                repos.append(one_dict)
        elif startrepos.search(line):
            in_repos = True

    for this_repo in range(len(repos)):
        if 'yes' in repos[this_repo]['Enabled'].lower():
            repos[this_repo]['Enabled'] = True
        else:
            repos[this_repo]['Enabled'] = False
        if 'yes' in repos[this_repo]['Refresh'].lower():
            repos[this_repo]['Refresh'] = True
        else:
            repos[this_repo]['Refresh'] = False

    for repo in repos:
        print('repo = {}'.format(repo['Name']))
        for key, value in repo.items():
            print("+ {0:15} = {1}".format(key, value))
        print()
    print('------------------\n')

    return repos

def get_zypper_product_list(_pat):
    '''
    Gathers zypper products output into a list of dictionaries

    Args:            None
    Returns:    List of Dictionaries
    Keys:            The dictionary key names correspond to the field names from zypper products command.
                        Status (S) - Product status
                        repository
                        InternalName
                        Name
                        Version
                        Architecture (Arch)
                        is_base - True (Yes) is the product is a base product, otherwise False (No).
    '''
    prod_section = core.get_file_section(_pat.get_supportconfig_path('updates.txt'), '/zypper\s--.*\sproducts')
    startProducts = re.compile("^-*\+-*\+")
    endProducts = re.compile("^#==|^$")
    products = []
    in_products = False
    for line in prod_section:
        if( in_products ):
            if endProducts.search(line):
                in_products = False
            else:
                one_product = line.split('|')
                for this_product in range(len(one_product)):
                    one_product[this_product] = one_product[this_product].strip()
                #Converts one_product into a dictionary with the named keys
                one_dict = dict(list(zip(['Status', 'Respository', 'Internal Name', 'Name', 'Version', 'Architecture', 'Is Base'], one_product)))
                products.append(one_dict)
        elif startProducts.search(line):
            in_products = True

    for this_product in range(len(products)):
        if 'yes' in products[this_product]['Is Base'].lower():
            products[this_product]['Is Base'] = True
        else:
            products[this_product]['Is Base'] = False

    for prod in products:
        print('prod = {}'.format(prod['Name']))
        for key, value in prod.items():
            print("+ {0:15} = {1}".format(key, value))
        print()
    print('------------------\n')

    return products


