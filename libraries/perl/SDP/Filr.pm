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
#     Jason Record (jrecord@suse.com)
#
#  Creation Date:      2013 May 22
#  Last Modified Date: 2013 Jun 22
#
##############################################################################

##############################################################################
# Module Definition
##############################################################################

package      SDP::Filr;

=head1 NAME

SDP::Filr - The Support Diagnostic Pattern perl library for Novell Filr

=head1 SYNOPSIS

use SDP::Filr;

=head1 DESCRIPTION

Provides necessary functions specific to patterns developed against supportconfig
running on Filr appliances.

=cut

##############################################################################

=head1 CONSTANTS

=head2 Filr Versions

=over 5

=item FILR1GA, FILR1R1

Novell Filr versions

=back

=cut

# Kernel Versions
use constant FILR1GA      => '1.0.459';
use constant FILR1R1      => '1.2'; # Update when/if actual version ships

##############################################################################
# Exports
##############################################################################

require      Exporter;

our @ISA       = qw(Exporter);
our @EXPORT    = qw(FILR1GA FILR1R1 getFilrVersion);
our $VERSION   = 0.0.6;

use      SDP::Core;

##############################################################################

=head1 FUNCTIONS: Information Gathering

=begin html

<hr>

=end html

=head2 getFilrVersion

=over 5

=item Description

Returns Filr version string

=item Usage

	my $FILR_VER = SDP::Filr::getFilrVersion();
	if ( "$FILR_VER" ne '' ) {
		if ( SDP::Core::compareVersions($FILR_VER, FILR1R1) < 0 ) {
			if ( vmWareVM() ) {
				SDP::Core::updateStatus(STATUS_ERROR, 'VM', "Supported VM environment: VMware");
			} else {
				SDP::Core::updateStatus(STATUS_CRITICAL, 'VM', "Unsupported Filr Appliance virtual machine environment");
			}
		} else {
			SDP::Core::updateStatus(STATUS_ERROR, 'VER', "Filr v$FILR_VER is sufficient, non-VMware skipped");
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, 'FILR', "Novell Filr Appliance not installed");
	}

=item Input

None

=item Output

Version string

=item Requires

None

=back

=cut

sub getFilrVersion {
	SDP::Core::printDebug('> getFilrVersion', 'BEGIN');
	my $RCODE = '';
	my $FILE_OPEN = 'basic-environment.txt';
	my $SECTION = '/etc/Novell-VA-release';
	my @CONTENT = ();

	if ( SDP::Core::getSection($FILE_OPEN, $SECTION, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( m/^\s*$/ ); # Skip blank lines
			if ( /version=(.*)/ ) {
				SDP::Core::printDebug("  getFilrVersion PROCESSING", $_);
				$RCODE = $1;
				$RCODE =~ s/'|"//g; # remove quotes
				last;
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: getFilrVersion(): Cannot find \"$SECTION\" section in $FILE_OPEN");
	}
	SDP::Core::printDebug("< getFilrVersion", "Returns: $RCODE");
	return $RCODE;
}

##############################################################################

=head1 CONTRIBUTORS

Jason Record E<lt>jrecord@suse.comE<gt>

=head1 COPYRIGHT

Copyright (C) 2013 SUSE LINUX Products GmbH

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

=cut

1;

