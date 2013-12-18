#!/bin/bash

# Title:       Bash SCA Pattern Template
# Description: A bash template for creating new SCA patterns
# Modified:    2013 Jun 14

##############################################################################
#  Copyright (C) 2013 SUSE Linux Products GmbH
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
#   First Last (flast@suse.com)
#
##############################################################################

##############################################################################
# Module Definition
##############################################################################

LIBS='Core.rc SUSE.rc'
[[ -n "$SPRSRC" ]] && BASHLIB="${SPRSRC}/lib/bash" || BASHLIB="/var/opt/scdiag/patterns/lib/bash"
for LIB in $LIBS; do [[ -s ${BASHLIB}/${LIB} ]] && . ${BASHLIB}/${LIB} || { echo "Error: Library not found - ${BASHLIB}/${LIB}"; exit 5; }; done

##############################################################################
# Overriden (eventually or in part) from Core.rc
##############################################################################

PATTERN_RESULTS=(\
"${PROPERTY_NAME_CLASS}=SLE" \
"${PROPERTY_NAME_CATEGORY}=Category" \
"${PROPERTY_NAME_COMPONENT}=Component" \
"${PROPERTY_NAME_PATTERN_ID}=$(basename $0)" \
"${PROPERTY_NAME_PRIMARY_LINK}=META_LINK_TID" \
"${PROPERTY_NAME_OVERALL}=$GSTATUS" \
"${PROPERTY_NAME_OVERALL_INFO}=None" \
"META_LINK_TID=http://www.suse.com/support/kb/doc.php?id=7000000" \
"META_LINK_BUG=https://bugzilla.novell.com/show_bug.cgi?id=700000" \
)

##############################################################################
# Local Function Definitions
##############################################################################

sub checkSomething {
	printDebug '> checkSomething'
	local RC=0
	local HEADER_LINES=0
	local LINE=''
	local FILE_OPEN='filename.txt'
	local SECTION='CommandToIdentifyFileSection'

	getSection "$FILE_OPEN" "$SECTION" $HEADER_LINES
	if (( $? ))
	then
		LINE=$(echo "$CONTENT" | egrep 'SearchForThisContentInLine')
		if [[ -n "$LINE" ]]
		then
			printDebug '  checkSomething FOUND' "$LINE"
			((RC++))
		fi
	else
		statusUpdate $STATUS_ERROR "ERROR: checkSomething: Cannot fine '$SECTION' section in $FILE_OPEN"
	fi
	printDebug '< checkSomething' "Returns: $RC"
	return $RC
}

##############################################################################
# Main Program Execution
##############################################################################

processOptions "$@"
checkSomething
if (( $? ))
then
	updateStatus $STATUS_CRITICAL "A critical severity is set"
else
	updateStatus $STATUS_ERROR "The pattern does not apply"
fi
printPatternResults

