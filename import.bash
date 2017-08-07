#!/usr/bin/env bash
# Import manager - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017 Alexandre PUJOL <alexandre@pujol.io>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

readonly PASSWORDS_MANAGERS=("1password" "chrome" "dashlane" "enpass" "fpm"
	"gorilla" "kedpm" "keepass" "keepass2csv" "keepassx" "kwallet" "lastpass"
	"password-exporter" "pwsafe" "revelation" "roboform")

#
# Common colors and functions
#
readonly green='\e[0;32m'
readonly yellow='\e[0;33m'
readonly magenta='\e[0;35m'
readonly Bold='\e[1m'
readonly Bred='\e[1;31m'
readonly Bgreen='\e[1;32m'
readonly Byellow='\e[1;33m'
readonly Bmagenta='\e[1;35m'
readonly reset='\e[0m'
_message() { [ "$QUIET" = 0 ] && echo -e " ${Bold} . ${reset} ${*}" >&2; }
_warning() { [ "$QUIET" = 0 ] && echo -e " ${Byellow} w ${reset} ${yellow}${*}${reset}" >&2; }
_success() { [ "$QUIET" = 0 ] && echo -e " ${Bgreen}(*)${reset} ${green}${*}${reset}" >&2; }
_error() { echo -e " ${Bred}[x]${reset} ${Bold}Error :${reset} ${*}" >&2; }
_die() { _error "${@}" && exit 1; }
_verbose() { [ "$VERBOSE" = 0 ] || echo -e " ${Bmagenta} . ${reset} ${magenta}pass${reset} ${*}" >&2; }

_ensure_dependencies() {
	command -v "xpath" &>/dev/null || _die "$PROGRAM $COMMAND requires xpath"
}

cmd_import_verion() {
	cat <<-_EOF
	$PROGRAM $COMMAND - A generic importer extension for pass

	Vesion: 0.2
	_EOF
}

cmd_import_usage() {
	cmd_import_verion
	echo
	cat <<-_EOF
	Usage:
	    $PROGRAM $COMMAND <importer> [ARG]
	        Import data to a password store.
	        ARG depends of the importer script.
	        <importer> can be: ${!IMPORTERS[@]}

	Options:
	    -v, --version  Show version information.
	    -h, --help	   Print this help message and exit.

	More information may be found in the pass-import(1) man page.
	_EOF
}

#
# Helpers tools and fucntions
#

in_array() {
	local needle=$1; shift
	local item
	for item in "${@}"; do
		[[ "${item}" == "${needle}" ]] && return 0
	done
	return 1
}

cmd_import() {
	local importer_path importer="$1"; shift;
	[[ -z "$importer" ]] && _die "$PROGRAM $COMMAND <importer> [ARG]"

	check_sneaky_paths "$importer"
	if in_array "$importer" "${!IMPORTERS[@]}"; then
		importer_path=$(find "$IMPORTER_DIR/${importer}2pass".* 2> /dev/null)
		[[ -x "$importer_path" ]] || _die "Unable to find $importer_path"
		_ensure_dependencies "$importer"
		"${IMPORTERS[$importer]}" "$importer_path" "$@"
	else
		_die "$importer is not a supported importer"
	fi
}

# Check dependencies are present or bail out
_ensure_dependencies

# Global options
VERBOSE=0
QUIET=0

# Getopt options
small_arg="vhVq"
long_arg="verbose,help,version,quiet"
opts="$($GETOPT -o $small_arg -l $long_arg -n "$PROGRAM $COMMAND" -- "$@")"
err=$?
eval set -- "$opts"
while true; do case $1 in
	-q|--quiet) QUIET=1; VERBOSE=0; shift ;;
	-v|--verbose) VERBOSE=1; shift ;;
	-h|--help) shift; cmd_import_usage; exit 0 ;;
	-V|--version) shift; cmd_import_verion; exit 0 ;;
	--) shift; break ;;
esac done

[[ $err -ne 0 ]] && cmd_import_usage && exit 1
cmd_import "$@"
