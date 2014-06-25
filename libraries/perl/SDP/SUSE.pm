##############################################################################
#  Copyright (C) 2014 SUSE LINUX Products GmbH
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
#     Modified: 2014 Jun 25
#
#
##############################################################################

##############################################################################
# Module Definition
##############################################################################

package      SDP::SUSE;

=head1 NAME

SDP::SUSE - The Support Diagnostic Pattern perl library for SUSE OS

=head1 SYNOPSIS

use SDP::SUSE;

=head1 DESCRIPTION

Provides necessary functions specific to patterns developed against supportconfig
running on SUSE servers.

=cut

##############################################################################

=head1 CONSTANTS

=head2 Kernel Versions

=over 5

=item SLE9GA, SLE9SP1, SLE9SP2, SLE9SP3, SLE9SP4, SLE9SP5, SLE10GA, SLE10SP1, SLE10SP2, SLE10SP3, SLE10SP4, SLE10SP5, SLE11GA, SLE11SP1, SLE11SP2, SLE11SP3, SLE11SP4, SLE12GA

SUSE Linux Enterprise Server/Desktop kernel versions

=back

=cut

# Kernel Versions
use constant SLE9GA       => '2.6.5-7.97';
use constant SLE9SP1      => '2.6.5-7.139';
use constant SLE9SP2      => '2.6.5-7.191';
use constant SLE9SP3      => '2.6.5-7.244';
use constant SLE9SP4      => '2.6.5-7.308';
use constant SLE9SP5      => '2.6.5-8'; #Update when/if actual version ships
use constant SLE10GA      => '2.6.16.21-0.8';
use constant SLE10SP1     => '2.6.16.46-0.12';
use constant SLE10SP2     => '2.6.16.60-0.21';
use constant SLE10SP3     => '2.6.16.60-0.54.5';
use constant SLE10SP4     => '2.6.16.60-0.85.1';
use constant SLE10SP5     => '2.6.17'; #Update to actual version when/if ready
use constant SLE11GA      => '2.6.27.19-5';
use constant SLE11SP1     => '2.6.32.12-0.7';
use constant SLE11SP2     => '3.0.13-0.27';
use constant SLE11SP3     => '3.0.76-0.11.1';
use constant SLE11SP4     => '3.1'; #Update to actual version when/if ready
use constant SLE12GA      => '3.999'; #Update to actual version when applicable

##############################################################################
# Exports
##############################################################################

require      Exporter;

our @ISA       = qw(Exporter);
our @EXPORT    = qw(SLE9GA SLE9SP1 SLE9SP2 SLE9SP3 SLE9SP4 SLE9SP5 SLE10GA SLE10SP1 SLE10SP2 SLE10SP3 SLE10SP4 SLE10SP5 SLE11GA SLE11SP1 SLE11SP2 SLE11SP3 SLE11SP4 SLE12GA getHostInfo getDriverInfo getServiceInfo getSCInfo getRpmInfo compareKernel compareDriver compareSupportconfig compareRpm packageInstalled packageVerify securityPackageCheck securityPackageCheckNoError securityKernelCheck securitySeverityPackageCheck securitySeverityPackageCheckNoError securitySeverityKernelCheck securitySeverityKernelAnnouncement securityAnnouncementPackageCheck serviceBootstate serviceStatus serviceHealth portInfo xenDomU xenDom0installed xenDom0running netRouteTable getSupportconfigRunDate appCores getBoundIPs getFileSystems haeEnabled);
our $VERSION   = 0.3.4;

use      SDP::Core;

##############################################################################

=head1 FUNCTIONS: Information Gathering

=begin html

<hr>

=end html

=head2 getHostInfo

=over 5

=item Description

Returns a hash containing host and OES information.

=item Usage

	my %HOST_INFO = SDP::SUSE::getHostInfo();
	if ( $HOST_INFO{'oes'} ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "OES Installed on $HOST_INFO{'hostname'}");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "OES NOT Installed on $HOST_INFO{'hostname'}");
	}

=item Input

None

=item Output

Hash with host information.

=item Requires

None

=item Hash Keys

architecture, hostname, kernel, distribution, patchlevel, oes, oesversion, oesmajor, oesdistribution, oespatchlevel, oesbuild, nows, nowsversion

=back

=cut

sub getHostInfo {
	printDebug("> getHostInfo", "BEGIN");
	use constant VERSION_FIELD      => 2;	# uname -r
	use constant HOSTNAME_FIELD     => 1;	# uname -n
	use constant PATCHLEVEL_FIELD   => 1;
	use constant DISTRO_FIELD       => 0;
	use constant ARCH_FIELD         => 1;
	my $RKFILE                      = $ARCH_PATH . "basic-environment.txt"; #The file in which the running kernel is found.
	my %HOST_INFO;

	# Get KERNEL_FROM_SYSTEM from basic-environment.txt
	# Open the file with the kernel version
	if ( ! open(RKFILE, "$RKFILE") ) {
		setStatus(STATUS_ERROR, "ERROR: Cannot open file, $RKFILE");
		printPatternResults();
		exit;
	} else {
		printDebug("  getHostInfo OPEN", $RKFILE);
	}

	my $FILE_LINE;
	my $COUNT=0;
	my $KEY_FOUND=0;
	my @KEY_FIELDS;
	# Get the uname -a string and the output on the following line
	printDebug("  getHostInfo SEARCH FOR", "uname -a");
	foreach $FILE_LINE (<RKFILE>) {
		chomp($FILE_LINE);
		$COUNT++;
		if ( $KEY_FOUND ) {
			printDebug("  getHostInfo KEY FOUND", $FILE_LINE);
			@KEY_FIELDS = split(/ /, $FILE_LINE);
			pop(@KEY_FIELDS);
			%HOST_INFO = (
				hostname      => $KEY_FIELDS[HOSTNAME_FIELD],
				kernel        => $KEY_FIELDS[VERSION_FIELD],
			);
			last;
		} else {
			if ( $FILE_LINE =~ /uname -a/ ) {
				printDebug("  getHostInfo KEY", "FOUND: uname -a");
				$KEY_FOUND++;
			}
		}
	}
	if ( $KEY_FOUND ) {
		printDebug("  getHostInfo RESULTS", "FOUND");
	} else {
		printDebug("  getHostInfo RESULTS", "NOT FOUND");
		setStatus(STATUS_ERROR, "ERROR: Cannot find system kernel in file");
		printPatternResults();
		exit STATUS_ERROR;
	}

	printDebug("  getHostInfo SEARCH FOR", "/etc/SuSE-release");
	$COUNT=0;
	my $MAX_LINES=5;
	$KEY_FOUND=0;
	$HOST_INFO{'distribution'} = "";
	$HOST_INFO{'patchlevel'}   = 0;
	$HOST_INFO{'architecture'} = "";
	seek(RKFILE,0,0);
	foreach $FILE_LINE (<RKFILE>) {
		chomp($FILE_LINE);
		$COUNT++;
		if ( $KEY_FOUND == 1 ) {
			printDebug("  getHostInfo LINE $COUNT", $FILE_LINE);
			@KEY_FIELDS = split('\(|\)', $FILE_LINE);
			$HOST_INFO{'distribution'} = $KEY_FIELDS[DISTRO_FIELD];
			$HOST_INFO{'architecture'} = $KEY_FIELDS[ARCH_FIELD];
			$KEY_FOUND++;
		} elsif ( $KEY_FOUND > 1 ) {
			if ( $FILE_LINE =~ /^PATCHLEVEL/ ) {
				printDebug("  getHostInfo LINE $COUNT", $FILE_LINE);
				@KEY_FIELDS = split('=', $FILE_LINE);
				$HOST_INFO{'patchlevel'} = $KEY_FIELDS[PATCHLEVEL_FIELD];
			}
			last if ( ! $MAX_LINES-- );
		} else {
			if ( $FILE_LINE =~ /\/etc\/suse\-release/i ) {
				printDebug("  getHostInfo LINE $COUNT", "FOUND: /etc/SuSE-release");
				$KEY_FOUND++;
			}
		}
	}
	if ( $KEY_FOUND ) {
		printDebug("  getHostInfo SEARCH RESULTS", "FOUND");
	} else {
		printDebug("  getHostInfo SEARCH RESULTS", "NOT FOUND");
	}

	# Close the file
	if ( ! close(RKFILE) ) {
		setStatus(STATUS_ERROR, "ERROR: Cannot close file");
		printPatternResults();
		exit;
	} else {
		printDebug("  getHostInfo CLOSE", $RKFILE);
	}
	my @CONTENT = ();
	if ( getSection('basic-environment.txt', 'novell-release', \@CONTENT) ) {
		$HOST_INFO{'oes'} = 0;
		foreach $_ (@CONTENT) {
			if ( /Open Enterprise/i ) {
				@KEY_FIELDS = split(/\(/, $_);
				$HOST_INFO{'oesdistribution'} = $KEY_FIELDS[0];
				$HOST_INFO{'oes'} = 1;
				last;
			}
		}
		if ( $HOST_INFO{'oes'} ) {
			$HOST_INFO{'oespatchlevel'} = 0;
			foreach $_ (@CONTENT) {
				if ( /Open Enterprise/i ) {
					@KEY_FIELDS = split(/\(/, $_);
					$HOST_INFO{'oesdistribution'} = $KEY_FIELDS[0];
				} elsif ( /VERSION/ ) {
					@KEY_FIELDS = split(/=/, $_);
					$HOST_INFO{'oesversion'} = $KEY_FIELDS[1];
					if ( $KEY_FIELDS[1] =~ /(\d+)/ ) {
						$HOST_INFO{'oesmajor'} = $1;
					} else {
						$HOST_INFO{'oesmajor'} = -1;
					}
				} elsif ( /PATCHLEVEL/ ) {
					if ( /=/ ) {
						@KEY_FIELDS = split(/=/, $_);
						$HOST_INFO{'oespatchlevel'} = $KEY_FIELDS[1];
					} else {
						$HOST_INFO{'oespatchlevel'} = "N/A";
					}
				} elsif ( /BUILD/ ) {
					if ( /=/ ) {
						@KEY_FIELDS = split(/=/, $_);
						$HOST_INFO{'oesbuild'} = $KEY_FIELDS[1];
					} else {
						$HOST_INFO{'oesbuild'} = "N/A";
					}
				}
			}
		}
	} else {
		$HOST_INFO{'oes'} = 0;
	}

	# Determine NOWS server data
	my $RPM_NAME = 'NOWS-copyMedia';
	my @RPM_INFO = SDP::SUSE::getRpmInfo($RPM_NAME);
	if ( $#RPM_INFO < 0 ) {
		$HOST_INFO{'nows'} = 0;
	} elsif ( $#RPM_INFO > 0 ) {
		$HOST_INFO{'nows'} = 0;
	} else {
		$HOST_INFO{'nows'} = 1;
		($HOST_INFO{'nowsversion'}, undef) = split(/-/, $RPM_INFO[0]{'version'});
	}

	# Remove leading and trailing white space from each field
	while ( my ($key, $value) = each(%HOST_INFO) ) {
		$HOST_INFO{$key} =~ s/\s$|^\s//;
	}

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		print('%HOST_INFO = ');
		while ( ($key, $value) = each(%HOST_INFO) ) {
			print("$key => \"$value\"  ");
		}
		print("\n");
	}
	printDebug("< getHostInfo", "Hostname: $HOST_INFO{'hostname'}");
	return %HOST_INFO;
}

=begin html

<hr>

=end html

=head2 getDriverInfo

=over 5

=item Description

Returns a hash containing loaded kernel module information.

=item Usage

	my $DRIVER_NAME = 'zapi';
	my %DRIVER_INFO = SDP::SUSE::getDriverInfo($DRIVER_NAME);
	if ( $DRIVER_INFO{'loaded'} ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Driver $DRIVER_NAME is loaded and supported = $DRIVER_INFO{'supported'}");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Driver $DRIVER_NAME is NOT loaded");
	}

=item Input

$DRIVER_NAME (The name of the driver about which you want information.)

=item Output

Hash with load kernel driver information.

=item Requires

None

=item Hash Keys

name, loaded, filename, version, license, description, srcversion, supported, vermagic

=back

=cut

sub getDriverInfo {
	my $DRIVER_NAME              = $_[0];
	SDP::Core::printDebug("> getDriverInfo", "$DRIVER_NAME");
	use constant HEADER_LINES   => 0;
	use constant VALUE_FIELD    => 1;
	my %DRIVER_INFO              = (
		name                     => "$DRIVER_NAME",
		loaded                   => 1,
		filename                 => "",
		version                  => "",
		license                  => "",
		description              => "",
		srcversion               => "",
		supported                => "",
		vermagic                 => ""
	);
	my $FILE_OPEN                = 'modules.txt';
	my $SECTION                  = "modinfo $DRIVER_NAME";
	my @CONTENT                  = ();
	my @LINE_CONTENT             = ();
	my $THISHASH                 = "";
	my $SUPPORTED                = 0;
	my @HASHES                   = qw(filename version license description srcversion vermagic);
	my $LINE                     = 0;

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( $LINE++ < HEADER_LINES ); # Skip header lines
			next if ( /^\s*$/ );                   # Skip blank lines
			foreach $THISHASH (@HASHES) {
				if ( /^$THISHASH:/ ) {
					SDP::Core::printDebug("LINE $LINE", $_);
					@LINE_CONTENT = split(/:/, $_);
					$LINE_CONTENT[VALUE_FIELD] =~ s/^\s+|\s+$//g;
					$DRIVER_INFO{$THISHASH}    = $LINE_CONTENT[VALUE_FIELD];
				}
			}
			if ( /^supported:/ ) {
				SDP::Core::printDebug("LINE $LINE", $_);
				@LINE_CONTENT = split(/:/, $_);
				$LINE_CONTENT[VALUE_FIELD]    =~ s/^\s+|\s+$//g;
				$DRIVER_INFO{'supported'}     = $LINE_CONTENT[VALUE_FIELD];
				$SUPPORTED                    = 1;
			}
		}
		if ( ! $SUPPORTED ) {
			$DRIVER_INFO{'supported'}        = 'no';
		}
	} else {
		$DRIVER_INFO{'loaded'}              = 0;
	}
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		print(' %DRIVER_INFO                   = ');
		while ( ($key, $value) = each(%DRIVER_INFO) ) {
			print("$key => \"$value\"  ");
		}
		print("\n");
	}
	SDP::Core::printDebug("< getDriverInfo", "$DRIVER_NAME Loaded: $DRIVER_INFO{'loaded'}");
	return %DRIVER_INFO;
}

=begin html

<hr>

=end html

=head2 getServiceInfo

=over 5

=item Description

Returns a hash containing loaded kernel module information.

=item Usage

	my $SERVICE_NAME = 'novell-nss';
	my %SERVICE_INFO = SDP::SUSE::getServiceInfo($SERVICE_NAME);
	if ( $SERVICE_INFO{'running'} > 0 ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Service $SERVICE_INFO{'name'} is running");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Service $SERVICE_INFO{'name'} is NOT running");
	}

=item Input

$SERVICE_NAME (The system service about which you want information.)

=item Output

Hash with service information information.

=item Requires

None

=item Hash Keys

name  (The service name)

running (-1=Unknown, 0=Unused or Dead, 1=Running)

bootlevels (A list of runlevel numbers in which the service is turned on for boot. An empty string means the service is turned off at boot for all runlevels.)

runlevel (The current system runlevel)

runlevelstatus (0=Service is turned off for the current runlevel, 1=Service is turned on for the current runlevel)

=back

=cut

sub getServiceInfo {
	my $SERVICE_NAME = $_[0];
	SDP::Core::printDebug("> getServiceInfo", "'$SERVICE_NAME'");
	my %SERVICE_TABLE = (
		'novell-afptcpd' => 'novell-afp.txt',
		'novell-ncs' => 'novell-ncs.txt',
		'auditd' => 'security-audit.txt',
		'smt' => 'smt.txt',
		'rcd' => 'updates-daemon.txt',
		'novell-zmd' => 'updates-daemon.txt',
		'novell-nss' => 'novell-nss.txt',
		'novell-smdrd' => 'novell-sms.txt',
		'novell-afptcpd' => 'novell-afp.txt',
		'novell-cifs' => 'novell-cifs.txt',
		'novell-ipsmd' => 'plugin-iPrint.txt',
		'namcd' => 'novell-lum.txt',
		'cron' => 'cron.txt',
		'atd' => 'cron.txt',
		'multipathd' => 'mpio.txt',
		'network' => 'network.txt',
		'nscd' => 'network.txt',
		'iscsitarget' => 'fs-iscsi.txt',
		'open-iscsi' => 'fs-iscsi.txt',
		'nfs' => 'nfs.txt',
		'nfsserver' => 'nfs.txt',
		'portmap' => 'nfs.txt',
		'nfslock' => 'nfs.txt',
		'xntpd' => 'ntp.txt',
		'ntp' => 'ntp.txt',
		'kdump' => 'crash.txt',
		'autofs' => 'fs-autofs.txt',
		'xend' => 'xen.txt',
		'boot.subdomain' => 'security-apparmor.txt',
		'openais' => 'ha.txt',
		'heartbeat' => 'ha.txt',
		'slpd' => 'slp.txt',
		'o2cb' => 'ocfs2.txt',
		'ocfs2' => 'ocfs2.txt',
		'smb' => 'samba.txt',
		'nmb' => 'samba.txt',
		'winbind' => 'samba.txt',
		'smartd' => 'fs-smartmon.txt',
		'ldap' => 'ldap.txt',
		'sshd' => 'ssh.txt',
		'slert' => 'slert.txt',
		'cset' => 'slert.txt',
		'cset.init.d' => 'slert.txt',
		'cups' => 'print.txt',
		'named' => 'dns.txt',
		'novell-named' => 'dns.txt',
		'dhcpd' => 'dhcp.txt',
		'owcimomd' => 'cimom.txt',
		'sfcb' => 'cimom.txt',
		'openibd' => 'ib.txt',
		'apache2' => 'web.txt',
		'novell-httpstkd' => 'web.txt',
	);
	my $FILE_OPEN               = '';
	my %SERVICE_INFO            = (
		name                     => $SERVICE_NAME,
		running                  => -1,
		bootlevels               => "",
		runlevel                 => "",
		runlevelstatus           => 0
	);
	if ( $SERVICE_TABLE{$SERVICE_NAME} ) {
		$FILE_OPEN = $SERVICE_TABLE{$SERVICE_NAME};
	}
	my $SECTION                  = '';
	my @CONTENT                  = ();
	my @LINE_CONTENT             = ();
	my $TMP                      = '';

	if ( $FILE_OPEN ) {
		$SERVICE_INFO{'running'} = 0;
		$SECTION = "/etc/init.d/$SERVICE_NAME status";
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
}

=begin html

<hr>

=end html

=head2 portInfo

=over 5

=item Description

Gathers information about the service listening on $PORT_NUMBER

=item Usage

	my $PORT_NUMBER = '22';
	my %PORT_INFO = SDP::SUSE::portInfo($PORT_NUMBER);
	if ( %PORT_INFO ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Port $PORT_NUMBER Is listening");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Port $PORT_NUMBER Is NOT listening");
	}

=item Input

$PORT_NUMBER (The network port number to check)

=item Output

Hash with port information

=item Hash Keys

port, service

=item Requires

None

=back

=cut

sub portInfo {
	my $PORT_NUMBER = $_[0];
	SDP::Core::printDebug('> portInfo', "$PORT_NUMBER");
	my $HEADER_LINES = 2;
	my $RCODE = 0;
	my $FILE_OPEN = 'network.txt';
	my $SECTION = 'netstat -nlp';
	my %PORT_INFO = ();
	my @CONTENT = ();
	my @LINE_CONTENT = ();
	my $LINE = 0;

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( $LINE++ < $HEADER_LINES ); # Skip header lines
			next if ( /^\s*$/ );                    # Skip blank lines
			@LINE_CONTENT = split(/\s+|\//, $_);
			if ( /:$PORT_NUMBER\s/ ) {
				SDP::Core::printDebug("ACTION", $_);
				@LINE_CONTENT = split(/\s+|\//, $_);
				$PORT_INFO{'port'} = $PORT_NUMBER;
				$PORT_INFO{'pid'} = $LINE_CONTENT[6];
				$PORT_INFO{'service'} = $LINE_CONTENT[7];
				$PORT_INFO{'protocol'} = $LINE_CONTENT[0];
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		print(' %PORT_INFO                     = ');
		while ( ($key, $value) = each(%PORT_INFO) ) {
			print("$key => \"$value\"  ");
		}
		print("\n");
	}
	SDP::Core::printDebug("< portInfo", "Return: $RCODE, $PORT_NUMBER-$PORT_INFO{'service'}");
	return %PORT_INFO;
}

=begin html

<hr>

=end html

=head2 getBoundIPs

=over 5

=item Description

Identifies all IPv4 IP addresses bound to the server.

=item Usage

	my $i = '';
	my @BOUND_IP = ();
	my $TYPE = '';
	my $PRI = 0;
	my $SEC = 0;
	my $ALL = 0;

	if ( SDP::SUSE::getBoundIPs(\@BOUND_IP) ) {
		for $i ( 0 .. $#BOUND_IP ) {
			if ( $BOUND_IP[$i]{'issec'} ) {
				$TYPE = 'Secondary';
				$SEC++;;
			} else {
				$TYPE = 'Primary';
				$PRI++;
			}
			SDP::Core::updateStatus(STATUS_PARTIAL, "$TYPE $BOUND_IP[$i]{'interface'} addr:$BOUND_IP[$i]{'addr'}");
		}
		$ALL = scalar(@BOUND_IP);
		SDP::Core::updateStatus(STATUS_ERROR, "Bound IP Addresses: Primary=$PRI, Secondary=$SEC, TOTAL=$ALL");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "Error: No IP addresses bound to the server");
	}

=item Input

Array address

=item Output

Array of hashes containing the address details

=item Hash Keys

interface, addr, bcast, mask, mac, irq, config, issec

=item Requires

None

=back

=cut

sub getBoundIPs {
	SDP::Core::printDebug('> getBoundIPs', "BEGIN");
	my $RCODE = 0;
	my $FILE_OPEN = 'network.txt';
	my @CONTENT = ();
	my @LINE_CONTENT = ();
	my $ARRAY_REF = $_[0];
	my $IP_CNT = 0;
	my $STATE = 0;

	my $IFACE = '';
	my $ADDR = '';
	my $BCAST = '';
	my $NETMASK = '';
	my $MAC = '';
	my $IRQ = '';
	my $CONFIG = '';

	my $SECTION = 'ifconfig -a';
	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			if ( $STATE ) {
				SDP::Core::printDebug("$IFACE", "$_");
				if ( /^\s*$/ ) { # blank line means add interface and move to next one
					SDP::Core::printDebug("Add Interface", "interface => $IFACE, addr => $ADDR, bcast => $BCAST, mask => $NETMASK, mac => $MAC, irq => $IRQ");
					push(@$ARRAY_REF, { interface => "$IFACE", addr => "$ADDR", bcast => "$BCAST", mask => "$NETMASK", mac => "$MAC", irq => "$IRQ", config => $CONFIG, issec => 0 } );
					$IP_CNT++;
					$STATE = 0; # move to next interface on next line
					# reinitialize values
					$IFACE = '';
					$ADDR = '';
					$BCAST = '';
					$NETMASK = '';
					$MAC = '';
					$IRQ = '';
					$CONFIG = '';
				} elsif ( /inet addr:/i ) {
					@LINE_CONTENT = split(/\s+/, $_);
					$ADDR = $LINE_CONTENT[2];
					$ADDR =~ s/addr://;
					$NETMASK = pop(@LINE_CONTENT);
					$NETMASK =~ s/mask://i;
					my $i;
					foreach $i (@LINE_CONTENT) {
						if ( $i =~ /bcast:/i ) {
							$i =~ s/bcast://i;
							$BCAST = $i;
							last;
						}
					}
				} elsif ( /interrupt/i ) {
					@LINE_CONTENT = split(/\s+/, $_);
					$IRQ = $LINE_CONTENT[1];
					$IRQ =~ s/Interrupt://i;
				}
			} else {
				if ( /^\S/ ) { # line begins with an interface character, not white space
					$STATE = 1;
					@LINE_CONTENT = split(/\s+/, $_);
					$IFACE = $LINE_CONTENT[0];
					$MAC = pop(@LINE_CONTENT);
				}
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}

	$SECTION = '/etc/init.d/network status';
	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		my $i;
		foreach $_ (@CONTENT) {
			if ( /configuration:/i ) {
				SDP::Core::printDebug("CONFIG", $_);
				@LINE_CONTENT = split(/\s+/, $_);
				$CONFIG = pop(@LINE_CONTENT);
				for $i ( 0 .. (scalar(@{$ARRAY_REF}) - 1) ) {
					if ( $$ARRAY_REF[$i]{'interface'} =~ $LINE_CONTENT[1] ) {
						$$ARRAY_REF[$i]{'config'} = $CONFIG;
						SDP::Core::printDebug("  >Modifying", "interface => $$ARRAY_REF[$i]{'interface'}, addr => $$ARRAY_REF[$i]{'addr'}, config => $CONFIG");
						last;
					}
				}
			} elsif ( /^\s+secondary/i ) {
				SDP::Core::printDebug("SECONDARY", $_);
				@LINE_CONTENT = split(/\s+|\//, $_);
				$IFACE = $LINE_CONTENT[2];
				$ADDR = $LINE_CONTENT[5];
				my $CIDR = $LINE_CONTENT[6];
				$BCAST = '';
				$NETMASK = '';
				$MAC = '';
				$IRQ = '';
				$CONFIG = '';
				my $NEW_IFACE = 1;
				for $i ( 0 .. (scalar(@{$ARRAY_REF}) - 1) ) {
					if ( $$ARRAY_REF[$i]{'interface'} =~ $IFACE && $$ARRAY_REF[$i]{'addr'} =~ $ADDR ) {
						$$ARRAY_REF[$i]{'issec'} = 1;
						SDP::Core::printDebug("  >Modifying", "interface == $$ARRAY_REF[$i]{'interface'}, addr == $$ARRAY_REF[$i]{'addr'}, issec == 1");
						$NEW_IFACE = 0;
						last;
					}
				}
				if ( $NEW_IFACE ) {
					my $j;
					for ( $j = 0 ; $j < 4 ; $j++) {
						$NETMASK .= "." if $j != 0;
						if ( $CIDR >= 8 ) {
							$NETMASK .= 255;
							$CIDR = $CIDR - 8;
						} elsif ( $CIDR != 0 ) {
							$NETMASK .= 2 ** $CIDR;
							$CIDR = 0;
						} else {
							$NETMASK .= 0;
						}
					}
					SDP::Core::printDebug("  >Adding", "interface => $IFACE, addr => $ADDR, bcast => $BCAST, mask => $NETMASK, mac => $MAC, irq => $IRQ");
					push(@$ARRAY_REF, { interface => "$IFACE", addr => "$ADDR", bcast => "$BCAST", mask => "$NETMASK", mac => "$MAC", irq => "$IRQ", config => $CONFIG, issec => 1 } );
					$IP_CNT++;
				}
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		my $i = 0;
		my $hash;
		foreach $hash (@$ARRAY_REF) {
			print(" ARRARY_REF $i                   = ");
			while ( ($key, $value) = each(%$hash) ) {
				print("$key => \"$value\"  ");
			}
			print("\n");
			$i++;
		}
	}
	SDP::Core::printDebug("< getBoundIPs", "Bound IP Addresses Found: $IP_CNT");
	return $IP_CNT;
}

=begin html

<hr>

=end html

=head2 netRouteTable

=over 5

=item Description

Gathers information from the routing table.

=item Usage

	my $i = '';
	my @NETWORK_ROUTES = ();

	if ( SDP::SUSE::netRouteTable(\@NETWORK_ROUTES) ) {
		for $i ( 0 .. $#NETWORK_ROUTES ) {
			SDP::Core::printDebug('ROUTE', "$i of $#NETWORK_ROUTES: $NETWORK_ROUTES[$i]{'gateway'} - $NETWORK_ROUTES[$i]{'flags'}");
		}
	}

=item Input

Array address

=item Output

Array of hashes

=item Hash Keys

destination, gateway, genmask, flags, mss, window, irtt, interface

=item Requires

None

=back

=cut

sub netRouteTable {
	SDP::Core::printDebug('> netRouteTable', "BEGIN");
	my $HEADER_LINES = 2;
	my $RCODE = 0;
	my $FILE_OPEN = 'network.txt';
	my $SECTION = 'netstat -nr';
	my %ROUTE_INFO = ();
	my @CONTENT = ();
	my @LINE_CONTENT = ();
	my $LINE = 0;
	my $ARRAY_REF = $_[0];
	my $ROUTE_CNT = 0;

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( $LINE++ < $HEADER_LINES ); # Skip header lines
			next if ( /^\s*$/ ); # Skip blank lines
			@LINE_CONTENT = split(/\s+/, $_);
			$ROUTE_INFO{'distination'} = $LINE_CONTENT[0];
			$ROUTE_INFO{'gateway'} = $LINE_CONTENT[1];
			$ROUTE_INFO{'genmask'} = $LINE_CONTENT[2];
			$ROUTE_INFO{'flags'} = $LINE_CONTENT[3];
			$ROUTE_INFO{'mss'} = $LINE_CONTENT[4];
			$ROUTE_INFO{'window'} = $LINE_CONTENT[5];
			$ROUTE_INFO{'irtt'} = $LINE_CONTENT[6];
			$ROUTE_INFO{'interface'} = $LINE_CONTENT[7];
			push(@$ARRAY_REF, { destination => "$LINE_CONTENT[0]", gateway => "$LINE_CONTENT[1]", genmask => "$LINE_CONTENT[2]", flags => "$LINE_CONTENT[3]", mss => "$LINE_CONTENT[4]", window => "$LINE_CONTENT[5]", irtt => "$LINE_CONTENT[6]", interface => "$LINE_CONTENT[7]" } );
			$ROUTE_CNT++;
			if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
				print(' %ROUTE_INFO                    = ');
				while ( ($key, $value) = each(%ROUTE_INFO) ) {
					print("$key => \"$value\"  ");
				}
				print("\n");
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}

	SDP::Core::printDebug("< netRouteTable", "Routes Found: $ROUTE_CNT");
	return $ROUTE_CNT;
}

=begin html

<hr>

=end html

=head2 getFileSystems

=over 5

=item Description

Gets all fields from the mounted file systems and the fstab file. Information is returned as an array of hashes.

=item Usage

	my @MOUNTS = SDP::SUSE::getFileSystems();
	my $TMP;
	my $FOUND = 0;
	foreach $TMP (@MOUNTS) {
		if ( $TMP->{'MPT'} eq '/' ) {
			SDP::Core::updateStatus(STATUS_SUCCESS, "Found root device $TMP->{'DEV'} mounted on $TMP->{'MPT'} with file system $TMP->{'TYPE'}");
			$FOUND = 1;
		}
	}
	SDP::Core::setStatus(STATUS_CRITICAL, 'Root file system not found') if ( ! $FOUND );

=item Input

None

=item Output

Array of hashes

=item Hash Keys

DEV, DEVM, DEVF, MPT, TYPE, OPTIONS, DUMP, FSCK, MOUNTED, SIZE, USED, AVAIL, USEPCT

	DEV     = The active device path
	DEVM    = The device path from the mount command
	DEVF    = The device path from /etc/fstab
	MPT     = The mount point
	TYPE    = File system type
	OPTIONS = Options used when mounted or mounting
	DUMP    = /etc/fstab dump field, -1 if unknown
	FSCK    = /etc/fstab fsck field, -1 if unknown
	MOUNTED = -1 Unknown, 0 Not mounted, 1 Mounted
	SIZE    = -1 Unknown, file system size in bytes
	USED    = -1 Unknown, file system space used in bytes
	AVAIL   = -1 Unknown, file system space available in bytes
	USEPCT  = -1 Unknown, file system percent used

=item Requires

None

=back

=cut

sub getFileSystems {
	SDP::Core::printDebug('> getFileSystems', 'BEGIN');
	use constant DISK_MOUNT_FIELD => 5;
	my $RCODE = 0;
	my @DEVICES = ();
	my @FIELD = ();
	my @THIS_ENTRY = ();
	my $FILE_OPEN = 'fs-diskio.txt';
	my @MOUNTS = ();
	my @FSTABS = ();
	my @DFCMD = ();
	my $MOUNT;
	my $FSTAB;
	my $I;

	# Populate both section arrays
	if ( SDP::Core::getSection($FILE_OPEN, '/bin/mount', \@MOUNTS) && SDP::Core::getSection($FILE_OPEN, '/etc/fstab', \@FSTABS) && SDP::Core::getSection('basic-health-check.txt', 'df -h', \@DFCMD)  ) {
		SDP::Core::printDebug("SECTIONS", "Found /bin/mount, /etc/fstab and df -h sections");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: getFileSystems(): Cannot find /bin/mount($FILE_OPEN), /etc/fstab($FILE_OPEN), df -h(basic-health-check.txt) sections");
	}

	# Get /bin/mount fields
	foreach $MOUNT (@MOUNTS) {
		next if ( $MOUNT =~ m/^\s*$/ ); # Skip blank lines
		$MOUNT =~ s/\(|\)//g; # remove the parentheses around the options
		SDP::Core::printDebug("MOUNT", $MOUNT);
		@FIELD = split(/\s+/, $MOUNT);
		# Merge in the /etc/fstab fields
		my $MATCHED;
		foreach $FSTAB (@FSTABS) {
			$MATCHED = 0;
			next if ( $FSTAB =~ m/^\s*$/ ); # Skip blank lines
			@THIS_ENTRY = split(/\s+/, $FSTAB);
			if ( "$THIS_ENTRY[1]" eq "$FIELD[2]" ) { # same mount point
				SDP::Core::printDebug(" ADD FSTAB", $FSTAB);
				$MATCHED = 1;
				push(@FIELD, $THIS_ENTRY[4]); # dump
				push(@FIELD, $THIS_ENTRY[5]); # fsck
				push(@FIELD, $THIS_ENTRY[0]); # fstab device
				last;
			}
		}
		if ( ! $MATCHED ) { # mounted but not defined in /etc/fstab
			push(@FIELD, -1); # dump
			push(@FIELD, -1); # fsck
			push(@FIELD, $FIELD[0]); # no fstab device
		}
		# add file system size info
		my $LINE_WRAPPED = 0;
		my $I;
		my @LINE_DATA = ();
		my $DFDATA = ();
		my $FOUND_SIZES = 0;
		foreach $_ (@DFCMD) {
			next if ( m/^\s*$|^Filesystem/ ); # Skip blank lines and header line
			$_ = SDP::Core::ltrimWhite($_);
			@LINE_DATA = split(/\s+/, $_);
#			print(" LINE                               = $#LINE_DATA of ". DISK_MOUNT_FIELD ." :: @LINE_DATA\n") if $OPT_LOGLEVEL >= LOGLEVEL_DEBUG;
			if ( $LINE_WRAPPED ) {
				for ( $I = 0; $I <= $#LINE_DATA; $I++ ) {
					push(@DFDATA, $LINE_DATA[$I]);
				}
				$LINE_WRAPPED=0;
			} else {
				@DFDATA = @LINE_DATA;
			}
			if ( $#DFDATA < DISK_MOUNT_FIELD ) {
#				printDebug(" STATUS", "  INCOMPLETE");
				@DFDATA = @LINE_DATA;
				$LINE_WRAPPED = 1;
			} else {
				printDebug("DATA", "@DFDATA");
				my ($FS, $SIZE, $USED, $AVAIL, $USEPCT, $MNT) = (@DFDATA);
				printDebug("VALUES", "$FS $SIZE $USED $AVAIL $USEPCT $MNT");
				$USEPCT =~ s/%//g;
				if ( $FIELD[2] eq $MNT ) {
					push(@FIELD, $SIZE);
					push(@FIELD, $USED);
					push(@FIELD, $AVAIL);
					push(@FIELD, $USEPCT);
					$FOUND_SIZES = 1;
					last;
				}
			}
		}
		if ( ! $FOUND_SIZES ) {
			push(@FIELD, -1);
			push(@FIELD, -1);
			push(@FIELD, -1);
			push(@FIELD, -1);
		}
		push(@DEVICES, { DEV => $FIELD[8], DEVM => $FIELD[0], DEVF => $FIELD[8], MPT => $FIELD[2], TYPE => $FIELD[4], OPTIONS => $FIELD[5], DUMP => $FIELD[6], FSCK => $FIELD[7], MOUNTED => 1, SIZE => $FIELD[9], USED => $FIELD[10], AVAIL => $FIELD[11], USEPCT => $FIELD[12] } );
	}

	# Add unmounted fstab entries
	foreach $FSTAB (@FSTABS) {
		next if ( $FSTAB =~ m/^\s*$|^#/ ); # Skip blank and commented lines
		SDP::Core::printDebug("FSTAB", $FSTAB);
		@FIELD = split(/\s+/, $FSTAB);
		# If there is more than one swap device, and any one of them is on, each swap device will be declared mounted. I can't tell if each individual device is mounted.
		if ( "$FIELD[1]" eq "swap" ) {
			my @SWAP = ();
			if ( SDP::Core::getSection('basic-health-check.txt', 'free -k', \@SWAP) ) {
				foreach $_ (@SWAP) {
					if ( /Swap:\s+(\d+)\s+/i ) {
						SDP::Core::printDebug(" FOUND", "Swap Total: $1");
						if ( $1 > 0 ) {
							push(@DEVICES, { DEV => $FIELD[0], DEVM => '', DEVF => $FIELD[0], MPT => $FIELD[1], TYPE => $FIELD[2], OPTIONS => $FIELD[3], DUMP => $FIELD[4], FSCK => $FIELD[5], MOUNTED => 1, SIZE => -1, USED => -1, AVAIL => -1, USEPCT => -1 } );
						} else {
							push(@DEVICES, { DEV => $FIELD[0], DEVM => '', DEVF => $FIELD[0], MPT => $FIELD[1], TYPE => $FIELD[2], OPTIONS => $FIELD[3], DUMP => $FIELD[4], FSCK => $FIELD[5], MOUNTED => 0, SIZE => -1, USED => -1, AVAIL => -1, USEPCT => -1 } );
						}
						last;
					}
				}
			} else { # mounted -1 means I don't know if it's mounted
				push(@DEVICES, { DEV => $FIELD[0], DEVM => '', DEVF => $FIELD[0], MPT => $FIELD[1], TYPE => $FIELD[2], OPTIONS => $FIELD[3], DUMP => $FIELD[4], FSCK => $FIELD[5], MOUNTED => -1, SIZE => -1, USED => -1, AVAIL => -1, USEPCT => -1 } );
			}
		} else {
			my $NEEDED;
			foreach $MOUNT (@MOUNTS) {
				$NEEDED = 1;
				next if ( $MOUNT =~ m/^\s*$/ ); # Skip blank lines
				@THIS_ENTRY = split(/\s+/, $MOUNT);
				if ( "$THIS_ENTRY[2]" eq "$FIELD[1]" ) { # same mount point
					$NEEDED = 0; # Not needed
					last;
				}
			}
			if ( $NEEDED ) {
				SDP::Core::printDebug(" ADDED", "Missing Entry");
				push(@DEVICES, { DEV => $FIELD[0], DEVM => '', DEVF => $FIELD[0], MPT => $FIELD[1], TYPE => $FIELD[2], OPTIONS => $FIELD[3], DUMP => $FIELD[4], FSCK => $FIELD[5], MOUNTED => 0, SIZE => -1, USED => -1, AVAIL => -1, USEPCT => -1 } );
			}
		}
	}

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		my $TMP;
		foreach $TMP (@DEVICES) {
		print(' File System                    = ');
		while ( ($key, $value) = each(%$TMP) ) {
			print("$key => \"$value\"  ");
		}
		print("\n");
		}
	}

	$RCODE = scalar @DEVICES;
	SDP::Core::printDebug("< getFileSystems", "Entries: $RCODE");
	return @DEVICES;
}

=begin html

<hr>

=end html

=head2 getSCInfo

=over 5

=item Description

Returns a hash containing supportconfig information.

=item Usage

	my $REQUIRED_VERSION = '2.25-173';
	my %SC_INFO = SDP::SUSE::getSCInfo();
	if ( SDP::Core::compareVersions($SC_INFO{'version'}, $REQUIRED_VERSION) >= 0 ) {
		SDP::Core::updateStatus(STATUS_ERROR, "Supportconfig v$SC_INFO{'version'} meets minimum requirement");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Supportconfig v$SC_INFO{'version'} NOT sufficient, $REQUIRED_VERSION or higher needed");
	}

=item Input

None

=item Output

Hash with supportconfig information.

=item Requires

None

=item Hash Keys

version, scriptdate, cmdline, config, envalue, kernvalue, rundate

=back

=cut

sub getSCInfo {
	SDP::Core::printDebug("> getSCInfo", "BEGIN");
	my $HEADER_LINES             = 0;
	my $VALUE_FIELD              = 1;
	my $FILE_OPEN                = 'supportconfig.txt';
	my $SECTION                  = "supportutils";
	my @CONTENT                  = ();
	my @LINE_CONTENT             = ();
	my $LINE                     = 0;
	my %SC_INFO                  = (
		version                  => "",
		scriptdate               => "",
		cmdline                  => "",
		config                   => "",
		envalue                  => "",
		kernvalue                => ""
	);

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( $LINE++ < $HEADER_LINES ); # Skip header lines
			next if ( /^\s*$/ );                    # Skip blank lines
			if ( /Environment Value:/i ) {
				SDP::Core::printDebug("  getSCInfo ENV", $_);
				@LINE_CONTENT = split(/:/, $_);
				$LINE_CONTENT[$VALUE_FIELD]    =~ s/^\s+|\s+$//g;
				$LINE_CONTENT[$VALUE_FIELD]    =~ m/(\d+)/;
				$SC_INFO{'envalue'}            = $1;
				$LINE_CONTENT[$VALUE_FIELD]    =~ m/\((\d+)\)/;
				$SC_INFO{'kernvalue'}          = $1;
			} elsif ( /Command with Args:/i ) {
				SDP::Core::printDebug("  getSCInfo ARGS", $_);
				@LINE_CONTENT = split(/:/, $_);
				$LINE_CONTENT[$VALUE_FIELD]    =~ s/^\s+|\s+$//g;
				$SC_INFO{'cmdline'}            = $LINE_CONTENT[$VALUE_FIELD];
			} elsif ( /Using Options:/i ) {
				SDP::Core::printDebug("  getSCInfo OPTIONS", $_);
				@LINE_CONTENT = split(/:/, $_);
				$LINE_CONTENT[$VALUE_FIELD]    =~ s/^\s+|\s+$//g;
				$SC_INFO{'config'}            = $LINE_CONTENT[$VALUE_FIELD];
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	$FILE_OPEN = $ARCH_PATH . 'basic-environment.txt';
	# Open basic-environment.txt for supportconfig information. Opening the file directly because the supportconfig information is not in a typical header
	if ( ! open(FILE, "$FILE_OPEN") ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot open file, $FILE_OPEN");
	} else {
		SDP::Core::printDebug("  getSCInfo OPEN", $FILE_OPEN);
	}

	$LINE          = 0;
	$LINE_MAX      = 7;
	@LINE_CONTENT  = ();
	$VALUE_FIELD   = 1;
	while(<FILE>) {
		last if ($LINE++ > $LINE_MAX);
		chomp($_);
		s/^\s+|\s+$//g;
		if ( m/Script Version:/ ) {
			SDP::Core::printDebug("  getSCInfo VERSION", $_);
			@LINE_CONTENT = split(/:/, $_);
			$LINE_CONTENT[$VALUE_FIELD]    =~ s/^\s+|\s+$//g;
			$SC_INFO{'version'}            = $LINE_CONTENT[$VALUE_FIELD];
		} elsif ( m/Script Date:/ ) {
				SDP::Core::printDebug("  getSCInfo SCRIPT DATE", $_);
			@LINE_CONTENT = split(/:/, $_);
			$LINE_CONTENT[$VALUE_FIELD]    =~ s/^\s+|\s+$//g;
			$SC_INFO{'scriptdate'}         = $LINE_CONTENT[$VALUE_FIELD];
		}	
	}
	seek(FILE, 0, 0);
	my $STATE = 0;
	$LINE     = 0;
	while(<FILE>) {
		$LINE++;
		chomp($_);
		if ($STATE) {
			# process the output of the date command
			SDP::Core::printDebug("  getSCInfo RUN DATE", $_);
			$SC_INFO{'rundate'} = $_;
			last;
		} else {
			# found the command, now get the next line
			if ( m/\/bin\/date/ ) {
				$STATE = !$STATE;
			}
		}
	}

	# Close the file
	if ( ! close(FILE) ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot close file");
	} else {
		SDP::Core::printDebug("  getSCInfo CLOSE", $FILE_OPEN);
	}

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		print(' %SC_INFO = ');
		while ( ($key, $value) = each(%SC_INFO) ) {
			print("$key => \"$value\"  ");
		}
		print("\n");
	}

	SDP::Core::printDebug("< getSCInfo", "Version: $SC_INFO{'envalue'}");
	return %SC_INFO;
}

##############################################################################

=head1 FUNCTIONS: Comparisons

=begin html

<hr>

=end html

=head2 compareKernel

=over 5

=item Description

Uses SDP::Core::compareVersions to compare $test_version against the running kernel version. Only the most significant version components are compared. For example, if 2.6.5 is compared with 2.6.16.60-0.23, then only 2.6.5 and 2.6.16 will be used for the comparison. 

=item Usage

	if ( SDP::SUSE::compareKernel(SLE10SP1) >= 0 && SDP::SUSE::compareKernel(SLE10SP2) < 0) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Running SLES10 SP1 Kernel");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ABORT: Outside the kernel scope");
	}

=item Input

$test_version (The version string to which the running kernel's version is compared.)

=item Output

-1 if kernel_version < $test_version

0 if kernel_version == $test_version

1 if kernel_version > $test_version

=item Requires

None

=back

=cut

sub compareKernel {
	my $COMPARE_TO       = $_[0];
	my %HOST_INFO        = getHostInfo();
	SDP::Core::printDebug("  compareKernel COMPARING", $HOST_INFO{'kernel'} . " to " . $COMPARE_TO);
	my $RESULT           = SDP::Core::compareVersions($HOST_INFO{'kernel'}, $COMPARE_TO);

	SDP::Core::printDebug("< compareKernel", "Result: $RESULT");
	return $RESULT;
}

=begin html

<hr>

=end html

=head2 compareDriver

=over 5

=item Description

Uses SDP::Core::compareVersions to compare the $DRIVER_NAME and $TEST_VERSION against the loaded driver version. Only the most significant version components are compared. For example, if 2.6.5 is compared with 2.6.16.60-0.23, then only 2.6.5 and 2.6.16 will be used for the comparison. 

=item Usage

	my $DRIVER_NAME = 'mptctl';
	my $TEST_VERSION = '5.25';
	if ( SDP::SUSE::compareDriver($DRIVER_NAME, $TEST_VERSION) >= 0 ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "$DRIVER_NAME version meets minimum requirement");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "$DRIVER_NAME version NOT sufficient, $TEST_VERSION or higher needed");
	}

=item Input

$DRIVER_NAME (The driver name that needs to be compared.)

$TEST_VERSION (The version string to which the loaded driver's version is compared.)

=item Output

-1 if driver_version < $TEST_VERSION

0 if driver_version == $TEST_VERSION

1 if driver_version > $TEST_VERSION

=item Requires

None

=back

=cut

sub compareDriver {
	printDebug("> compareDriver", "BEGIN");
	my $DRIVER_NAME      = $_[0];
	my $COMPARE_TO       = $_[1];
	my %DRIVER_INFO      = getDriverInfo($DRIVER_NAME);

	SDP::Core::printDebug("COMPARING", $DRIVER_INFO{'version'} . " to " . $COMPARE_TO);
	my $RESULT           = SDP::Core::compareVersions($DRIVER_INFO{'version'}, $COMPARE_TO);

	SDP::Core::printDebug("< compareDriver", "Result: $RESULT");
	return $RESULT;
}

=begin html

<hr>

=end html

=head2 compareSupportconfig

=over 5

=item Description

Uses SDP::Core::compareVersions to compare $TEST_VERSION against the supportconfig version. Only the most significant version components are compared. For example, if 2.6.5 is compared with 2.6.16.60-0.23, then only 2.6.5 and 2.6.16 will be used for the comparison. 

=item Usage

	my $TEST_VERSION = '2.25-173';
	if ( SDP::SUSE::compareSupportconfig($TEST_VERSION) >= 0 ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Supportconfig version meets minimum requirement");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Supportconfig version NOT sufficient, $TEST_VERSION or higher needed");
	}

=item Input

$TEST_VERSION (The version string to which supportconfig's version is compared.)

=item Output

-1 if supportconfig_version < $TEST_VERSION

0 if supportconfig_version == $TEST_VERSION

1 if supportconfig_version > $TEST_VERSION

=item Requires

None

=back

=cut

sub compareSupportconfig {
	printDebug("> compareSupportconfig", "BEGIN");
	my $COMPARE_TO       = $_[0];
	my %SC_INFO          = getSCInfo();

	SDP::Core::printDebug("COMPARING", $SC_INFO{'version'} . " to " . $COMPARE_TO);
	my $RESULT           = SDP::Core::compareVersions($SC_INFO{'version'}, $COMPARE_TO);

	SDP::Core::printDebug("< compareSupportconfig", "Result: $RESULT");
	return $RESULT;
}


=begin html

<hr>

=end html

=head2 compareRpm

=over 5

=item Description

Uses SDP::Core::compareVersions to compare $test_version against the installed RPM version. Comparisons are only valid on a single installed RPM; the comparison is skipped if multiple RPMs of the same name are installed. Only the most significant version components are compared. For example, if 2.6.5 is compared with 2.6.16.60-0.23, then only 2.6.5 and 2.6.16 will be used for the comparison. Letters in version strings are compared as separate elements. So 2.6SP3 would be compared as 2.6.SP.3. Letters are compared as a string comparison, and are case sensitive.

=item Usage

	my $RPM_NAME = 'autofs';
	my $VERSION_TO_COMPARE = '1.1.2';
	my $RPM_COMPARISON = SDP::SUSE::compareRpm($RPM_NAME, $VERSION_TO_COMPARE);
	if ( $RPM_COMPARISON == 2 ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: RPM $RPM_NAME Not Installed");
	} elsif ( $RPM_COMPARISON > 2 ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Multiple Versions of $RPM_NAME RPM are Installed");
	} else {
		if ( $RPM_COMPARISON < 0 ) {
			SDP::Core::updateStatus(STATUS_WARNING, "The installed $RPM_NAME RPM version is less than version $VERSION_TO_COMPARE");
		} else {
			SDP::Core::updateStatus(STATUS_ERROR, "The installed $RPM_NAME RPM version meets or exceeds version $VERSION_TO_COMPARE");
		}			
	}

=item Input

$rpm_name (The RPM name you are testing)

$test_version (The RPM version string to which the installed RPM version is compared.)

=item Output

-1 if installed_rpm_version < $test_version

0 if installed_rpm_version == $test_version

1 if installed_rpm_version > $test_version

2 if RPM is not installed

3 if Multiple RPM versions exist

=item Requires

None

=back

=cut

sub compareRpm {
	use constant NORPM    => 2;
	use constant MANYRPMS => 3;
	my $RESULT;
	my $RPM_NAME          = $_[0];
	my $COMPARED_TO       = $_[1];
	my @RPM_INFO          = getRpmInfo($RPM_NAME);
	printDebug("> compareRpm", "'$RPM_NAME' 'Installed RPM Version' to '$COMPARED_TO'");

	if ( $#RPM_INFO < 0 ) {
		printDebug("  compareRpm ERROR", "RPM $RPM_NAME Not Installed");
		$RESULT = NORPM;
	} elsif ( $#RPM_INFO > 0 ) {
		printDebug("  compareRpm ERROR", "Multiple RPMs Installed: $RPM_NAME");
		$RESULT = MANYRPMS;
	} else {
		my $VERSTR = $RPM_INFO[0]{'version'};
		if ( $VERSTR ne $COMPARED_TO ) {
			my @FIRST = SDP::Core::normalizeVersionString($VERSTR);
			my @LAST = SDP::Core::normalizeVersionString($COMPARED_TO);

			if ( $#LAST > $#FIRST ) {
				my $I;
				for ( $I = $#FIRST; $I < $#LAST; $I++ ) {
					push(@FIRST, 0);
				} 
				$VERSTR = join('.', @FIRST);
				printDebug("  compareRpm EXCEPTION", "$RPM_INFO[0]{'version'} modified as $VERSTR");
			}
		}
		printDebug("  compareRpm COMPARING", $VERSTR . " to " . $COMPARED_TO);
		$RESULT = compareVersions($VERSTR, $COMPARED_TO);
	}

	printDebug("< compareRpm", "Result: $RESULT");
	return $RESULT;
}

##############################################################################

=head1 FUNCTIONS: RPM Packages

=begin html

<hr>

=end html

=head2 getRpmInfo

=over 5

=item Description

Returns an array of hashes containing RPM information. If the RPM is not installed, then @RPM_INFO is not set.

=item Usage

	my $RPM_NAME = 'kernel-xen';
	my @RPM_INFO = SDP::SUSE::getRpmInfo($RPM_NAME);
	if ( $#RPM_INFO < 0 ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: RPM $RPM_NAME Not Installed");
	} elsif ( $#RPM_INFO > 0 ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Multiple $RPM_NAME RPMs Installed");
	} else {
		SDP::Core::updateStatus(STATUS_SUCCESS, "RPM $RPM_INFO[0]{'name'}-$RPM_INFO[0]{'version'} installed on $RPM_INFO[0]{'installed'}");
	}

=item Input

$rpm_name

=item Output

@RPM_INFO (An array of hashes containing RPM information)

=item Requires

None

=item RPM Hash Keys

name, version, vendor, installed

=back

=cut

sub getRpmInfo {
	my $RPM_NAME = $_[0];
	printDebug("> getRpmInfo", "'$RPM_NAME'");
	my $FILE_OPEN = "rpm.txt"; #The rpm information file
	my @RPM_INFO = ();
	my @LINE_DATA = ();
	my $i = 0;

	# get vendor and version
	my $HEADER_LINES  = 2;
	my @CONTENT       = ();
	my $SECTION       = '{NAME}';
	my $LINE          = 0;
	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			$LINE++;
			next if ( $LINE < $HEADER_LINES );
			if ( /^$RPM_NAME\s/ ) {
				SDP::Core::printDebug("  getRpmInfo LINE $LINE", $_);
				@LINE_DATA = split(/\s+/, $_);
				$RPM_INFO[$i]{'name'} = $RPM_NAME;
				$RPM_INFO[$i]{'version'} = pop @LINE_DATA; # the version is the last element
				shift @LINE_DATA; # remove the package name
				$RPM_INFO[$i]{'vendor'} = "@LINE_DATA";
				$i++;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}

	# get installation time
	if ( $#RPM_INFO >= 0 ) {
		$HEADER_LINES  = 2;
		@CONTENT       = ();
		$SECTION       = 'rpm -qa --last';
		$LINE          = 0;
		my $RPMVER     = "";
		if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
			foreach $_ (@CONTENT) {
				$LINE++;
				next if ( $LINE < $HEADER_LINES );
				for ( $i = 0; $i <= $#RPM_INFO; $i++ ) {
					$RPMVER = $RPM_INFO[$i]{'name'} . "-" . $RPM_INFO[$i]{'version'};
					if ( /^$RPMVER/ ) {
						SDP::Core::printDebug("  getRpmInfo LINE $LINE", $_);
						@LINE_DATA = split(/\s+/, $_);
						shift @LINE_DATA;
						$RPM_INFO[$i]{'installed'} = join($", @LINE_DATA);
					}
				}
			}
		} else {
			SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
		}
	} else {
		SDP::Core::printDebug("  getRpmInfo RPM", "Not Installed: $RPM_NAME");
	}

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		my $role;
		
		foreach $i (0 .. $#RPM_INFO) {
			print("RPM_INFO $i = ");
			for $role ( keys %{ $RPM_INFO[$i] } ) {
				print("'$role' => '$RPM_INFO[$i]{$role}'  ");
			}
			print("\n");
		}
	}
	my $RPMS_FOUND = $#RPM_INFO + 1;
	printDebug("< getRpmInfo", "RPMs Found: $RPMS_FOUND");
	return @RPM_INFO;
}

=begin html

<hr>

=end html

=head2 packageInstalled

=over 5

=item Description

Confirms $PKG_NAME is installed on the system

=item Usage

	my $PKG_NAME = 'supportutils';
	if ( SDP::SUSE::packageInstalled($PKG_NAME) ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Package Installed: $PKG_NAME");
	} else {
		SDP::Core::updateStatus(STATUS_CRITICAL, "Package NOT Installed: $PKG_NAME");
	}

=item Input

$pacakge_name (The package name to validate)

=item Output

1 if Package is installed

0 if Package is NOT installed

=item Requires

None

=back

=cut

sub packageInstalled {
	my $PKG_NAME   = $_[0];
	SDP::Core::printDebug('> packageInstalled', "'$PKG_NAME'");
	@RPM_INFO          = SDP::SUSE::getRpmInfo($PKG_NAME);
	$RCODE             = 1; # Assume it's installed

	if ( $#RPM_INFO < 0 ) {
		SDP::Core::printDebug('  packageInstalled RPM', "Not Installed: $PKG_NAME");
		$RCODE = 0;
	} else {
		SDP::Core::printDebug('  packageInstalled RPM', "Installed: $PKG_NAME");
	}
	SDP::Core::printDebug("< packageInstalled", "Return: $RCODE, '$PKG_NAME'");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 haeEnabled

=over 5

=item Description

Checks for a corosync.conf to show HAE is enabled.

=item Usage

	if ( SDP::SUSE::haeEnabled() ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "HAE Enabled");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "HAE Disabled");
	}

=item Input

None

=item Output

0 if HAE is disabled, corosync.conf missing

1 if HAE is enabled, corosync.conf found

=item Requires

None

=back

=cut

sub haeEnabled {
	SDP::Core::printDebug('> haeEnabled', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'ha.txt';
	my @CONTENT = ();

	if ( SDP::Core::listSections($FILE_OPEN, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( m/^\s*$/ ); # Skip blank lines
			if ( /corosync.conf/ ) {
				SDP::Core::printDebug("PROCESSING", $_);
				if ( /not found/i ) {
					$RCODE = 0;
				} else {
					$RCODE = 1;
				}
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: haeEnabled(): No sections found in $FILE_OPEN");
	}
	SDP::Core::printDebug("< haeEnabled", "Returns: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 packageVerify

=over 5

=item Description

Checks if the named package passed it's RPM validation check.

=item Usage

	my $FILE_OPEN = 'fs-autofs.txt';
	my $PKG_NAME = 'autofs';
	my @EXCEPTION_LIST = ();
	if ( SDP::SUSE::packageVerify($FILE_OPEN, $PKG_NAME, \@EXCEPTION_LIST) > 1 ) {
		SDP::Core::updateStatus(STATUS_CRITICAL, "Failed RPM Validation: $PKG_NAME");
	} else {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Passed RPM Validation: $PKG_NAME");
	}

=item Input

$FILE_OPEN (The file in which the rpm -V was executed.)

$PKG_NAME (The package name to validate)

$EXCEPTION_LIST (An address to an array of files or directories to exclude from the check. OPTIONAL)

=item Output

0 if Package is valid, no differences found

1 if Package is valid, or only docs or configuration files have been modified

2 if Package is not valid, non-doc or non-configuration files have been modified

3 if Package is not valid, binaries or library files have been modified

4 if Package is not valid, unknown reason

=item Requires

None

=back

=cut

sub packageVerify {
	my $PKG_NAME = $_[1];
	printDebug('> packageVerify', "'$PKG_NAME'");
	my $RCODE         = 4;  # assume the package is NOT valid
	my $FILE_SERVICE  = $_[0];
	my $EXCEPTION_LIST = $_[2];
	my $LINE          = 0;
	my $SECTION       = "rpm -V $PKG_NAME";
	my @CONTENT       = ();
	my @LINE_DATA     = ();
	my $PKG_CRIT       = 0;
	my $PKG_WARN       = 0;
	my $PKG_MODF       = 0;

	if ( SDP::Core::getSection($FILE_SERVICE, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			$LINE++;
			next if m/^# /;
			next if m/^\s*$/;
			@LINE_DATA = split(/\s+/, $_);
			my $TEST_FILE = pop(@LINE_DATA);
			my $THIS_EXCEPTION;
			my $ABORT = 0;
			foreach $THIS_EXCEPTION (@$EXCEPTION_LIST) {
				if ( "$THIS_EXCEPTION" eq "$TEST_FILE" ) {
					SDP::Core::printDebug("EXCEPTION:", $TEST_FILE);
					$ABORT = 1;
					last;
				}
			}
			next if ( $ABORT );
			if ( $#LINE_DATA < 2 ) {	# a non conf or doc file has been modified
				if ( $LINE_DATA[0] =~ m/[S|M|5|D|L|U|G]/i ) { # the M catches mode and missing
					if ( $LINE_DATA[$#LINE_DATA] =~ m/\.log$|\.conf$/ ) {
						$PKG_MODF++;
						SDP::Core::printDebug("LINE $LINE Modified: $PKG_MODF", $_);
					} else {
						if ( $LINE_DATA[$#LINE_DATA] =~ m/\/bin|\/lib/i ) {
							$PKG_CRIT++;
							SDP::Core::printDebug("LINE $LINE Critical: $PKG_CRIT", $_);
						} else {
							$PKG_WARN++;
							SDP::Core::printDebug("LINE $LINE Warning: $PKG_WARN", $_);
						}
					}
				} else {
					$PKG_MODF++;
					SDP::Core::printDebug("LINE $LINE Modified: $PKG_MODF", $_);
				}
			} else {
				$PKG_MODF++;
				SDP::Core::printDebug("LINE $LINE Modified: $PKG_MODF", $_);
			}
		}
		my $PKG_TOTAL = $PKG_CRIT + $PKG_WARN + $PKG_MODF;
		if ( $PKG_TOTAL == 0 ) {
			$RCODE = 0;
		} else {
			if ( $PKG_CRIT > 0 ) {
				$RCODE = 3;
			} elsif ($PKG_WARN > 0 ) {
				$RCODE = 2;
			} elsif ($PKG_MODF > 0 ) {
				$RCODE = 1;
			}
		}
		SDP::Core::printDebug('RPM VALIDATION', "Package: $PKG_NAME; Critical: $PKG_CRIT, Warning: $PKG_WARN, Modified: $PKG_MODF");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_SERVICE");
		$RCODE = 0;
	}
	printDebug("< packageVerify", "Returned: $RCODE, $PKG_NAME");
	return $RCODE;
}


=begin html

<hr>

=end html

=head2 securityPackageCheck

=over 5

=item Description

A function specific to checking packages in a Security Advisory type format. The function will trigger a script exit if the @rpms_to_check are not installed. It is assumed that the @rpms_to_check are different packages with the same $fixed_rpm_version for each. For example, @rpms_to_check might be cups and cups-devel, but the fix is version 1.1.0 for each (cups-1.1.0 and cups-devel-1.1.0). This function is not intended to check two different versions on the same server. For example, java-1_4_2 and java-1_5_0 on the same server should not be checked with this function because securityPackageCheck will abort if it finds any occurance of a package not installed. 

=item Usage

SDP::SUSE::securityPackageCheck($title, $advisory_number, $advisory_description, \@rpms_to_check, $fixed_rpm_version);

=item Input

$title (Short one or two word title of the Advisory; ie Kerberos, CUPS or IBM Java)

$advisory_number (The security advisory "Announcement ID," ie SUSE-SA:2009:007)

$advisory_description (The security advisory "Vulnerability Type," ie "Local privilege escalation")

\@rpms_to_check (An array of rpm packages with the same version that are affected by the security advisory; ie cups, cups-libs, cups-devel)

$fixed_rpm_version (The version of the @rpms_to_check in which the security vulnerabilty has been fixed, ie 1.1.23-40.38)

=item Output

1 if Package is confirmed to be installed and fixed

0 if Package cannot be confirmed as installed and fixed

@PATTERN_RESULTS (Adds the CVE key value pair)

=item Requires

None

=back

=cut

sub securityPackageCheck {
	my $CVE_CHECK           = $_[0];
	my $SECURITY_ADVISORY   = $_[1];
	my $SECURITY_TYPE       = $_[2];
	my $RPM_PKGS_REF        = $_[3];
	my @RPM_PKGS            = @$RPM_PKGS_REF;
	my $RPM_FIXED           = $_[4];
	SDP::Core::printDebug('> securityPackageCheck', "$CVE_CHECK, $SECURITY_ADVISORY, $SECURITY_TYPE, $#RPM_PKGS, $RPM_FIXED");
	my $RPM_FOUND           = 0;
	my $RPM_PKG             = '';
	my $RPM_COMPARISON;
	my $RCODE               = 0; #Cannot confirm the package is installed and fixed

	SDP::Core::setStatus(STATUS_SUCCESS, "$CVE_CHECK Security Advisory: $SECURITY_TYPE vulnerability AVOIDED ($SECURITY_ADVISORY)");
	if ( $#RPM_PKGS >= 0 ) {
		foreach my $RPM_PKG (@RPM_PKGS) {
			$RPM_COMPARISON   = SDP::SUSE::compareRpm($RPM_PKG, $RPM_FIXED);
			if      ( $RPM_COMPARISON == 3 ) { # More than one $RPM_PKG package is installed, can't proceed
				SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $CVE_CHECK Security Advisory $RPM_PKG: More than one version installed");
			} elsif ( $RPM_COMPARISON == 2 ) { # The $RPM_PKG is not installed at all
				if ( $#RPM_PKGS >= 0 ) {
					SDP::Core::updateStatus(STATUS_ERROR, "IGNORING $RPM_PKG: Package not installed");
				} else {
					SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $CVE_CHECK Security Advisory: Package not installed, $RPM_PKG");
				}
			} else {
				$RPM_FOUND++;
				if ( $RPM_COMPARISON < 0 ) {
					SDP::Core::updateStatus(STATUS_CRITICAL, "$CVE_CHECK $SECURITY_TYPE vulnerability, update system to apply: $RPM_PKG-$RPM_FIXED ($SECURITY_ADVISORY)");
				} else {
					SDP::Core::updateStatus(STATUS_ERROR, "Security: $RPM_PKG, $SECURITY_TYPE vulnerability AVOIDED ($SECURITY_ADVISORY)");
					$RCODE = 1;
				}
			}
		}
	}

	if ( ! $RPM_FOUND ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $CVE_CHECK Security Advisory: No package(s) installed");
	}

	SDP::Core::printDebug("< securityPackageCheck", "Returned: $RCODE, $CVE_CHECK");
	return $RCODE;

}

=begin html

<hr>

=end html

=head2 securitySeverityPackageCheck

=over 5

=item Description

A function specific to checking packages in a Security Advisory type format. The function will trigger a script exit if the @rpms_to_check are not installed. It is assumed that the @rpms_to_check are different packages with the same $fixed_rpm_version for each. For example, @rpms_to_check might be cups and cups-devel, but the fix is version 1.1.0 for each (cups-1.1.0 and cups-devel-1.1.0). This function is not intended to check two different versions on the same server. For example, java-1_4_2 and java-1_5_0 on the same server should not be checked with this function because securityPackageCheck will abort if it finds any occurance of a package not installed. 

=item Usage

SDP::SUSE::securitySeverityPackageCheck($TITLE, $SEVERITY, $VULNERABILITY_TYPE, \@RPMS_TO_CHECK, $FIXED_RPM_VERSION);

=item Input

$PRODUCT (Short one or two word title of the Advisory; ie Kerberos, CUPS or IBM Java)

$SEVERITY (The CVSS v2 Base Score number)

$VULNERABILITY_TYPE (The security advisory "Vulnerability Type," ie "Local privilege escalation")

\@RPMS_TO_CHECK (An array of rpm packages with the same version that are affected by the security advisory; ie cups, cups-libs, cups-devel)

$FIXED_RPM_VERSION (The version of the @rpms_to_check in which the security vulnerabilty has been fixed, ie 1.1.23-40.38)

=item Output

1 if Package is confirmed to be installed and fixed

0 if Package cannot be confirmed as installed and fixed

@PATTERN_RESULTS (Adds the CVE key value pair)

=item Requires

None

=back

=cut

sub securitySeverityPackageCheck {
	my $PRODUCT = $_[0];
	my $SEVERITY = $_[1];
	my $VULNERABILITY_TYPE = $_[2];
	my $RPM_PKGS_REF = $_[3];
	my @RPM_PKGS = @$RPM_PKGS_REF;
	my $RPM_FIXED = $_[4];
	SDP::Core::printDebug('> securitySeverityPackageCheck', "$PRODUCT, $SEVERITY, $VULNERABILITY_TYPE, $#RPM_PKGS, $RPM_FIXED");
	my $RPM_FOUND = 0;
	my $RPM_PKG = '';
	my $RPM_COMPARISON;
	my $RCODE = 0; #Cannot confirm the package is installed and fixed

	SDP::Core::setStatus(STATUS_SUCCESS, "Level $SEVERITY $PRODUCT $VULNERABILITY_TYPE vulnerability AVOIDED");
	if ( $#RPM_PKGS >= 0 ) {
		foreach my $RPM_PKG (@RPM_PKGS) {
			$RPM_COMPARISON   = SDP::SUSE::compareRpm($RPM_PKG, $RPM_FIXED);
			if      ( $RPM_COMPARISON == 3 ) { # More than one $RPM_PKG package is installed, can't proceed
				SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $CVE_CHECK Security Advisory $RPM_PKG: More than one version installed");
			} elsif ( $RPM_COMPARISON == 2 ) { # The $RPM_PKG is not installed at all
				if ( $#RPM_PKGS >= 0 ) {
					SDP::Core::updateStatus(STATUS_ERROR, "IGNORING $RPM_PKG: Package not installed");
				} else {
					SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $PRODUCT Security Advisory: Package not installed, $RPM_PKG");
				}
			} else {
				$RPM_FOUND++;
				if ( $RPM_COMPARISON < 0 ) {
					SDP::Core::updateStatus(STATUS_CRITICAL, "Level $SEVERITY $PRODUCT $VULNERABILITY_TYPE vulnerability, update system to apply: $RPM_PKG-$RPM_FIXED");
				} else {
					SDP::Core::updateStatus(STATUS_ERROR, "Level $SEVERITY $PRODUCT $VULNERABILITY_TYPE vulnerability AVOIDED");
					$RCODE = 1;
				}
			}
		}
	}

	if ( ! $RPM_FOUND ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $PRODUCT Security Advisory: No package(s) installed");
	}

	SDP::Core::printDebug("< securitySeverityPackageCheck", "Returned: $RCODE, $PRODUCT");
	return $RCODE;

}

=begin html

<hr>

=end html

=head2 securityPackageCheckNoError

=over 5

=item Description

A function specific to checking packages in a Security Advisory type format. No script exists are triggered. SDP::Core::setStatus is not called. If no @rpms_to_check are found, then STATUS_PARTIAL is returned. It is assumed that the @rpms_to_check are different packages with the same $fixed_rpm_version for each. For example, @rpms_to_check might be cups and cups-devel, but the fix is version 1.1.0 for each (cups-1.1.0 and cups-devel-1.1.0).

=item Usage

SDP::SUSE::securityPackageCheckNoError($title, $advisory_number, $advisory_description, \@rpms_to_check, $fixed_rpm_version);

=item Input

$title (Short one or two word title of the Advisory; ie Kerberos, CUPS or IBM Java)

$advisory_number (The security advisory "Announcement ID," ie SUSE-SA:2009:007)

$advisory_description (The security advisory "Vulnerability Type," ie "Local privilege escalation")

\@rpms_to_check (An array of rpm packages with the same version that are affected by the security advisory; ie cups, cups-libs, cups-devel)

$fixed_rpm_version (The version of the @rpms_to_check in which the security vulnerabilty has been fixed, ie 1.1.23-40.38)

=item Output

1 if Package(s) is confirmed to be installed and fixed

0 if Package(s) cannot be confirmed as installed and fixed

@PATTERN_RESULTS (Adds the PKG key value pair)

=item Requires

SDP::Core::setStatus()

=back

=cut

sub securityPackageCheckNoError {
	my $CVE_CHECK           = $_[0];
	my $SECURITY_ADVISORY   = $_[1];
	my $SECURITY_TYPE       = $_[2];
	my $RPM_PKGS_REF        = $_[3];
	my @RPM_PKGS            = @$RPM_PKGS_REF;
	my $RPM_FIXED           = $_[4];
	SDP::Core::printDebug('> securityPackageCheckNoError', "$CVE_CHECK, $SECURITY_ADVISORY, $SECURITY_TYPE, $#RPM_PKGS, $RPM_FIXED");
	my $RPM_PKG             = '';
	my $RPM_COMPARISON;
	my $RCODE               = 0; #Cannot confirm the package is installed and fixed

	if ( $#RPM_PKGS >= 0 ) {
		foreach my $RPM_PKG (@RPM_PKGS) {
			$RPM_COMPARISON   = SDP::SUSE::compareRpm($RPM_PKG, $RPM_FIXED);
			if      ( $RPM_COMPARISON == 3 ) { # More than one $RPM_PKG package is installed, can't proceed
				SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $CVE_CHECK Security Advisory $RPM_PKG: More than one version installed");
			} elsif ( $RPM_COMPARISON == 2 ) { # The $RPM_PKG is not installed at all
				SDP::Core::updateStatus(STATUS_PARTIAL, "$CVE_CHECK Security Advisory: Package not installed, $RPM_PKG");
			} else {
				$RCODE = 1;
				if ( $RPM_COMPARISON < 0 ) {
					SDP::Core::updateStatus(STATUS_CRITICAL, "$CVE_CHECK $SECURITY_TYPE vulnerability, update system to apply: $RPM_PKG-$RPM_FIXED ($SECURITY_ADVISORY)");
				} else {
					SDP::Core::updateStatus(STATUS_ERROR, "Security: $RPM_PKG, $SECURITY_TYPE vulnerability AVOIDED ($SECURITY_ADVISORY)");
				}
			}
		}
	}
	SDP::Core::printDebug("< securityPackageCheckNoError", "Returned: $RCODE, $CVE_CHECK");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 securityAnnouncementPackageCheck

=over 5

=item Description

Goes here...

=item Usage

SDP::SUSE::securityAnnouncementPackageCheck($NAME, $SEVERITY, $TAG, %PACKAGES);

=item Input

$NAME (The product name being checked, like PostgreSQL, Acroread, or Firefix)

$MAIN (The main rpm package name that must be installed to indicate $NAME is found OR leave empty to check all packages.)

$SEVERITY (Critical, Important, etc. A single word shown in the Rating field of the security announcement)

$TAG (The security announcement ID, like SUSE-SU-2013:0633-1)

%PACKAGES (A hash of packages and their version numbers in which this issue is fixed to be checked. The key is the package name and the value is the fixed version string)

=item Output

1 if Package(s) is confirmed to be installed and fixed

0 if Package(s) cannot be confirmed as installed and fixed

=back

=cut

sub securityAnnouncementPackageCheck {
	my $NAME = shift;
	my $MAIN = shift;
	my $SEVERITY = shift;
	my $TAG = shift;
	SDP::Core::printDebug('> securityAnnouncementPackageCheck');
	my %PACKAGES = %{+shift};
	my @FAILED = ();
	my $INSTALLED = 0;
	my $RCODE = 0;
	if ( "$MAIN" eq '' || SDP::SUSE::packageInstalled($MAIN) ) {
		while ( my ($CHECK_PKG, $FIXED_VER) = each(%PACKAGES) ) {
			my $RPM_COMPARISON = SDP::SUSE::compareRpm("$CHECK_PKG", "$FIXED_VER");
			if ( $RPM_COMPARISON > 2 ) { # More than one $CHECK_PKG package is installed, can't proceed
				SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $NAME Security Announcement: More than one version installed");
			} elsif ( $RPM_COMPARISON == 2 ) { # The $CHECK_PKG is not installed at all
				SDP::Core::printDebug('  securityAnnouncementPackageCheck NOT INSTALLED', "$CHECK_PKG-$FIXED_VER");
				SDP::Core::updateStatus(STATUS_PARTIAL, "Package not installed, $CHECK_PKG");
			} else {
				$INSTALLED++;
				if ( $RPM_COMPARISON < 0 ) {
					SDP::Core::printDebug('  securityAnnouncementPackageCheck FAILED', "$CHECK_PKG-$FIXED_VER");
					$RCODE = 1;
					push(@FAILED, "$CHECK_PKG-$FIXED_VER");
				} else {
					SDP::Core::printDebug('  securityAnnouncementPackageCheck PASSED', "$CHECK_PKG-$FIXED_VER");
				}
			}
		}
		my $FAILED_PACKAGES = scalar @FAILED;
		if ( $INSTALLED > 0 ) {
			if ( $FAILED_PACKAGES ) {
				SDP::Core::updateStatus(STATUS_CRITICAL, "$SEVERITY $NAME Security Announcement $TAG, update system to apply: @FAILED");
			} else {
				SDP::Core::updateStatus(STATUS_IGNORE, "$SEVERITY $NAME Security Announcement $TAG AVOIDED");
			}
		} else {
			SDP::Core::updateStatus(STATUS_ERROR, "ERROR: No affected packages installed, skipping security test");
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: $NAME Not Installed, Skipping Security Test");
	}
	SDP::Core::printDebug('< securityAnnouncementPackageCheck', "Returns: $RCODE");
}


=begin html

<hr>

=end html

=head2 securitySeverityPackageCheckNoError

=over 5

=item Description

A function specific to checking packages in a Security Advisory type format. No script exists are triggered. SDP::Core::setStatus is not called. If no @rpms_to_check are found, then STATUS_PARTIAL is returned. It is assumed that the @rpms_to_check are different packages with the same $fixed_rpm_version for each. For example, @rpms_to_check might be cups and cups-devel, but the fix is version 1.1.0 for each (cups-1.1.0 and cups-devel-1.1.0).

=item Usage

SDP::SUSE::securitySeverityPackageCheckNoError($title, $advisory_severity, $advisory_description, \@rpms_to_check, $fixed_rpm_version);

=item Input

$title (Short one or two word title of the Advisory; ie Kerberos, CUPS or IBM Java)

$advisory_severity (The CVSS v2 Base Score Number)

$advisory_description (The security advisory "Vulnerability Type," ie "Local privilege escalation")

\@rpms_to_check (An array of rpm packages with the same version that are affected by the security advisory; ie cups, cups-libs, cups-devel)

$fixed_rpm_version (The version of the @rpms_to_check in which the security vulnerabilty has been fixed, ie 1.1.23-40.38)

=item Output

1 if Package(s) is confirmed to be installed and fixed

0 if Package(s) cannot be confirmed as installed and fixed

@PATTERN_RESULTS (Adds the PKG key value pair)

=item Requires

SDP::Core::setStatus()

=back

=cut

sub securitySeverityPackageCheckNoError {
	my $CVE_CHECK = $_[0];
	my $ADVISORY_SEVERITY = $_[1];
	my $SECURITY_TYPE = $_[2];
	my $RPM_PKGS_REF = $_[3];
	my @RPM_PKGS = @$RPM_PKGS_REF;
	my $RPM_FIXED = $_[4];
	SDP::Core::printDebug('> securitySeverityPackageCheckNoError', "$CVE_CHECK, $ADVISORY_SEVERITY, $SECURITY_TYPE, $#RPM_PKGS, $RPM_FIXED");
	my $RPM_PKG = '';
	my $RPM_COMPARISON;
	my $RCODE = 0; #Cannot confirm the package is installed and fixed

	if ( $#RPM_PKGS >= 0 ) {
		foreach my $RPM_PKG (@RPM_PKGS) {
			$RPM_COMPARISON   = SDP::SUSE::compareRpm($RPM_PKG, $RPM_FIXED);
			if      ( $RPM_COMPARISON == 3 ) { # More than one $RPM_PKG package is installed, can't proceed
				SDP::Core::updateStatus(STATUS_ERROR, "ABORTED: $CVE_CHECK Security Advisory $RPM_PKG: More than one version installed");
			} elsif ( $RPM_COMPARISON == 2 ) { # The $RPM_PKG is not installed at all
				SDP::Core::updateStatus(STATUS_PARTIAL, "Package not installed, $RPM_PKG");
			} else {
				$RCODE = 1;
				if ( $RPM_COMPARISON < 0 ) {
					SDP::Core::updateStatus(STATUS_CRITICAL, "Level $ADVISORY_SEVERITY $CVE_CHECK $SECURITY_TYPE vulnerability, update system to apply: $RPM_PKG-$RPM_FIXED");
				} else {
					SDP::Core::updateStatus(STATUS_ERROR, "Level $ADVISORY_SEVERITY $CVE_CHECK $SECURITY_TYPE vulnerability AVOIDED");
				}
			}
		}
	}
	SDP::Core::printDebug("< securitySeverityPackageCheckNoError", "Returned: $RCODE, $CVE_CHECK");
	return $RCODE;
}


=begin html

<hr>

=end html

=head2 securityKernelCheck

=over 5

=item Description

A function specific to checking kernel packages in a Security Advisory type format. The function returns a 1 if the system kernel is outside the scope specified.

=item Usage

SDP::SUSE::securityKernelCheck($kernelMin, $kernelMax, $kernelFix, $advisoryNumber, $advisoryDescription);

=item Input

$kernelMin (The minimum kernel version in which the vulnerability is found. Provides the beginning scope in which to look.)

$kernelMax (The maximum kernel version in which the vulnerability is found. Provides the ending scope in which to look.)

$kernelFix (The kernel version in which the vulnerability is fixed.)

$advisoryNumber (The security advisory "Announcement ID," ie SUSE-SA:2009:007)

$advisoryDescription (The security advisory "Vulnerability Type," ie "Local privilege escalation")

=item Output

0 if $kernelMin <= System Kernel < $kernelMax

1 if System Kernel is outside $kernelMin/$kernelMax scope

@PATTERN_RESULTS (Adds the CVE key value pair)

=item Requires

None

=back

=cut

sub securityKernelCheck {
	my $kernelMin           = $_[0];
	my $kernelMax           = $_[1];
	my $kernelFix           = $_[2];
	my $advisoryNumber      = $_[3];
	my $adivsoryDescription = $_[4];
	SDP::Core::printDebug('> securityKernelCheck', "$kernelMin, $kernelMax, $kernelFix, $advisoryNumber, $adivsoryDescription");
	my $RCODE               = 0; #The system kernel is within check scope

	SDP::Core::setStatus(STATUS_SUCCESS, "Kernel Security Advisory: $adivsoryDescription vulnerability AVOIDED ($advisoryNumber)");
	if ( SDP::SUSE::compareKernel($kernelMin) >= 0 && SDP::SUSE::compareKernel($kernelMax) < 0 ) {
		if ( SDP::SUSE::compareKernel($kernelFix) < 0 ) {
			SDP::Core::updateStatus(STATUS_CRITICAL, "Kernel $adivsoryDescription, update system to apply kernel: $kernelFix ($advisoryNumber)");
		} else {
			SDP::Core::updateStatus(STATUS_ERROR, "Kernel Security: $adivsoryDescription vulnerability AVOIDED ($advisoryNumber)");
		}
	} else {
		$RCODE = 1;
	}

	SDP::Core::printDebug("< securityKernelCheck", "Returned: $RCODE, $advisoryNumber");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 securitySeverityKernelCheck

=over 5

=item Description

A function specific to checking kernel packages in a Security Advisory type format. The function returns a 1 if the system kernel is outside the scope specified.

=item Usage

SDP::SUSE::securitySeverityKernelCheck($kernelMin, $kernelMax, $kernelFix, $severityValue, $advisoryDescription);

=item Input

$kernelMin (The minimum kernel version in which the vulnerability is found. Provides the beginning scope in which to look.)

$kernelMax (The maximum kernel version in which the vulnerability is found. Provides the ending scope in which to look.)

$kernelFix (The kernel version in which the vulnerability is fixed.)

$severityValue (The CVSS v2 Base Score Number)

$advisoryDescription (The security advisory "Vulnerability Type," ie "Local privilege escalation")

=item Output

0 if $kernelMin <= System Kernel < $kernelMax

1 if System Kernel is outside $kernelMin/$kernelMax scope

@PATTERN_RESULTS (Adds the CVE key value pair)

=item Requires

None

=back

=cut

sub securitySeverityKernelCheck {
	my $kernelMin           = $_[0];
	my $kernelMax           = $_[1];
	my $kernelFix           = $_[2];
	my $severityValue       = $_[3];
	my $adivsoryDescription = $_[4];
	SDP::Core::printDebug('> securitySeverityKernelCheck', "$kernelMin, $kernelMax, $kernelFix, $severityValue, $adivsoryDescription");
	my $RCODE               = 0; #The system kernel is within check scope

	SDP::Core::setStatus(STATUS_SUCCESS, "Level $severityValue Kernel $adivsoryDescription vulnerability AVOIDED");
	if ( SDP::SUSE::compareKernel($kernelMin) >= 0 && SDP::SUSE::compareKernel($kernelMax) < 0 ) {
		if ( SDP::SUSE::compareKernel($kernelFix) < 0 ) {
			SDP::Core::updateStatus(STATUS_CRITICAL, "Level $severityValue Kernel $adivsoryDescription vulnerability, update system to apply kernel: $kernelFix");
		} else {
			SDP::Core::updateStatus(STATUS_ERROR, "Level $severityValue Kernel $adivsoryDescription vulnerability AVOIDED");
		}
	} else {
		$RCODE = 1;
	}

	SDP::Core::printDebug("< securitySeverityKernelCheck", "Returned: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 securitySeverityKernelAnnouncement

=over 5

=item Description

A function specific to checking kernel packages in a Security announcement type format. The function returns a 1 if the system kernel is outside the scope specified.

=item Usage

SDP::SUSE::securitySeverityKernelAnnouncement($kernelMin, $kernelMax, $kernelFix, $severityValue, $advisoryID);

=item Input

$kernelMin (The minimum kernel version in which the vulnerability is found. Provides the beginning scope in which to look.)

$kernelMax (The maximum kernel version in which the vulnerability is found. Provides the ending scope in which to look.)

$kernelFix (The kernel version in which the vulnerability is fixed.)

$severityValue (A severity string like "Important")

$announcementID (The security announcement ID, like "SUSE-SU-2012:0153-2")

=item Output

0 if $kernelMin <= System Kernel < $kernelMax

1 if System Kernel is outside $kernelMin/$kernelMax scope

@PATTERN_RESULTS (Adds the CVE key value pair)

=item Requires

None

=back

=cut

sub securitySeverityKernelAnnouncement {
	my $kernelMin           = $_[0];
	my $kernelMax           = $_[1];
	my $kernelFix           = $_[2];
	my $severityValue       = $_[3];
	my $announcementID      = $_[4];
	SDP::Core::printDebug('> securitySeverityKernelAnnouncement', "$kernelMin, $kernelMax, $kernelFix, $severityValue, $announcementID");
	my $RCODE               = 0; #The system kernel is within check scope

	SDP::Core::setStatus(STATUS_SUCCESS, "$severityValue Kernel Security Announcement $announcementID AVOIDED");
	if ( SDP::SUSE::compareKernel($kernelMin) >= 0 && SDP::SUSE::compareKernel($kernelMax) < 0 ) {
		if ( SDP::SUSE::compareKernel($kernelFix) < 0 ) {
			SDP::Core::updateStatus(STATUS_CRITICAL, "$severityValue Kernel Security Announcement $announcementID, update system to apply kernel: $kernelFix");
		} else {
			SDP::Core::updateStatus(STATUS_ERROR, "$severityValue Kernel Security Announcement $announcementID AVOIDED");
		}
	} else {
		$RCODE = 1;
	}

	SDP::Core::printDebug("< securitySeverityKernelAnnouncement", "Returned: $RCODE");
	return $RCODE;
}


##############################################################################

=head1 FUNCTIONS: General

=begin html

<hr>

=end html

=head2 serviceBootstate

=over 5

=item Description

Checks if the daemon, boot or xinetd service is turned on at boot. 

=item Usage

	my $service_name = 'autofs';
	if ( SDP::SUSE::serviceBootstate($service_name) ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Turned on at boot: $service_name");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Turned off at boot: $service_name");
	}

=item Input

$service_name (The daemon or service to check)

=item Output

1 if Service is turned on at boot

0 if Service is turned off at boot

=item Requires

None

=back

=cut

sub serviceBootstate {
	my $SERVICE_NAME  = $_[0];
	SDP::Core::printDebug('> serviceBootstate', "$SERVICE_NAME");
	my $LINE          = 0;
	my $FILE_OPEN     = "chkconfig.txt";
	my $SECTION       = "chkconfig --list";
	my @CONTENT       = ();
	my $RCODE         = 0;
	my $SERVICE_FOUND = 0;

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			$LINE++;
			$_ =~ s/\s+//g;
			if ( /^$SERVICE_NAME/ ) {
				SDP::Core::printDebug("  serviceBootstate LINE $LINE", $_); 
				$SERVICE_FOUND = 1;
				if ( /3:on|5:on/ ) {
					$RCODE = 1;
					SDP::Core::printDebug('  serviceBootstate BOOTSTATE', "Service ON at boot in 3 or 5: $SERVICE_NAME");
				} elsif ( /:on/ ) {
					$RCODE = 1;
					SDP::Core::printDebug('  serviceBootstate BOOTSTATE', "Service ON at boot: $SERVICE_NAME");
				} else {
					$RCODE = 0;
					SDP::Core::printDebug('  serviceBootstate BOOTSTATE', "OFF at boot: $SERVICE_NAME");
				}
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	SDP::Core::printDebug("< serviceBootstate", "Returned: $RCODE, $SERVICE_NAME");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 serviceStatus

=over 5

=item Description

Checks if the specified service is currently running

=item Usage

	my $file_name = 'fs-autofs.txt';
	my $service_name = 'autofs';
	if ( SDP::SUSE::serviceStatus($file_name, $service_name) > 0 ) {
		SDP::Core::updateStatus(STATUS_WARNING, "NOT Running: $service_name");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "Running: $service_name");
	}

=item Input

$file_name (The file in which the "$service_name status" command was run)

$service_name (The daemon or service to check)

=item Output

0 if Service is running

1 if Service is unused

2 if Service is down or dead

3 if Service is in an unknown state

=item Requires

None

=back

=cut

sub serviceStatus {
	my $SERVICE_NAME  = $_[1];
	SDP::Core::printDebug('> serviceStatus', "$SERVICE_NAME");
	my $LINE          = 0;
	my $FILE_OPEN     = $_[0];
	my $SECTION       = "$SERVICE_NAME status";
	my @CONTENT       = ();
	my $RCODE         = 3; # Assume unknown state

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (reverse(@CONTENT)) {
			$LINE++;
			if ( /running/i ) {
				SDP::Core::printDebug("  serviceStatus LINE $LINE", $_);
				SDP::Core::printDebug('  serviceStatus STATUS', "Running: $SERVICE_NAME");
				$RCODE = 0;
				last;
			} elsif ( /unused/i ) {
				SDP::Core::printDebug("  serviceStatus LINE $LINE", $_);
				SDP::Core::printDebug('  serviceStatus STATUS', "Unused: $SERVICE_NAME");
				$RCODE = 1;
				last;
			} elsif ( /down|dead/i ) {
				SDP::Core::printDebug("  serviceStatus LINE $LINE", $_);
				SDP::Core::printDebug('  serviceStatus STATUS', "Down/Dead: $SERVICE_NAME");
				$RCODE = 2;
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");	
	}
	SDP::Core::printDebug("< serviceStatus", "Returned: $RCODE, $SERVICE_NAME");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 serviceHealth

=over 5

=item Description

Checks the basic service health; checking RPM validation, run state and chkconfig state. Limited to specific services that have dedicated information files.

=item Usage

	my $FILE_OPEN = "dns.txt";
	my $CHECK_PACKAGE = "bind";
	my $CHECK_SERVICE = "named";
	my @EXCLUDES = ();
	if ( packageInstalled($CHECK_PACKAGE) ) {
		SDP::SUSE::serviceHealth($FILE_OPEN, $CHECK_PACKAGE, $CHECK_SERVICE, \@EXCLUDES);
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "Basic Service Health; Package Not Installed: $CHECK_PACKAGE");
	}

=item Input

$FILE_OPEN (The file that contains the basic service health information)

$CHECK_PACKAGE (The package name to check)

$CHECK_SERVICE (The service name to check)

@EXCLUDES (Array of files to exclude from an RPM validation check)

=item Output

0 if Service is healthy

1 if Service is unhealthy

=item Requires

None

=back

=cut

sub serviceHealth {
	my $FILE_OPEN = $_[0];
	my $CHECK_PACKAGE = $_[1];
	my $CHECK_SERVICE = $_[2];
	my $EXCLUDE = $_[3];
	SDP::Core::printDebug('> serviceHealth', "File: $FILE_OPEN, Package: $CHECK_PACKAGE, Service: $CHECK_SERVICE");
	my $RCODE = 0; # Assume health state
	my $VALIDATE_RPM = 1; # Assume we need to validate
	my $SRV_BOOT = SDP::SUSE::serviceBootstate($CHECK_SERVICE);
	my $SRV_STATUS = SDP::SUSE::serviceStatus($FILE_OPEN, $CHECK_SERVICE);
	if ( $SRV_BOOT == 0 && $SRV_STATUS == 1 ) { # Off and unused
		SDP::Core::updateStatus(STATUS_ERROR, "Basic Service Health; Not in use: $CHECK_SERVICE");
		$VALIDATE_RPM = 0; # Not in use, don't validate
	} elsif ( $SRV_BOOT == 0 && $SRV_STATUS > 1 ) { # Off but dead/down/unknown state
		SDP::Core::updateStatus(STATUS_ERROR, "Basic Service Health; Apparently unused: $CHECK_SERVICE");
	} elsif ( $SRV_BOOT > 0 && $SRV_STATUS > 0 ) { # On but not running
		SDP::Core::updateStatus(STATUS_CRITICAL, "Basic Service Health; Turned on at boot, but not running: $CHECK_SERVICE in $FILE_OPEN");
		$RCODE = 1;
	} elsif ( $SRV_BOOT == 0 && $SRV_STATUS == 0 ) { # Off but running
		SDP::Core::updateStatus(STATUS_WARNING, "Basic Service Health; Turned off at boot, but currently running: $CHECK_SERVICE in $FILE_OPEN");
		$RCODE = 1;
	} elsif ( $SRV_BOOT > 0 && $SRV_STATUS == 0 ) { # On and running
		SDP::Core::updateStatus(STATUS_ERROR, "Basic Service Health; Turned on at boot, and currently running: $CHECK_SERVICE");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "Basic Service Health; Boot State: $SRV_BOOT, Run State: $SRV_STATUS, Service: $CHECK_SERVICE");
	}
	if ( $VALIDATE_RPM ) {
		my $SRV_RPMV = SDP::SUSE::packageVerify($FILE_OPEN, $CHECK_PACKAGE, $EXCLUDE);
		if ( $SRV_RPMV == 0 ) { # No differences found
			SDP::Core::updateStatus(STATUS_ERROR, "Basic Service Health; Passed RPM Validation: $CHECK_PACKAGE");
		} elsif ( $SRV_RPMV == 1 ) { # minor changes
			SDP::Core::updateStatus(STATUS_ERROR, "Basic Service Health; Minor Modifications in RPM Validation: $CHECK_PACKAGE in $FILE_OPEN");
		} elsif ( $SRV_RPMV == 2 ) { # consider changes
			SDP::Core::updateStatus(STATUS_WARNING, "Basic Service Health; Review Changes in RPM Validation: $CHECK_PACKAGE in $FILE_OPEN");
			$RCODE = 1;
		} elsif ( $SRV_RPMV == 3 ) { # A bin or lib failed
			SDP::Core::updateStatus(STATUS_CRITICAL, "Basic Service Health; Binary/Library Failed RPM Validation: $CHECK_PACKAGE in $FILE_OPEN");
		} else {
			SDP::Core::updateStatus(STATUS_WARNING, "Basic Service Health; Review Changes in RPM Validation: $CHECK_PACKAGE in $FILE_OPEN");
			$RCODE = 1;
		}
	}
	SDP::Core::printDebug("< serviceHealth", "Returned: $RCODE, $CHECK_SERVICE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 xenDomU

=over 5

=item Description

Identifies a Xen DomU virtual machine

=item Usage

	if ( SDP::SUSE::xenDomU() ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "The server is a Xen DomU virtual machine");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ABORT: Not a Xen DomU");
	}

=item Input

Non

=item Output

0 if server is NOT a DomU

1 if server is a DomU

=item Requires

None

=back

=cut

sub xenDomU {
	SDP::Core::printDebug('> xenDomU', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'basic-environment.txt';
	my $SECTION = 'Virtualization';
	my @CONTENT = ();
	my @LINE_CONTENT = ();
	my $LINE = 0;

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			$LINE++;
			next if ( /^\s*$/ ); # Skip blank lines
			if ( /^Identity:\s+Virtual Machine.*DomU/i ) {
				SDP::Core::printDebug("  xenDomU LINE $LINE", $_);
				$RCODE = 1;
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_PARTIAL, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	SDP::Core::printDebug("< xenDomU", "Returns: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 xenDom0installed

=over 5

=item Description

Identifies an installed Xen Dom0 virtual machine server

=item Usage

	if ( SDP::SUSE::xenDom0installed() ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "The server has Xen Dom0 installed, buy may or may not be running.");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ABORT: The server does not have Xen Dom0 installed");
	}

=item Input

Non

=item Output

0 if Xen Dom0 is NOT installed

1 if Xen Dom0 is installed

=item Requires

None

=back

=cut

sub xenDom0installed {
	SDP::Core::printDebug('> xenDom0installed', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'boot.txt';
	my $SECTION = 'menu.lst';
	my @CONTENT = ();

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( /^\s*$/ ); # Skip blank lines
			if ( /^\s+kernel.*xen.*gz/i ) {
				$RCODE = 1;
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_PARTIAL, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	SDP::Core::printDebug("< xenDom0installed", "Returns: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 xenDom0running

=over 5

=item Description

Identifies an installed Xen Dom0 virtual machine server

=item Usage

	if ( SDP::SUSE::xenDom0running() ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "The server has Xen Dom0 running.");
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ABORT: The server does not have Xen Dom0 running.");
	}

=item Input

Non

=item Output

0 if Xen Dom0 is NOT running

1 if Xen Dom0 is running

=item Requires

None

=back

=cut

sub xenDom0running {
	SDP::Core::printDebug('> xenDom0running', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'basic-environment.txt';
	my $SECTION = 'Virtualization';
	my @CONTENT = ();
	my @LINE_CONTENT = ();
	my $LINE = 0;

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			$LINE++;
			next if ( /^\s*$/ ); # Skip blank lines
			if ( /^Identity:\s+Virtual Machine.*Dom0/i ) {
				SDP::Core::printDebug("  xenDom0running LINE $LINE", $_);
				$RCODE = 1;
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_PARTIAL, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	SDP::Core::printDebug("< xenDom0running", "Returns: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 getSupportconfigRunDate

=over 5

=item Description

Returns the year, month and day that the supportconfig was run on the server. It also returns the number of days from 1970 Jan 01 to the run date. 

=item Usage

	my (undef, $SC_YEAR, $SC_MONTH, $SC_DAY) = split(/\t/, SDP::SUSE::getSupportconfigRunDate());
	SDP::Core::updateStatus(STATUS_PARTIAL, "Supportconfig run date: $SC_YEAR $SC_MONTH $SC_DAY");

=item Input

None

=item Output

$DAYS

$YEAR

$MONTH

$DAY

=item Requires

None

=back

=cut

sub getSupportconfigRunDate {
	SDP::Core::printDebug('> getSupportconfigRunDate', 'BEGIN');
	my @CONTENT = ();
	my ($DAYS,$YEAR,$MONTH,$DAY) = (0,0,0,0); 

	if (SDP::Core::getSection("basic-environment.txt", "/bin/date", \@CONTENT)) {
		(undef, $MONTH, $DAY, undef, undef, $YEAR) = split (/\s+/, $CONTENT[0]);
		printDebug("  getSupportconfigRunDate Today is ", "$MONTH $DAY, $YEAR");
		$DAYS = SDP::Core::convertDate2Days($MONTH, $DAY, $YEAR);
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find date section in basic-environment.txt");
	}
	SDP::Core::printDebug("< getSupportconfigRunDate", "Days: $DAYS, Year: $YEAR");
	return "$DAYS\t$YEAR\t$MONTH\t$DAY";
}

=begin html

<hr>

=end html

=head2 appCores

=over 5

=item Description

Returns an array of hashes regarding application core file images found on the server.

=item Usage

	my @APP_CORE_INFO = ();
	my $ROLE;

	push(@APP_CORE_INFO, { filename => "/core.5083", month => "Aug", day => "14", year => "2009", days => "1427717.81125", application => "httpd" } );
	if ( SDP::SUSE::appCores(\@APP_CORE_INFO) ) {
		for ( my $I=0; $I<=$#APP_CORE_INFO; $I++) {
			print(" ARRAY $I                        = ");
			for $ROLE ( keys %{ $APP_CORE_INFO[$I] } ) {
				print("'$ROLE' => '$APP_CORE_INFO[$I]->{$ROLE}'  ");
			}
			print("\n");
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "Application core files NOT found");
	}


=item Input

Address to an array

=item Output

Modifies the array reference given

=item Requires

None

=back

=cut

sub appCores {
	SDP::Core::printDebug('> appCores', "@_");
	my $ARRAY_REF = $_[0];
	my $RCODE = 0;
	my $FILE_OPEN = 'crash.txt';
	my ($SC_DAYS, $SC_YEAR) = split(/\t/, getSupportconfigRunDate());


	# get the core file names, dates and age in days
	SDP::Core::printDebug('  appCores [SECTION]', "Core file details");
	my (@CONTENT,@LINE_CONTENT) = ();
	my $SECTION = 'Core File List';
	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( /^\s*$/ ); # Skip blank lines
			SDP::Core::printDebug("  appCores ACTION", "$_");
			my (undef, undef, undef, undef, undef, $MONTH, $DAY, $YEAR, $FILENAME) = split (/\s+/,$_);
			if ($YEAR =~ m/:/) { $YEAR = $SC_YEAR; };
			my $DAYS = SDP::Core::convertDate2Days($MONTH, $DAY, $YEAR);
			SDP::Core::printDebug("  appCores PARTS", "$DAYS  $MONTH  $DAY  $YEAR  $FILENAME");
			push(@$ARRAY_REF, { filename => "$FILENAME", month => "$MONTH", day => "$DAY", year => "$YEAR", days => "$DAYS", application => "$FILENAME" } );
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}

	# add the application dumping the core to each hash
	SDP::Core::printDebug('  appCores [SECTION]', "Core file application association");
	(@CONTENT,@LINE_CONTENT) = ();
	$SECTION = '/usr/bin/file';
	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( /^\s*$/ ); # Skip blank lines
			SDP::Core::printDebug("  appCores ACTION", "$_");
			@LINE_CONTENT = split(/\s+/, $_);
			my $TMP_CORE = $LINE_CONTENT[0];
			/from '(.*)'$/;
			if ( $1 ) {
				my $CORE_APP = $1;
				$TMP_CORE =~ s/\:$//;
				for ( my $I=0; $I<@{$ARRAY_REF}; $I++) {
					if ( "@{$ARRAY_REF}[$I]->{'filename'}" eq "$TMP_CORE" ) {
						@$ARRAY_REF[$I]->{'application'} = "$CORE_APP"; # Add the application that dumped the core file
						SDP::Core::printDebug("  appCores MATCH[$I]", "@{$ARRAY_REF}[$I]->{'filename'} and $TMP_CORE map to @{$ARRAY_REF}[$I]->{'application'}");
						$I = @{$ARRAY_REF}; # Finish the loop, I found what I wanted
					} else {
						SDP::Core::printDebug("  appCores DIFFER[$I]", "@{$ARRAY_REF}[$I]->{'filename'} and $TMP_CORE");
					}
				}
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_PARTIAL, "ERROR: Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		my ($role,$i);
		for ( $i=0; $i<@{$ARRAY_REF}; $i++) {
			print(" ARRAY $i                        = ");
			for $role ( keys %{ @$ARRAY_REF[$i] } ) {
				print("'$role' => '@$ARRAY_REF[$i]->{$role}'  ");
			}
			print("\n");
		}
	}

	$RCODE = @{$ARRAY_REF};
	SDP::Core::printDebug("< appCores", "Returns: $RCODE");
	return $RCODE;
}




##############################################################################

=head1 CONTRIBUTORS

Jason Record <lt>jrecord@suse.com<gt>

=head1 COPYRIGHT

Copyright (C) 2013 SUSE Linux Products GmbH

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

=cut

1;

