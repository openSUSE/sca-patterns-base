##############################################################################
#  Copyright (C) 2008-2014 SUSE LLC
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
#  Last Modified Date: 2014 Jan 09
#
##############################################################################

##############################################################################
# Module Definition
##############################################################################

package      SDP::Core;

=head1 NAME

SDP::Core - The Support Diagnostic Pattern core perl library

=head1 SYNOPSIS

use SDP::Core;

=head1 DESCRIPTION

Provides necessary fuctions to have a support pattern interact correctly with 
the NSA client.

=cut

##############################################################################

=head1 CONSTANTS

=head2 Setting Severity Status

=over 5

=item STATUS_TEMPORARY

This is the initial overall status. Used for pre-condition processing.

=item STATUS_PARTIAL

All criteria are only partially checked. A status that can be used to test various conditional before assigning a valid exit condition, which is an overall status of STATUS_SUCCESS or higher. Used for pre-condition processing.

=item STATUS_SUCCESS

All criteria have been checked. All are confirmed to be valid and working.

=item STATUS_RECOMMEND

All criteria have been checked. However, the linked solution is a recommendation and does not fall into the other categories. Used to recommend an optimization TID or documentation, or even product promotions.

=item STATUS_PROMOTION

All criteria have been checked. This status is used to suggest a Novell product or service from which the customer may benefit.

=item STATUS_WARNING

All criteria have been checked. The criteria show a problem may occur, but may not currently be causing symptoms.

=item STATUS_CRITICAL

All criteria have been checked. The critiera show the server is currently matching criteria for the issue being checked.

=item STATUS_ERROR

Not all criteria could be checked. A fatal pattern error has occurred, like a file not found.

=back

=head2 Setting Log Levels

=over 5

=item LOGLEVEL_QUIET

=item LOGLEVEL_DEBUG

=back

=cut

# Status Values
use constant STATUS_TEMPORARY                 => -2;
use constant STATUS_PARTIAL                   => -1;
use constant STATUS_SUCCESS                   => 0;
use constant STATUS_RECOMMEND                 => 1;
use constant STATUS_PROMOTION                 => 2;
use constant STATUS_WARNING                   => 3;
use constant STATUS_CRITICAL                  => 4;
use constant STATUS_ERROR                     => 5;
use constant STATUS_IGNORE                    => STATUS_ERROR;

use constant INDEX_OVERALL                    => 5;
use constant INDEX_OVERALL_INFO               => 6;
use constant LOGLEVEL_QUIET                   => 0;
use constant LOGLEVEL_DEBUG                   => 10;

# Pattern Result Property Names
use constant PROPERTY_NAME_CLASS              => "META_CLASS";         # Major pattern class
use constant PROPERTY_NAME_CATEGORY           => "META_CATEGORY";      # Major pattern category
use constant PROPERTY_NAME_COMPONENT          => "META_COMPONENT";     # Major pattern component
use constant PROPERTY_NAME_PATTERN_ID         => "PATTERN_ID";         # already in use need to change current use of it to be PATTERN_ID_VALUE
use constant PROPERTY_NAME_PRIMARY_LINK       => "PRIMARY_LINK";
use constant PROPERTY_NAME_OVERALL            => "OVERALL";
use constant PROPERTY_NAME_OVERALL_INFO       => "OVERALL_INFO";

use constant LESS                             => -1;
use constant EQUAL                            => 0;
use constant MORE                             => 1;

use constant CONFIGURATION_FILE               => "schealth.conf";

##############################################################################
# Exports
##############################################################################

require      Exporter;

##############################################################################

=head1 GLOBAL VARIABLES

=over 5

=item @PATTERN_RESULTS

The array returned by each pattern. There are mandatory fields and optional KEY=VALUE pairs that match criteria checked. Use L<SDP::Core::printPatternResults|/printPatternResults> to return the results to the NSA client.

=item $ARCH_PATH 

Set with the -p startup option. This is the directory where the archive is located. Default: Current Working Directory

=item $OPT_LOGLEVEL 

Sets the log level for pattern output. The -d startup option sets $OPT_LOGLEVEL to LOGLEVEL_DEBUG. (L<LOGLEVEL_QUIET|/Setting Log Levels>|L<LOGLEVEL_DEBUG|/Setting Log Levels>) Default: LOGLEVEL_QUIET

=item $GSTATUS 

Keeps track of the overall status. The worst case of all criteria checked is saved in $GSTATUS, which is returned in @PATTERN_RESULTS as the OVERALL status. You should never have to set this manually, L<SDP::Core::setStatus|/setStatus> and L<SDP::Core::updateStatus|/updateStatus> to that. 

=back

=cut

our @ISA       = qw(Exporter);
our @EXPORT    = qw(PROPERTY_NAME_CLASS PROPERTY_NAME_CATEGORY PROPERTY_NAME_COMPONENT PROPERTY_NAME_PATTERN_ID PROPERTY_NAME_PRIMARY_LINK PROPERTY_NAME_OVERALL PROPERTY_NAME_OVERALL_INFO INDEX_OVERALL INDEX_OVERALL_INFO LOGLEVEL_QUIET LOGLEVEL_DEBUG CONFIGURATION_FILE STATUS_TEMPORARY STATUS_PARTIAL STATUS_SUCCESS STATUS_RECOMMEND STATUS_PROMOTION STATUS_WARNING STATUS_CRITICAL STATUS_ERROR $OPT_LOGLEVEL $GSTATUS @PATTERN_RESULTS $PATTERN_ID $ARCH_PATH $ARCH_FILE $SRC_FILE1 $SECTION_FOUND $LINE_FOUND @SECTION $PATTERN_CONF %schealth_conf_map setStatus updateStatus loadConfFile fileOpen fileClose initFileSections listSections grepSection grepSectionLines grepSectionLinesWrap usage processOptions printDebug inSection loadFile getSection printPatternResults compareVersions convertDate2Days normalizeVersionString trimWhite ltrimWhte rtrimWhite convert2bytes fileInArchive);
our $VERSION   = 0.1.0;

##############################################################################
# Variables
##############################################################################

use File::Basename;

# Pattern Result Property Values
$META_CATEGORY      = "";

$GSTATUS            = STATUS_TEMPORARY;
$ARCH_PATH          = "";  # Set with -a directory
$PATTERN_ID         = basename($0);
$PATTERN_CONF       = "";

$OPT_LOGLEVEL       = LOGLEVEL_QUIET;

my %schealth_conf_map;    # hashmap for conf properties name/value

##############################################################################

=head1 FUNCTIONS: NSA Client Integration

=cut

=begin html

<hr>

=end html

=head2 processOptions

=over 5

=item Description

Processes the pattern's startup options, which includes setting $ARCH_PATH.

=item Usage

SDP::Core::processOptions();

=item Input

None

=item Output

L<$ARCH_PATH|/GLOBAL VARIABLES>, L<$OPT_LOGLEVEL|/GLOBAL VARIABLES>

=item Requires

None

=back

=cut

sub processOptions {
	# Get the command line startup options
	use Getopt::Std;
	my $valid_options = 'c:dhp:';
	my %opt;
	getopts("$valid_options", \%opt) or usage("ERROR: Invalid option or missing argument");

	# Process each of the command line options
	usage()                              if $opt{h};
	$OPT_LOGLEVEL   = LOGLEVEL_DEBUG     if $opt{d};
	$PATTERN_CONF   = $opt{c}            if $opt{c};
	$ARCH_PATH      = $opt{p}            if $opt{p};
	$ARCH_PATH      = $ARCH_PATH . "/"   if ( $ARCH_PATH !~ m|/$| );
}

sub usage {
	print << "UEOF";

usage: $0 [-dh][-p path][-c conf_file]

 -h            : This screen
 -d            : Debug mode
 -p path       : Supportconfig archive path
 -c conf       : Path to configuration file

UEOF
	exit;
}


=begin html

<hr>

=end html

=head2 setStatus

=over 5

=item Description

Initializes the OVERALL and OVERALL_INFO to the set status.

=item Usage

SDP::Core::setStatus(STATUS, $description);

=item Input

L<STATUS|/Setting Severity Status> (STATUS_TEMPORARY|STATUS_PARTIAL|STATUS_SUCCESS|STATUS_RECOMMEND|STATUS_PROMOTION|STATUS_WARNING|STATUS_CRITICAL|STATUS_ERROR)

$description (Brief description string)

=item Output

L<@PATTERN_RESULTS|/GLOBAL VARIABLES>, L<$GSTATUS|/GLOBAL VARIABLES>

=item Requires

None

=back

=cut

sub setStatus {
	my $CURRENT_STATUS = $_[0];
	my $DESCRIPTION    = $_[1];
	$GSTATUS = $CURRENT_STATUS;
	$PATTERN_RESULTS[INDEX_OVERALL] = "OVERALL=$GSTATUS";
	$PATTERN_RESULTS[INDEX_OVERALL_INFO] = "OVERALL_INFO=$DESCRIPTION";
	SDP::Core::printDebug('>< setStatus', "$PATTERN_RESULTS[INDEX_OVERALL], OVERALL_INFO='$PATTERN_RESULTS[INDEX_OVERALL_INFO]'");
}

=begin html

<hr>

=end html

=head2 updateStatus

=over 5

=item Description

Updates the OVERALL status if status is more severe that before. It also adds the specified key=value pair to @PATTERN_RESULTS. If the OVERALL status is green, and updateStatus is called with STATUS_SUCCESS, the OVERALL_INFO will not be updated, because the status is not worse that it was before. Use setStatus to update OVERALL and OVERALL_INFO in this case. A status greater than or equal to STATUS_ERROR, will trigger a script exit after printing @PATTERN_RESULTS.

=item Usage

SDP::Core::updateStatus(STATUS, $value);

=item Input

L<STATUS|/Setting Severity Status> (STATUS_TEMPORARY|STATUS_PARTIAL|STATUS_SUCCESS|STATUS_RECOMMEND|STATUS_PROMOTION|STATUS_WARNING|STATUS_CRITICAL|STATUS_ERROR)


=item Output

L<@PATTERN_RESULTS|/GLOBAL VARIABLES>, L<$GSTATUS|/GLOBAL VARIABLES>

=item Requires

None

=back

=cut

sub updateStatus {
	my $CURRENT_STATUS = $_[0];
	my $DESCRIPTION = $_[1];
	my $CHANGE_STATE = 'Unchanged:';
	my $PREV_STATUS = $PATTERN_RESULTS[INDEX_OVERALL];

	if ( $GSTATUS < $CURRENT_STATUS ) {
		$GSTATUS = $CURRENT_STATUS;
		$PATTERN_RESULTS[INDEX_OVERALL] = PROPERTY_NAME_OVERALL."=$GSTATUS";
		$PATTERN_RESULTS[INDEX_OVERALL_INFO] = PROPERTY_NAME_OVERALL_INFO."=$DESCRIPTION";
		$CHANGE_STATE = 'Updated:';
	}
	if ( $GSTATUS >= STATUS_ERROR ) {
		SDP::Core::printPatternResults();
		SDP::Core::printDebug(">< updateStatus STATUS_ERROR", 'SDP::Core::updateStatus(): Triggered Exit');
		exit;
	}
	SDP::Core::printDebug(">< updateStatus FROM $PREV_STATUS", "$CHANGE_STATE OVERALL=$GSTATUS, $PATTERN_RESULTS[INDEX_OVERALL_INFO]");
}


=begin html

<hr>

=end html

=head2 printPatternResults

=over 5

=item Description

Prints L<@PATTERN_RESULTS|/GLOBAL VARIABLES> to STDOUT

=item Usage

SDP::Core::printPatternResults();

=item Input

None

=item Output

None

=item Requires

None

=back

=cut

sub printPatternResults {
	printDebug('> printPatternResults');
	$" = "|"; # Change array element separator
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		foreach $_ (@PATTERN_RESULTS) {
			/(\S+)=(.*)/;
			printDebug("  printPatternResults $1", "$2");
		}
	} else {
		print("@PATTERN_RESULTS\n");
	}
	printDebug('< printPatternResults');
}

##############################################################################

=head1 FUNCTIONS: Base

=begin html

<hr>

=end html

=begin html

<hr>

=end html

=head2 convertDate2Days

=over 5

=item Description

Converts the $YEAR, $MONTH, $DAY date elements to the number of days since 1970 Jan 01.

=item Usage

	my $DAYS = SDP::Core::convertDate2Days(2009, 'Jan', 2);
	SDP::Core::updateStatus(STATUS_PARTITAL, "Number of days from 1970 Jan 01 to 2009 Jan 02: $DAYS");

=item Input

$YEAR (Use all four digits)

$MONTH (Use locale's abbreviated month name {e.g., Jan})

$DAY (Use the day of month {e.g, 01})

=item Output

Number of days since 1970 Jan 01.

=item Requires

None

=back

=cut

sub convertDate2Days {
	SDP::Core::printDebug('> convertDate2Days', "@_");
	my ($MONTH, $DAY, $YEAR) = @_;

	if ($MONTH eq "Jan") { $MONTH = 0; }
	elsif ($MONTH eq "Feb") { $MONTH = 1; }
	elsif ($MONTH eq "Mar") { $MONTH = 2; }
	elsif ($MONTH eq "Apr") { $MONTH = 3; }
	elsif ($MONTH eq "May") { $MONTH = 4; }
	elsif ($MONTH eq "Jun") { $MONTH = 5; }
	elsif ($MONTH eq "Jul") { $MONTH = 6; }
	elsif ($MONTH eq "Aug") { $MONTH = 7; }
	elsif ($MONTH eq "Sep") { $MONTH = 8; }
	elsif ($MONTH eq "Oct") { $MONTH = 9; }
	elsif ($MONTH eq "Nov") { $MONTH = 10; }
	elsif ($MONTH eq "Dec") { $MONTH = 11; }
	else { SDP::Core::updateStatus(STATUS_ERROR, "ERROR: SDP::Core::convertDate2Days(): Unrecognized MONTH: $MONTH"); } 

	SDP::Core::printDebug("  convertDate2Days CONVERTING", "$YEAR-" . ($MONTH + 1) . "-$DAY");
	my $DAYS = _daygm( undef, undef, undef, $DAY, $MONTH, $YEAR );
  
	SDP::Core::printDebug("< convertDate2Days", "Days: $DAYS");
	return $DAYS;
}

=begin html

<hr>

=end html

=begin html

<hr>

=end html

=head2 fileInArchive

=over 5

=item Description

Returns true if the $FILE_NAME is in the supportconfig archive.

=item Usage

	my $FILE_NAME = 'plugin-iPrint.txt';
	if ( SDP::Core::fileInArchive($FILE_NAME) ) {
		SDP::Core::update_state(STATUS_SUCCESS, 'FILE', "File Found: $FILE_NAME");
	} else {
		SDP::Core::update_state(STATUS_WARNING, 'FILE', "File NOT Found: $FILE_NAME");
	}

=item Input

$FILE_NAME (The file to test.)

=item Output

0 = File NOT found in archive

1 = File found in archive

=item Requires

None

=back

=cut

sub fileInArchive {
	SDP::Core::printDebug('> fileInArchive', "@_");
	my $RCODE = 0;

	$RCODE++ if ( -e $ARCH_PATH . $_[0] );
  
	SDP::Core::printDebug("< fileInArchive", "Returns: $RCODE");
	return $RCODE;
}

=begin html

<hr>

=end html

=head2 convertDate2Days

=over 5

=item Description

Converts the $INPUT_STRING to bytes

=item Usage

	my $INPUT_STRING = "2.5G";
	my $BYTES = SDP::Core::convert2bytes($INPUT_STRING);
	SDP::Core::updateStatus(STATUS_PARTIAL, "$INPUT_STRING converts to $BYTES bytes");

=item Input

$INPUT_STRING (A digit or decimal followed by a case insensitive type qualifer.)

Valid type modifier:

	k = Kilobytes
	m = Megabytes (Default if no qualifier specified)
	g = Gigbytes
	t = Terabytes
	p = Petabytes

=item Output

Number of bytes converted from $INPUT_STRING

-1 for invalid type modifiers

=item Requires

None

=back

=cut

sub convert2bytes {
	SDP::Core::printDebug('> convert2bytes', "@_");
	my $INPUT_STRING = $_[0];
	my $BYTES = -1;
	my ($VALUE, $MODIFIER, $TYPE);
	if ( $INPUT_STRING =~ m/\D$/ ) {
		$INPUT_STRING =~ m/(.*)(\D)+/;
		($VALUE, $TYPE) = ($1, $2);
	} else { # no qualifier specified
		$VALUE = $INPUT_STRING;
		$MODIFIER = 1024*1024; # megabytes is the default
	}
	SDP::Core::printDebug("  convert2bytes CONVERT", "Value=$VALUE, Type=$TYPE");
	SDP::Core::printDebug("< convert2bytes", "Bytes: $BYTES");
	return $BYTES;
}

=begin html

<hr>

=end html

=head2 trimWhite, ltrimWhite, rtrimWhite

=over 5

=item Description

Removes leading and trailing white space from $STRING, ltrimWhite trims the left and rtrimWhite the right.

=item Usage

	my $STRING = "   This is a test   \t  ";
	SDP::Core::updateStatus(STATUS_PARTIAL, SDP::Core::trimWhite($STRING));
	SDP::Core::updateStatus(STATUS_PARTIAL, SDP::Core::ltrimWhite($STRING));
	SDP::Core::updateStatus(STATUS_PARTIAL, SDP::Core::rtrimWhite($STRING));

=item Input

$STRING (A string)

=item Output

String without leading or trailing whitespace.

=item Requires

None

=back

=cut

sub trimWhite($)
{
	my $STRING = shift;
	SDP::Core::printDebug('> trimWhite', "'$STRING'");
	$STRING =~ s/^\s+//;
	$STRING =~ s/\s+$//;
	SDP::Core::printDebug('< trimWhite', "Returns: '$STRING'");
	return $STRING;
}

sub ltrimWhite($)
{
	my $STRING = shift;
	SDP::Core::printDebug('> ltrimWhite', "'$STRING'");
	$STRING =~ s/^\s+//;
	SDP::Core::printDebug('< ltrimWhite', "Returns: '$STRING'");
	return $STRING;
}

sub rtrimWhite($)
{
	my $STRING = shift;
	SDP::Core::printDebug('> rtrimWhite', "'$STRING'");
	$STRING =~ s/\s+$//;
	SDP::Core::printDebug('< rtrimWhite', "Returns: '$STRING'");
	return $STRING;
}



=head1 FUNCTIONS: Information Gathering

=begin html

<hr>

=end html

=head2 listSections

=over 5

=item Description

Stores the section names in ARRAY_POINTER contined in FILE_OPEN.

=item Usage

	my $FILE_OPEN = 'fs-diskio.txt';
	my @FILE_SECTIONS = ();
	my $SECTION = '';

	if ( SDP::Core::listSections($FILE_OPEN, \@FILE_SECTIONS) ) {
		foreach $SECTION (@FILE_SECTIONS) {
			if ( $SECTION =~ m/\/parted -s / ) {
				printf("Section with parted: $SECTION\n");
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: myFunction(): No sections found in $FILE_OPEN");
	}

=item Input

FILE_OPEN (The supportconfig FILE_OPEN to look in)

ARRAY_POINTER (A pointer to an array that will contain the FILE_OPEN section names)

=item Output

Number of elements in the array

=item Requires

None

=back

=cut

sub listSections {
	my $FILE_OPEN = $ARCH_PATH . $_[0];
	my $ARRAY_REF = $_[1];
	my $SECTION_FOUND = 0;
	my $SECTION_COUNT = 0;
	printDebug('> listSections', "'$FILE_OPEN'");

	if ( ! open(FILE, $FILE_OPEN) ) {
		setStatus(STATUS_ERROR, "ERROR: SDP::Core::listSections(): Cannot open file, $FILE_OPEN");
		printPatternResults();
		exit;
	} else {
		printDebug("  listSections FILE OPENED", $FILE_OPEN);
	}

	while (my $line = <FILE>) {
		chomp ($line);
		if ($line =~ m/#=+\[.+\]=+#/) { # section found
			$SECTION_FOUND = 1;
		} elsif ( $SECTION_FOUND ) {
			$SECTION_COUNT++;
			$line =~ s/# //g;
			printDebug("  listSections SECTION NAME:$SECTION_COUNT", $line);
			push(@$ARRAY_REF, $line);
			$SECTION_FOUND = 0;
		}
	}

	# Close the file
	if ( ! close(FILE) ) {
		setStatus(STATUS_ERROR, "ERROR: SDP::Core::listSections(): Cannot close file, $FILE_OPEN");
		printPatternResults();
		exit;
	} else {
		printDebug("  listSections FILE CLOSED", $FILE_OPEN);
	}

	printDebug('< listSections', "Sections Found: $SECTION_COUNT");
	return @$ARRAY_REF;
}

=begin html

<hr>

=end html

=head2 inSection

=over 5

=item Description

Opens FILE_OPEN and looks for SEARCH_STRING anywhere in the file

=item Usage

	my $FILE_OPEN = 'modules.txt';
	my $MODULE = 'usbcore';
	my $SEARCH_STRING = "options.*$MODULE.*usbfs_snoop"
	my $FOUND = SDP::Core::inSection($FILE_OPEN, $SEARCH_STRING);
	if ( $FOUND ) {
		SDP::Core::updateStatus(STATUS_SUCCESS, "Found $SEARCH_STRING in $FILE_OPEN, section $FOUND");
	} else {
		SDP::Core::updateStatus(STATUS_WARNING, "NOT FOUND: $SEARCH_STRING in $FILE_OPEN");
	} 

=item Input

FILE_OPEN (The supportconfig filename to look in)

SEARCH_STRING (The string you are looking for in FILE_OPEN)

=item Output

The section name in $FILE_OPEN where $SEARCH_STRING is first found.

=item Requires

None

=back

=cut

sub inSection {
	my $FILE_OPEN = $ARCH_PATH . $_[0];
	my $SEARCH_STRING = $_[1];
	my $STRING_FOUND = 0;
	my $SECTION = '';
	my $GET_SECTION = 0;
	SDP::Core::printDebug('> inSection', "'$FILE_OPEN' '$SEARCH_STRING' 'Searching\.\.\.\'");

	# Open the file
	if ( ! open(FILE, $FILE_OPEN) ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: SDP::Core::inSection(): Cannot open file, $FILE_OPEN");
	} else {
		SDP::Core::printDebug("  inSection FILE OPENED", $FILE_OPEN);
	}

	while (my $LINE = <FILE>) {
		chomp ($LINE);
		if ( $GET_SECTION ) {
			$SECTION = $LINE;
			$SECTION =~ s/^#\s+//g;
			$GET_SECTION = 0;
		} elsif ( $LINE =~ m/^#==\[/ ) {
			$GET_SECTION = 1;
		} elsif ( $LINE =~ m/$SEARCH_STRING/i ) {
			$STRING_FOUND++;
			last;
		}
	}
	$SECTION = '' if ( ! $STRING_FOUND );

	# Close the file
	if ( ! close(FILE) ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: SDP::Core::inSection(): Cannot close file, $FILE_OPEN");
	} else {
		SDP::Core::printDebug("  inSection FILE CLOSED", $file_name);
	}


	SDP::Core::printDebug('< inSection', "STRING_FOUND: $STRING_FOUND, SECTION: '$SECTION'");
	return $SECTION;
}

=begin html

<hr>

=end html

=head2 loadFile

=over 5

=item Description

Loads the entire $FILE_OPEN into @CONTENT, skipping blank lines.

=item Usage

	my $FILE_OPEN = 'modules.txt';
	my @CONTENT = ();
	my $STATE = 0;
	my $CONTENT_FOUND = 0;
	if ( SDP::Core::loadFile($FILE_OPEN, \@CONTENT) ) {
		foreach $_ (@CONTENT) {
			next if ( m/^\s*$/ ); # Skip blank lines
			if ( $STATE ) {
				if ( /^#==\[/ ) {
					$STATE = 0;
					SDP::Core::printDebug("  main DONE", "State Off");
				} elsif ( /SearchForSectionContent/ ) { # Section content needed
					$CONTENT_FOUND = 1;
				}
			} elsif ( /^# SectionNameToSearchFor/ ) { # Section
				$STATE = 1;
				SDP::Core::printDebug("  main CHECK", "Section: $_");
			}
		}
	} else {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: checkSomething(): Cannot load file: $FILE_OPEN");
	}

=item Input

LOAD_FILE (The supportconfig filename to open)

ARRAY_REF (An address to an array)

=item Output

$ARRAY_REF and the number lines in the array

=item Requires

None

=back

=cut

sub loadFile {
	my $FILE_OPEN = $ARCH_PATH . $_[0];
	my $ARRAY_REF = $_[1];
	SDP::Core::printDebug('> loadFile', "'$FILE_OPEN'");

	# Open the file
	if ( ! open(FILE, $FILE_OPEN) ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: SDP::Core::loadFile(): Cannot open file, $FILE_OPEN");
	} else {
		SDP::Core::printDebug("  loadFile FILE OPENED", $FILE_OPEN);
	}

	while (my $LINE = <FILE>) {
		chomp ($LINE);
		next if ( $LINE =~ m/^\s*$/ ); # skip blank lines
		push(@$ARRAY_REF, $LINE);
	}

	# Close the file
	if ( ! close(FILE) ) {
		SDP::Core::updateStatus(STATUS_ERROR, "ERROR: SDP::Core::loadFile(): Cannot close file, $FILE_OPEN");
	} else {
		SDP::Core::printDebug("  loadFile FILE CLOSED", $FILE_OPEN);
	}

	my $LINES = scalar @$ARRAY_REF;
	SDP::Core::printDebug('< loadFile', "Lines: $LINES");
	return $LINES;
}


=begin html

<hr>

=end html

=head2 getSection

=over 5

=item Description

Opens file_name and retrieves the section matching the search string into the specified array

=item Usage

SDP::Core::getSection($file_name, $section, \@array_pointer);

=item Input

file_name (The supportconfig file_name to look in)

section (The name of the section you want)

array_pointer (A pointer to an array that will contain the lines of the section asked for)

=item Output

Number of elements in the array

=item Requires

None

=back

=cut

sub getSection {
	my $file_name = $ARCH_PATH . $_[0];
	my $search_string = $_[1];
	my $array_ref = $_[2];
	my $section_name = "";
	my $section_found = 0;
	printDebug('> getSection', "'$file_name' '$search_string' 'Searching\.\.\.\'");

	if ( ! open(FILE, $file_name) ) {
		setStatus(STATUS_ERROR, "ERROR: SDP::Core::getSection(): Cannot open file, $file_name");
		printPatternResults();
		exit;
	} else {
		printDebug("  getSection OPEN", $file_name);
	}

	while (my $line = <FILE>) {
		chomp ($line);
		if ($line =~ m/#=+\[.+\]=+#/) { # section found
			$section_name = "";
		} elsif ($section_name eq "") {
			$line =~ s/# //g;
			$section_name = $line;
		} elsif ($section_name =~ /$search_string/) {
			push(@$array_ref, $line);
			$section_found = 1;
		}
	}

	# Close the file
	if ( ! close(FILE) ) {
		setStatus(STATUS_ERROR, "ERROR: SDP::Core::getSection(): Cannot close file, $file_name");
		printPatternResults();
		exit;
	} else {
		printDebug("  getSection CLOSE", $file_name);
	}

	printDebug('< getSection', "Section Found: $section_found, '$_[0]' '$search_string'");
	return @$array_ref;
}

sub _daygm {
# Lifted this function from Time::Local library in order to 
# not require that the perl installation have it included.
# Copyright (c) 1997-2003 Graham Barr, 2003-2007 David Rolsky.  All
# rights reserved.  This (module) is free software; you can redistribute
# it and/or modify it under the same terms as Perl itself.
#
# This is written in such a byzantine way in order to avoid
# lexical variables and sub calls, for speed
	return $_[3] + (
		do {
			my $MONTH = ( $_[4] + 10 ) % 12;
			my $YEAR  = ( $_[5] + 1900 ) - ( $MONTH / 10 );

			( ( 365 * $YEAR )
			+ ( $YEAR / 4 )
			- ( $YEAR / 100 )
			+ ( $YEAR / 400 )
			+ ( ( ( $MONTH * 306 ) + 5 ) / 10 )
			)
		}
	);
}

=begin html

<hr>

=end html

=head2 normalizeVersionString

=over 5

=item Description

Converts a version string $VERSTR to an array of version elements. This function separates elements based on /usr/share/doc/packages/rpm/manual/dependencies. See the paragraph beginning: "The algorithm that RPM uses to determine the version...."

=item Usage

	my $VERSTR = '1.0-1.83';
	my @FIRST = SDP::Core::normalizeVersionString($VERSTR);
	SDP::Core::printDebug('$FIRST[$#FIRST]', "$FIRST[$#FIRST]");

=item Input

$VERSTR (A version string)

=item Output

Array of version elements

=item Requires

None

=back

=cut

sub normalizeVersionString {

	my $VERSTR = $_[0];
	printDebug('> normalizeVersionString', "'$VERSTR'");

	my @NORMALIZED = ();

	# define version boundaries
	$VERSTR =~ s/[\.,\-,_,+]/\|/g;		# replace all version seperators with the bar "|" boundary character 
#	printDebug("  normalizeVersionString SEPARATORS", "$VERSTR");
	$VERSTR =~ s/([A-Z,a-z]+)/\|$1\|/g;	# place a boundary character between groups of letters
#	printDebug("  normalizeVersionString LETTER GROUPS", "$VERSTR");
	$VERSTR =~ s/\|\|/\|/g;					# replace all double boundary characters with a single one
#	printDebug("  normalizeVersionString DOUBLE \|", "$VERSTR");
	$VERSTR =~ s/\|0+([1-9])/\|$1/g;		# strip off leading zeros in version elements
#	printDebug("  normalizeVersionString LEADING ZEROS", "$VERSTR");
	printDebug("  normalizeVersionString BOUNDARIES", "$VERSTR");
	@NORMALIZED = split(/\|/, $VERSTR);	# split the version elements into an array for analysis
	my $ELEMENTS = $#NORMALIZED + 1;
	printDebug("  normalizeVersionString BOUNDARY ARRAY", "@NORMALIZED");

	SDP::Core::printDebug("< normalizeVersionString", "'$_[0]' contains $ELEMENTS elements");
	return @NORMALIZED;
}


##############################################################################

=head1 FUNCTIONS: Comparisons

=begin html

<hr>

=end html

=head2 compareVersions

=over 5

=item Description

Compares two version strings. Only the most significant version components are compared. For example, if 2.6.5 is compared with 2.6.16.60-0.23, then only 2.6.5 and 2.6.16 will be used for the comparison. Characters in the version strings are separated into their own version element, as if there were a "." at the beginning and end of the group of letters. String comparisons are used on string elements and numeric comparisons are used for digits. If a numeric element is compared to a string element, the numeric element will be converted to string for the comparison.

=item Usage

SDP::Core::compareVersions($verstr1, $verstr2);

=item Input

$verstr1 (The first version string to compare)

$verstr2 (The last version string to compare)

=item Output

-1 if $verstr1 < $verstr2

0 if $verstr1 == $verstr2

1 if $verstr1 > $verstr2


=item Requires

None

=back

=cut

sub compareVersions {
# This function should work somewhat as described in:
# /usr/share/doc/packages/rpm/manual/dependencies
# See the paragraph beginning: "The algorithm that RPM
# uses to determine the version...."

	my $COMPARISON       = EQUAL;
	my $VERSTR_1         = $_[0];
	my $VERSTR_2         = $_[1];
	printDebug('> compareVersions', "'$VERSTR_1' to '$VERSTR_2'");

	if ( $VERSTR_1 ne $VERSTR_2 ) {
		my @FIRST = SDP::Core::normalizeVersionString($VERSTR_1);
		my @LAST = SDP::Core::normalizeVersionString($VERSTR_2);

		# use the smallest version string which represents the most significant version elements
		if ( $#FIRST <= $#LAST ) {
			$TOTAL_ELEMENTS = $#FIRST + 1;
		} else {
			$TOTAL_ELEMENTS = $#LAST + 1;
		}
		printDebug("  compareVersions TOTAL_ELEMENTS", $TOTAL_ELEMENTS);

		# compare version elements
		my $FSTR = "";
		my $LSTR = "";
		for ( my $I=0; $I < $TOTAL_ELEMENTS; $I++ ) {
			if ( $FIRST[$I] =~ m/\D/ || $LAST[$I] =~ m/\D/ ) {
				$FSTR = sprintf("%s", $FIRST[$I]);
				$LSTR = sprintf("%s", $LAST[$I]);
				if ( $FSTR gt $LSTR ) {
					printDebug("  compareVersions F/L Str", "$FSTR gt $LSTR");
					$COMPARISON = MORE;
					$I = $TOTAL_ELEMENTS;
				} elsif ( $FSTR lt $LSTR ) {
					printDebug("  compareVersions F/L Str", "$FSTR lt $LSTR");
					$COMPARISON = LESS;
					$I = $TOTAL_ELEMENTS;
				} else {
					printDebug("  compareVersions F/L Str", "$FSTR eq $LSTR");
				}
			} else {
				if ( $FIRST[$I] > $LAST[$I] ) {
					printDebug("  compareVersions F/L Num", "$FIRST[$I] gt $LAST[$I]");
					$COMPARISON = MORE;
					$I = $TOTAL_ELEMENTS;
				} elsif ( $FIRST[$I] < $LAST[$I] ) {
					printDebug("  compareVersions F/L Num", "$FIRST[$I] lt $LAST[$I]");
					$COMPARISON = LESS;
					$I = $TOTAL_ELEMENTS;
				} else {
					printDebug("  compareVersions F/L Num", "$FIRST[$I] eq $LAST[$I]");
				}
			}
		}
	} else {
		printDebug("  compareVersions F/L", "$VERSTR_1 eq $VERSTR_2");
	}

	if ( $COMPARISON < 0 ) {
		printDebug('  compareVersions COMPARISON RESULT', "$VERSTR_1 < $VERSTR_2");
	} elsif ( $COMPARISON > 0 ) {
		printDebug('  compareVersions COMPARISON RESULT', "$VERSTR_1 > $VERSTR_2");
	} else {
		printDebug('  compareVersions COMPARISON RESULT', "$VERSTR_1 == $VERSTR_2");
	}
	printDebug('< compareVersions', "COMPARISON: $COMPARISON");
	return $COMPARISON;
}


##############################################################################

=head1 FUNCTIONS: Debugging

=begin html

<hr>

=end html

=head2 printDebug

=over 5

=item Description

Prints the label and value to STDOUT if the L<$OPT_LOGLEVEL|/GLOBAL VARIABLES> is set to LOGLEVEL_DEBUG or higher.

=item Usage

SDP::Core::printDebug($label, $value);

=item Input

$label (Any string that labels you debug output)

$value (The values or variables you want to print out. Does not support arrays or hashes.)

=item Output

None

=item Requires

None

=back

=cut

sub printDebug {
	my $LABEL = $_[0];
	my $VALUE = $_[1];
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		if ( defined $VALUE ) {
			printf(" %-45s = %s\n", $LABEL, $VALUE);
		} else {
			printf(" %-45s\n", $LABEL);
		}
	}
}

##############################################################################
# Functions to be deprecated
##############################################################################

sub fileOpen {
	if ( ! open(SRC_FILE1, "$SRC_FILE1") ) {
		setStatus(STATUS_ERROR, "ERROR: SDP::Core::fileOpen(): Cannot open $SRC_FILE1");
		printPatternResults();
		exit;
	}
}

sub fileClose {
	if ( ! close(SRC_FILE1) ) {
		setStatus(STATUS_ERROR, "ERROR: SDP::Core::fileClose(): Cannot open $SRC_FILE1");
		print("ERROR: Cannot close $SRC_FILE1\n");
	}
}

# load the property configuration file to hashmap
# requires $PATTERN_CONF (via -c option or sub pattern libary script) 
sub loadConfFile() {
	my $line;                 # line of file read
	my $key;                  # key (property name)
	my $value;                # value (property value)

	open( SCHEALTH_CONF, $PATTERN_CONF )
		or die OPEN_FILE_ERROR . $PATTERN_CONF . "\n";

	while ( $line = <SCHEALTH_CONF> ) {
		$line =~ s/^#.*?\n//;
		if ($line) {
			( $key, $value ) = split( "=", $line );
			$value =~ s/\s*#.*?\n//	if $key	&& $value; # get rid of the whitespace and comments, keep only the actual property value
			print "$key=$value\n" if $OPT_LOGLEVEL >= LOGLEVEL_DEBUG && $key && $value;
			if ( $key && $value ) { # only if they exist do we need to add them to the name/value property hashmap
				$schealth_conf_map{$key} = $value;
			}
		}
	}
	print "\n\n" if $OPT_LOGLEVEL >= LOGLEVEL_DEBUG;

	close(SCHEALTH_CONF);
	return;
}


# Defines @SECTION with section header line number values
sub initFileSections {
	my $LINES             = 0;
	my $SECTIONS          = 0;
	@SECTION              = ();

	fileOpen();
	# Get section starting line numbers
	while (<SRC_FILE1>) {
		$LINES++;	# Count the lines
		# Get the line number of each line beginning with #==[
		# These line numbers are the section headers
		$SECTION[$SECTIONS++] = $LINES if /^#==\[/; 
	}
	$SECTION[$SECTIONS] = $LINES;
	fileClose();
}

# Returns an array with the line containing $GREP_FOR in the
# specified section. Only searches the first section found 
# containing the $SECT_DESC.
# Input:    1 - section descriptor, 2 - search for string
# Output:   Array with line containing search criteria
# Requires: initFileSections()
sub grepSection {
	my $SECT_DESC         = $_[0];
	my $GREP_FOR          = $_[1];
	my @FOUND_LINE        = ();
	my $CURR_LINE         = 1;
	my $CURR_INDEX        = 0;
	my $FOUND_INDEX       = -1;
	$SECTION_FOUND        = 0;
	$LINE_FOUND           = 0;

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		print("\n> grepSection   - BEGIN @SECTION\n");
		print("SECT_DESC       = $SECT_DESC\n");
		print("GREP_FOR        = $GREP_FOR\n");
		print("CURR_INDEX      = $CURR_INDEX\n");
		print("CURR_LINE       = $CURR_LINE\n");
		print("SECTION_FOUND   = $SECTION_FOUND\n");
		print("LINE_FOUND      = $LINE_FOUND\n");
		print("FOUND_INDEX     = $FOUND_INDEX\n");
		print("FOUND_LINE      = @FOUND_LINE\n");
		print("#FOUND_LINE     = $#FOUND_LINE\n");
		print("\n\n");
	}
	fileOpen();
	# Search each line of the file for $SECT_DESC and then assign
	# the section it's in. The first section header that matches
	# is returned.
	foreach $INLINE (<SRC_FILE1>) {
		chomp($INLINE);
		if ( $CURR_LINE >= $SECTION[$CURR_INDEX] ) {
			printf("%3g,%3g,%3g: %s\n", $CURR_LINE, $CURR_INDEX, $SECTION[$CURR_INDEX], $INLINE) if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG );
			# Only look for $SECT_DESC in the second line of each section
			if ( $FOUND_INDEX < 0 && $INLINE =~ /$SECT_DESC/ && $CURR_LINE == $SECTION[$CURR_INDEX]+1 && $CURR_LINE < $SECTION[$CURR_INDEX+1]) {
				$SECTION_FOUND++;
				$FOUND_INDEX = $CURR_INDEX;
				printf("SECTION MATCH: %3g,%3g,%3g: %s\n", $CURR_LINE, $CURR_INDEX, $SECTION[$CURR_INDEX], $INLINE) if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG );
			}
			elsif ( $INLINE =~ /$GREP_FOR/ && $CURR_LINE < $SECTION[$FOUND_INDEX+1]) {
				printf("GREP MATCH: %3g,%3g,%3g: %s\n", $CURR_LINE, $CURR_INDEX, $SECTION[$CURR_INDEX], $INLINE) if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG );
				$LINE_FOUND++;
				@FOUND_LINE = ($CURR_LINE, split(/\s/, $INLINE));
				last;  # break from loop - found the line
			}
			
			$CURR_INDEX++ if($CURR_INDEX < $#SECTION && $CURR_LINE+1 == $SECTION[$CURR_INDEX+1]);
		}
		
		$CURR_LINE++;
	}
	fileClose();
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		$" = "|"; # Change array element separator
		print("\n< grepSection   - END @SECTION\n");
		print("SECT_DESC       = $SECT_DESC\n");
		print("GREP_FOR        = $GREP_FOR\n");
		print("CURR_INDEX      = $CURR_INDEX\n");
		print("CURR_LINE       = $CURR_LINE\n");
		print("LINE_FOUND      = $LINE_FOUND\n");
		print("SECTION_FOUND   = $SECTION_FOUND\n");
		print("FOUND_INDEX     = $FOUND_INDEX\n");
		print("FOUND_LINE      = @FOUND_LINE\n");
		print("#FOUND_LINE     = $#FOUND_LINE\n");
		print("\n\n");
	}
	return(@FOUND_LINE);
}

# Returns an array of arrays with the lines containing $GREP_FOR
# from the specified section. Only searches the first section found 
# containing the $SECT_DESC. Columns split on any number of whitespaces in a row
# Input:    1 - section descriptor
#           2 - search for string
# Output:   Array with lines (each line is a pre-tokenized array) containing search criteria
# Requires: initFileSections()
sub grepSectionLines {
	my $SECT_DESC         = $_[0];
	my $GREP_FOR          = $_[1];
	my (@FOUND_LINES, @FOUND_LINE);
	my $CURR_LINE         = 1;
	my $CURR_INDEX        = 0;
	my $FOUND_INDEX       = -1;
	$SECTION_FOUND        = 0;
	$LINE_FOUND           = 0;

	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		print("\n> grepSection   - BEGIN @SECTION\n");
		print("SECT_DESC       = $SECT_DESC\n");
		print("GREP_FOR        = $GREP_FOR\n");
		print("CURR_INDEX      = $CURR_INDEX\n");
		print("CURR_LINE       = $CURR_LINE\n");
		print("SECTION_FOUND   = $SECTION_FOUND\n");
		print("LINE_FOUND      = $LINE_FOUND\n");
		print("FOUND_INDEX     = $FOUND_INDEX\n");
		print("FOUND_LINES     = @FOUND_LINES\n");
		print("#FOUND_LINES     = $#FOUND_LINES\n");
		print("\n\n");
	}
	
	fileOpen();
	
	# Search each line of the file for $SECT_DESC and then assign
	# the section it's in. The first section header that matches
	# is returned.
	foreach $INLINE (<SRC_FILE1>) {
		chomp($INLINE);
		printf("%3g,%3g,%3g: %s\n", $CURR_LINE, $CURR_INDEX, $SECTION[$CURR_INDEX], $INLINE) if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG );
		if ( $CURR_LINE >= $SECTION[$CURR_INDEX] ) {
			# Only look for $SECT_DESC in the second line of each section
			if ( $FOUND_INDEX < 0 && $INLINE =~ /$SECT_DESC/ && $CURR_LINE == $SECTION[$CURR_INDEX]+1 && $CURR_LINE < $SECTION[$CURR_INDEX+1]) {
				$SECTION_FOUND++;
				$FOUND_INDEX = $CURR_INDEX;
			}
		
			elsif ( $INLINE =~ /$GREP_FOR/ && $CURR_LINE < $SECTION[$FOUND_INDEX+1]) {
				@FOUND_LINE = (split(/\s+/, $INLINE)); # split into array on spaces
				$FOUND_LINES[$LINE_FOUND] = [ @FOUND_LINE ];
				$LINE_FOUND++;
			}
			
			if ( $CURR_INDEX < $#SECTION && $CURR_LINE+1 == $SECTION[$CURR_INDEX+1]) {
				$CURR_INDEX++;
				last if(scalar(@FOUND_LINES) > 0);
			}
		}
		$CURR_LINE++;
	}
	
	fileClose();
	
	if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG ) {
		$" = "|"; # Change array element separator
		print("\n< grepSection   - END @SECTION\n");
		print("SECT_DESC       = $SECT_DESC\n");
		print("GREP_FOR        = $GREP_FOR\n");
		print("CURR_INDEX      = $CURR_INDEX\n");
		print("CURR_LINE       = $CURR_LINE\n");
		print("LINE_FOUND      = $LINE_FOUND\n");
		print("SECTION_FOUND   = $SECTION_FOUND\n");
		print("FOUND_INDEX     = $FOUND_INDEX\n");
		print("FOUND_LINES      = @FOUND_LINES\n");
		print("#FOUND_LINES     = $#FOUND_LINES\n");
		print("\n\n");
	}
	
	return(@FOUND_LINES);
}


# Returns an array of arrays with the lines containing $GREP_FOR
# from the specified section. Only searches the first section found 
# containing the $SECT_DESC. Merges wrapped with previous line if the wrapped
# line started with a space: "^ " signifies line wrapped in this case
#
# Input:    1 - section descriptor
#           2 - search for string (GREP_FOR)
#           3 - number of header lines to skip before attempting line grep
# 
# Output:   Array with lines (each line is a pre-tokenized array) containing search criteria
#
# Requires: initFileSections()
sub grepSectionLinesWrap {
	my $SECT_DESC         = $_[0];
	my $GREP_FOR          = $_[1];
	my $LINES_SKIP        = $_[2] ? $_[2] : 0;  # default skipped lines to 0 if unspecified
	my @LINES_READ        = ();
	my (@FOUND_LINES, @FOUND_LINE);
	my $CURR_LINE         = 1;
	my $CURR_INDEX        = 0;
	my $FOUND_INDEX       = -1;
	my $SECTION_FOUND     = 0;
	my $LINE_FOUND        = 0;

	fileOpen();
	
	# Search each line of the file for $SECT_DESC and then assign
	# the section it's in. The first section header that matches
	# is returned.
	foreach $INLINE (<SRC_FILE1>) {
		chomp($INLINE);
		printf("%3g,%3g,%3g: %s\n", $CURR_LINE, $CURR_INDEX, $SECTION[$CURR_INDEX], $INLINE) if ( $OPT_LOGLEVEL >= LOGLEVEL_DEBUG );
		if ($CURR_LINE >= $SECTION[$CURR_INDEX] ) {
			# Only look for $SECT_DESC in the second line of each section
			if ($FOUND_INDEX < 0 && $INLINE =~ /$SECT_DESC/ && $CURR_LINE == $SECTION[$CURR_INDEX]+1 && $CURR_LINE < $SECTION[$CURR_INDEX+1]) {
				$SECTION_FOUND++;
				$FOUND_INDEX = $CURR_INDEX;
			}
			elsif ($FOUND_INDEX >= 0 && $LINES_SKIP) {
				$LINES_SKIP--; # count down to zero, skip number of lines specified.
			}
			elsif ( $FOUND_INDEX >= 0 && $INLINE =~ /$GREP_FOR/ && $CURR_LINE < $SECTION[$FOUND_INDEX+1]) {
				if($INLINE =~ /^ /) {       # if wrap line is the first line, then problems will happen
				  print("found wrapped line: $INLINE\n") if $OPT_LOGLEVEL >= LOGLEVEL_DEBUG;
					$INLINE =~ s/^ //;                   # remove the leading space from the line
					
					my $LAST_LINE = pop(@LINES_READ);    # pop last line
					$LAST_LINE =~ s/\n//;                # remove newline
					$LAST_LINE = $LAST_LINE.$INLINE;     # concatenate the two lines to be the last line
					
					print("push composited line: $LAST_LINE\n") if $OPT_LOGLEVEL >= LOGLEVEL_DEBUG;
					push(@LINES_READ, $LAST_LINE);       # save the composite line to the array
				}
				else {
					# first line and/or grepped line should not be a wrapped line (no wrap should be here)
					print("push else: $INLINE\n") if $OPT_LOGLEVEL >= LOGLEVEL_DEBUG; 
		      push(@LINES_READ, $INLINE);          # save the last line
				}
			}
			
			if ( $CURR_INDEX < $#SECTION && $CURR_LINE+1 == $SECTION[$CURR_INDEX+1]) {
				$CURR_INDEX++;
			}
		}
		$CURR_LINE++;
		last if(scalar(@LINES_READ) > 0 && $CURR_LINE == $SECTION[$CURR_INDEX]);
	}
	
	fileClose();
	
	# copy the lines read and place into an array of arrays with the each array row split on whitespace
	$LINE_FOUND = 0;
	foreach $INLINE (@LINES_READ) {
		print("$INLINE\n") if $OPT_LOGLEVEL >= LOGLEVEL_DEBUG;
		@FOUND_LINE = (split(/\s+/, $INLINE)); # split into array on whitespace
		$FOUND_LINES[$LINE_FOUND] = [ @FOUND_LINE ];
		$LINE_FOUND++;
	}
	
	return(@FOUND_LINES);
}


##############################################################################

=head1 CONTRIBUTORS

Jason Record E<lt>jrecord@novell.comE<gt>

Douglas Kimball E<lt>dkimball@novell.comE<gt>

Tregaron Bayly E<lt>tbayly@novell.comE<gt>

=head1 COPYRIGHT

Copyright (C) 2008,2009,2010 Novell, Inc.

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

