##############################################################################
#  Copyright (C) 2008,2009,2010-2013 Novell, Inc.
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
#     Tregaron Bayly (tbayly@novell.com)
#
#  Last Modified Date: 2013 Jun 13
#
##############################################################################

package SDP::eDir;

use SDP::Core;
use strict;
use warnings;

require Exporter;

=head1 NAME

eDir - The Support Diagnostic Pattern eDirectory perl library

=head1 SYNOPSIS

use SDP::eDir;

=head1 DESCRIPTION

Provides shared functions for eDirectory support pattern analysis

=head1 Constants

=over 5

=item EDIR_NOT_INSTALLED - 
  An instance of eDirectory is not installed

=item EDIR_NOT_RUNNING - 
  An instance of ndsd is not running on the machine

=cut

use constant EDIR_NOT_INSTALLED                   => 1;
use constant EDIR_NOT_RUNNING                     => 2;

our @ISA = qw(Exporter);

our %EXPORT_TAGS = ( 'all' => [ qw(
	
) ] );

our @EXPORT_OK = ( @{ $EXPORT_TAGS{'all'} } );

our @EXPORT = qw(EDIR_NOT_INSTALLED EDIR_NOT_RUNNING eDirValidation eDirStatus ndsdMemoryMaximum);

our $VERSION = '1.1.0';

=back

=head1 Functions

=head2 eDirValidation

=over 2

=item Description

eDirValidation tests to ensure that eDirectory rpm is installed and the daemon is running.

=item Examples

  SDP::eDir::eDirValidation()

  will cause the pattern to exit with STATUS_ERROR if eDirectory is not installed or is not running.  The function
  can only return 0.

  SDP::eDir::eDirValidation(EDIR_NOT_INSTALLED)

  will cause the pattern to exit with STATUS_ERROR if eDirectory is not running.  The function will either return 
  0 if eDirectory is installed, or EDIR_NOT_INSTALLED if eDirectory is not installed.

  SDP::eDir::eDirValidation(EDIR_NOT_RUNNING)

  will cause the pattern to exit with STATUS_ERROR if eDirectory is not installed.  The function will either return
  0 if eDirectory is running, or EDIR_NOT_RUNNING if eDirectory is not running.

  SDP::eDir::eDirValidation(EDIR_NOT_INSTALLED | EDIR_NOT_RUNNING)

  will never cause the pattern to exit with STATUS_ERROR.  The function will either return a 0 if eDirectory is
  installed and running, or a bitwise OR of EDIR_NOT_RUNNING and EDIR_NOT_INSTALLED depending on what is
  discovered.  Check the return with a bitwise AND to detect what was found.

=back 

=cut

sub eDirValidation {

  my ($mask) = @_;
  unless( defined($mask) ) { $mask = 0; }
  my $return = 0;
  my $eDir_is_installed = 0;
  my $eDir_is_running = 0;

  my $file = "rpm.txt";
  my $section = "rpm -qa";
  my @output = ();

  if (SDP::Core::getSection($file, $section, \@output)) {
    foreach $_ (@output) {
      if ($_ =~ "NDSserv") { $eDir_is_installed = 1; }
    }
  }
  else {
    SDP::Core::updateStatus(STATUS_ERROR, "eDirectory Pattern", "Cannot find \"$section\" section in $file");
  }

  @output = ();

  if (SDP::Core::getSection("basic-health-check.txt", "/bin/ps axwwo", \@output)) {
    foreach $_ (@output) {
      if ($_ =~ "ndsd") { $eDir_is_running = 1; }
    }
  }
  else {
    SDP::Core::updateStatus(STATUS_ERROR, "eDirectory Pattern", "Cannot find \"ps\" section in basic-health-check.txt");
  }
  
  unless ($eDir_is_installed) {
     if ($mask & EDIR_NOT_INSTALLED) {
       $return += EDIR_NOT_INSTALLED;
     }
     else {
       SDP::Core::updateStatus(STATUS_ERROR, "eDirectory Pattern", "eDirectory is not installed");
     }
  }
  unless ($eDir_is_running) {
      if ($mask & EDIR_NOT_RUNNING) {
        $return += EDIR_NOT_RUNNING;
      }
      else {
        SDP::Core::updateStatus(STATUS_ERROR, "eDirectory Pattern", "eDirectory is not running");
      }
  }

  return $return;

}

=begin html

<hr>

=end html

=head2 eDirStatus

=over 2

=item Description

eDirStatus returns the output of the ndsstat command into a hash

=item Example

  use SDP::eDir;
  my %ndsstat = SDP::eDir::eDirStatus();
  print "Using eDirectory version $ndsstat{'Binary Version'}\n"; 
  print "Testing server $ndsstat{'Server Name'} in tree $ndsstat{'Tree Name'}\n";

=back

=cut

sub eDirStatus {
	my $file          = "novell-edir.txt";
	my %ndsstat       = ();
        my $section       = "ndsstat";
        my @content       = ();

        if (SDP::Core::getSection($file, $section, \@content)) {
          foreach $_ (@content) {
            my ($key, $value) = split (/:/, $_);
            if (defined($key) && defined($value)) {
              $value =~ s/^\s+//;
              $value =~ s/\s+$//;
              $ndsstat{$key} = $value;
            }
          }
        }
        else {
          SDP::Core::updateStatus(STATUS_ERROR, "eDirectory Pattern", "Cannot find \"$section\" section in $file");
        }
        return %ndsstat;
}

=begin html

<hr>

=end html

=head2 ndsdMemoryMaximum

=over 2

=item Description

ndsdMemoryMaximum returns the maximum memory size ndsd can reach before becoming unresponsive.  This number is dependent on version and architecture.

=item Example

  use SDP::eDir;
  my $maximum_memory = SDP::eDir::ndsdMemoryMaximum();

=back

=cut

sub ndsdMemoryMaximum {
  # Get architecture
  my $file          = "basic-environment.txt";
  my $section       = "uname";
  my @content       = ();
  my $architecture = "";

  if (SDP::Core::getSection($file, $section, \@content)) {
    foreach $_ (@content) {
      if ($_ =~ "x86_64") { $architecture = "x86_64"; }
      elsif ($_ =~ "i686") { $architecture = "x86"; }
    }
  }
  else {
    SDP::Core::updateStatus(STATUS_ERROR, "eDirectory Pattern", "Cannot find \"$section\" section in $file");
  }
  
  # Get eDirectory Version
  my %ndsstat = eDirStatus();

  # These calculations assume 32-bit eDirectory.  Taken from TID 3019223
  
  if ($ndsstat{'Product Version'} =~ "8.7") { 
    # eDirectory 8.73x has a maximum memory limitation of 2GB on 32 bit linux.
    if ($architecture eq "x86") { return 2000000; }
    # eDirectory 8.73x has a maximum memory limitation of 2.7GB on 64 bit linux.
    elsif ($architecture eq "x86_64") { return 2700000; }  
    # Won't handle an else fall-through case since I would have puked above...
  }
  elsif ($ndsstat{'Product Version'} =~ "8.8") {
    # eDirectory 8.8 sp2 has a maximum memory limitation of 3.0GB on 32 bit linux.
    if ($architecture eq "x86") { return 3000000; }
    # eDirectory 8.8 sp2 has a maximum memory limitation of 3.7GB on 64 bit linux.
    elsif ($architecture eq "x86_64") { return 3700000; }  
    # Won't handle an else fall-through case since I would have puked above...
  }
}


1;
__END__

=head1 AUTHOR

Tregaron Bayly, E<lt>tbayly@novell.comE<gt>

=head1 COPYRIGHT AND LICENSE

Copyright (C) 2009,2010 by Tregaron Bayly

This library is free software; you can redistribute it and/or modify
it under the same terms as Perl itself, either Perl version 5.10.0 or,
at your option, any later version of Perl 5 you may have available.

=cut

