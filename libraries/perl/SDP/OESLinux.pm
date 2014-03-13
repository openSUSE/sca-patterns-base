##############################################################################
#  Copyright (C) 2009,2010-2013 Novell, Inc.
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
#     Jason Record (jrecord@novell.com)
#
#  Creation Date:      2009 Jun 23
#  Last Modified Date: 2013 Jun 18
#
##############################################################################

##############################################################################
# Module Definition
##############################################################################

package      SDP::OESLinux;

=head1 NAME

SDP::OESLinux - The Support Diagnostic Pattern perl library for Open Enterprise
                Server for Linux

=head1 SYNOPSIS

use SDP::OESLinux;

=head1 DESCRIPTION

Provides necessary functions specific to patterns requiring OES for Linux 
functionality.

=cut

##############################################################################
# Exports
##############################################################################

require      Exporter;

our @ISA       = qw(Exporter);
our @EXPORT    = qw(getNssVolumes dsfwCapable iPrintClustered shadowVolumes ncsActive);
our $VERSION   = 0.0.30;

use      SDP::Core;

##############################################################################

=head1 FUNCTIONS: Information Gathering

=begin html

<hr>

=end html

=head2 getNssVolumes

=over 5

=item Description

Creates an array of hashes with NSS volumes and their attributes. Attributes are defined as the hash keys.

=item Usage

	my $i;
	my @NSS_VOLUMES = SDP::OESLinux::getNssVolumes();
	for $i (0 .. $#NSS_VOLUMES) {
		print("Volume: $NSS_VOLUMES[$i]{'name'}\n");
	}
	$i = $#NSS_VOLUMES + 1;
	print("Volumes Found: $i\n");

=item Input

None

=item Output

An array of hashes.

=item Requires

None

=item Hash Keys for Volumes

name (The NSS volume name)

state (The current volume state, ususally ACTIVE)

I<attribute> (If a volume attribute exists, the hash key is the attribute name with a value of 1; otherwise no key is defined.)

=back

=cut

sub getNssVolumes {
	SDP::Core::printDebug('> getNssVolumes', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'novell-nss.txt';
	my $SECTION = 'nss /volumes';
	my @CONTENT = ();
	my @NSS_VOLUMES = ();
	my %NSS_VOLUME = ();
	my @LINE_CONTENT = ();
	my $LINE = 0;
	my $VOL_INDEX = -1;

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		my $IN_VOLUMES = 0; # Determines if we're in the list of volumes area of the section

		foreach $_ (@CONTENT) {
			next if ( /\S+>\s/ ); # skip nss commands if present
			if ( /Volume Name\s+State\s+Attributes/ ) { # Found the volume list area of the section
				$IN_VOLUMES = 1;
				SDP::Core::printDebug("  getNssVolumes IN_VOLUMES", "$IN_VOLUMES");
			} elsif ($IN_VOLUMES == 1 && !($_ =~ /^-+/)) { # We're in the volume list, but skipping the header line with dashes "-"
				$LINE++;
				if ( /^$|^\s+$/ ) { # A blank line or lines with only white space leave the volume list area of the section
					$IN_VOLUMES = 0;
					SDP::Core::printDebug("  getNssVolumes IN_VOLUMES", "$IN_VOLUMES");
				} elsif ( /^\S/ ) { # First line of a volume that includes the volume name
					SDP::Core::printDebug("  getNssVolumes LINE $LINE SET", $_);
					$VOL_INDEX++;
					@LINE_CONTENT = split(/\s+/, $_);
					$NSS_VOLUMES[$VOL_INDEX]{'name'} = shift(@LINE_CONTENT);
					$NSS_VOLUMES[$VOL_INDEX]{'state'} = shift(@LINE_CONTENT);
					if ( $#LINE_CONTENT >= 0 ) { # Use attribute name as the key
						$NSS_VOLUMES[$VOL_INDEX]{"@LINE_CONTENT"} = 1;
					}
				} elsif ( /^\s/ ) { # An additional line for a volume
					SDP::Core::printDebug("  getNssVolumes LINE $LINE UNSET", $_);
					s/^\s+//; # Remove leading white space
					s/\s+$//; # Remove trailing white space
					$NSS_VOLUMES[$VOL_INDEX]{"$_"} = 1; # Use attribute name as the key
				} else {
					SDP::Core::printDebug("  getNssVolumes LINE $LINE IGNORED", $_);
				}
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		my $i;
		my $role;
		
		foreach $i (0 .. $#NSS_VOLUMES) {
			print(" NSS VOLUME $i                   = ");
			for $role ( keys %{ $NSS_VOLUMES[$i] } ) {
				print("'$role' => '$NSS_VOLUMES[$i]{$role}'  ");
			}
			print("\n");
		}
	}
	$RCODE = $#NSS_VOLUMES + 1;
	SDP::Core::printDebug("< getNssVolumes", "Volumes Found: $RCODE");
	return @NSS_VOLUMES;
}

=begin html

<hr>

=end html

=head2 ncsActive

=over 5

=item Description

Returns true is Novell Cluster Services is active on the server, otherwise it returns false.

=item Usage

	if ( SDP::OESLinux::ncsActive() ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "NCS is Active on the Server");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "NCS is NOT active on the Server");
	}


=item Input

None

=item Output

0 = NCS Not Active

1 = NCS Active

=item Requires

None

=back

=cut

sub ncsActive {
	SDP::Core::printDebug('> ncsActive', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'novell-ncs.txt';
	my $SECTION = 'cluster stats display';
	my @CONTENT = ();

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( m/^\s*$/ ); # Skip blank lines
			if ( /^node 0/ ) {
				$RCODE++;
				last;
			}
		}
	}
	SDP::Core::printDebug("< ncsActive", "Returns: $RCODE");
	return $RCODE;
}



=begin html

<hr>

=end html

=head2 dsfwCapable

=over 5

=item Description

Checks for DSfW capabilities from the LDAP root DSE server in novell-lum.txt file.

=item Usage

	if ( SDP::OESLinux::dsfwCapable() ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Server is DSfW Capable");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Server is not DSfW Capable");
	}


=item Input

None

=item Output

0 = No DSfW

1 = DSfW capable

=item Requires

None

=back

=cut

sub dsfwCapable {
	SDP::Core::printDebug('> dsfwCapable', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'novell-lum.txt';
	my $SECTION = 'ldapsearch -x';
	my @CONTENT = ();

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( m/^\s*$/ ); # Skip blank lines
			if ( /2.16.840.1.113719.1.513.7.1/ ) { # suppportedCapabilities listed in the LDAP Root DSE, this value represent DSfW capable
				$RCODE++;
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: dsfwCapable(): Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	SDP::Core::printDebug("< dsfwCapable", "Returns: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 shadowVolumes

=over 5

=item Description

Checks for DSfW capabilities from the LDAP root DSE server in novell-lum.txt file.

=item Usage

	if ( SDP::OESLinux::shadowVolumes() ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Server is DSfW Capable");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "Server is not DSfW Capable");
	}


=item Input

None

=item Output

0 = No Dynamic Storeage Technology Shadow Volumes in use

1 = Shadow Volumes in use

=item Requires

None

=back

=cut

sub shadowVolumes {
	SDP::Core::printDebug('> shadowVolumes', 'BEGIN');
	my $RCODE = 0;
	my $FILE_OPEN = 'novell-ncp.txt';
	my $SECTION = '/etc/opt/novell/ncpserv.conf';
	my @CONTENT = ();

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( m/^\s*$/ ); # Skip blank lines
			if ( /SHADOW_VOLUME/ ) {
				$RCODE++;
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: shadowVolumes(): Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	SDP::Core::printDebug("< shadowVolumes", "Returns: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 iPrintClustered

=over 5

=item Description

Checks to see if iPrint has been configured in a clustered environment.

=item Usage

	my $IPNCS = SDP::OESLinux::iPrintClustered();
	if ( $IPNCS > 0 ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "iPrint is Clustered");
	} elsif ( $IPNCS < 0 ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: Invalid iPrint Cluster Configuration");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "iPrint is NOT Clustered");
	}


=item Input

None

=item Output

-1 = Invalid cluster configuration

0  = iPrint is not clustered

1  = iPrint is clustered

=item Requires

None

=back

=cut

sub iPrintClustered {
	SDP::Core::printDebug('> iPrintClustered', 'BEGIN');
	my $RCODE = 0;
	my $NCSCOUNT = 0;
	my $NCSREQ = 3;
	my $FILE_OPEN = 'plugin-iPrint.txt';
	my $SECTION = '^novell-iprint-server';
	my @CONTENT = ();

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( m/^\s*$/ ); # Skip blank lines
			if ( /\/var\/opt\/novell\/iprint$/ ) {
				SDP::Core::printDebug("  iPrintClustered PROCESSING", $_);
				$NCSCOUNT++ if ( /^l/ );
			} elsif ( /\/etc\/opt\/novell\/iprint\/conf$/ ) {
				SDP::Core::printDebug("  iPrintClustered PROCESSING", $_);
				$NCSCOUNT++ if ( /^l/ );
			} elsif ( /\/var\/opt\/novell\/log\/iprint$/ ) {
				SDP::Core::printDebug("  iPrintClustered PROCESSING", $_);
				$NCSCOUNT++ if ( /^l/ );
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: iPrintClustered(): Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	if ( $NCSCOUNT > 0 ) {
		if ( $NCSCOUNT < $NCSREQ ) {
			$RCODE = -1;
		} else {
			$RCODE = 1;
		}
	}
	SDP::Core::printDebug("< iPrintClustered", "Returns: $RCODE");
	return $RCODE;
}

##############################################################################

=head1 CONTRIBUTORS

Jason Record E<lt>jrecord@novell.comE<gt>

=head1 COPYRIGHT

Copyright (C) 2009,2010-2013 Novell, Inc.

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

