#!/usr/bin/env bash
# pass import - Password Store Extension (https://www.passwordstore.org/)
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

readonly VERSION="2.0"
readonly LIBDIR="${PASSWORD_STORE_LIBDIR:-/usr/lib/password-store/import}"
readonly PASSWORDS_MANAGERS=("onepassword" "chrome" "dashlane" "enpass" "fpm"
	"gorilla" "kedpm" "keepass" "keepasscsv" "keepassx" "kwallet" "lastpass"
	"passwordexporter" "pwsafe" "revelation" "roboform")

readonly green='\e[0;32m'
readonly Bold='\e[1m'
readonly Bred='\e[1;31m'
readonly Bgreen='\e[1;32m'
readonly reset='\e[0m'
_message() { [ "$QUIET" = 0 ] && echo -e " ${Bold} . ${reset} ${*}" >&2; }
_success() { [ "$QUIET" = 0 ] && echo -e " ${Bgreen}(*)${reset} ${green}${*}${reset}" >&2; }
_error() { echo -e " ${Bred}[x]${reset} ${Bold}Error:${reset} ${*}" >&2; }
_die() { _error "${@}" && exit 1; }

_ensure_dependencies() {
	command -v "python3" &>/dev/null || _die "$PROGRAM $COMMAND requires python3"
	command -v "${LIBDIR}/import.py" &>/dev/null || _die "$PROGRAM $COMMAND requires ${LIBDIR}/import.py"
}

cmd_import_version() {
	cat <<-_EOF
	$PROGRAM $COMMAND $VERSION - A generic importer extension for pass.
	_EOF
}

cmd_import_usage() {
	cmd_import_version
	echo
	cat <<-_EOF
	Usage:
	    $PROGRAM $COMMAND [[-p folder] [-c] [-e] [-f] | -l] <manager> <file>
	        Import data from most of the password manager. Passwords
	        are imported in the existing default password store, therefore
	        the password store must has been initialized before with 'pass init'

	        <file> is the path to the file that contains the data to import, if
	        empty read the data from stdin.

	        <manager> can be:
	        	onepassword chrome dashlane enpass fpm gorilla
	        	kedpm keepass keepasscsv keepassx kwallet lastpass
	        	passwordexporter pwsafe revelation roboform

	Options:
	    -p, --path     Import the passwords to a specific subfolder.
	    -c, --clean    Clean data before import.
	    -e, --extra    Also import all the extra data present.
	    -l, --list     List the supported password managers.
	    -f, --force    Overwrite existing path.
	    -q, --quiet    Be quiet.
	    -v, --verbose  Be verbose.
	    -V, --version  Show version information.
	    -h, --help	   Print this help message and exit.

	More information may be found in the pass-import(1) man page.
	_EOF
}

in_array() {
	local needle=$1; shift
	local item
	for item in "${@}"; do
		[[ "${item}" == "${needle}" ]] && return 0
	done
	return 1
}

cmd_import_list() {
	_success "The supported password managers are:"
	for manager in "${PASSWORDS_MANAGERS[@]}"; do
		_message "$manager"
	done
}

# Import core function
# $1: Root path in the password store
# $2: Password manager name
# $3: File to import
cmd_import() {
	local path="$1" manager="$2" file="$3"
	[[ -z "$manager" ]] && _die "$PROGRAM $COMMAND [options] <manager> <file>"
	[[ -e "$file" ]] || _die "$PROGRAM $COMMAND [options] <manager> <file>"

	check_sneaky_paths "$path" "$file"
	if in_array "$manager" "${PASSWORDS_MANAGERS[@]}"; then
		export PREFIX PASSWORD_STORE_KEY GIT_DIR PASSWORD_STORE_GPG_OPTS
		export X_SELECTION CLIP_TIME PASSWORD_STORE_UMASK GENERATED_LENGTH
		export CHARACTER_SET CHARACTER_SET_NO_SYMBOLS EXTENSIONS
		export PASSWORD_STORE_ENABLE_EXTENSIONS  PASSWORD_STORE_SIGNING_KEY
		export GNUPGHOME LIBDIR VERBOSE QUIET
		python3 "${LIBDIR}/import.py" "$manager" "$file" "$path" "$CLEANUP" "$FORCE"
		[ $? = 0 ] || _die "importing data from $manager"
	else
		_die "$manager is not a supported password manager"
	fi
}

# Check dependencies are present or bail out
_ensure_dependencies

# Global options
VERBOSE=0
QUIET=0
CLEANUP=0
EXTRA=0
FORCE=0
path=""

# Getopt options
small_arg="vhVqp:lcfe"
long_arg="verbose,help,version,quiet,path:,list,cleanup,force,extra"
opts="$($GETOPT -o $small_arg -l $long_arg -n "$PROGRAM $COMMAND" -- "$@")"
err=$?
eval set -- "$opts"
while true; do case $1 in
	-p|--path) path="$2"; shift 2 ;;
	-c|--cleanup) CLEANUP=1; shift ;;
	-e|--extra) EXTRA=1; shift ;;
	-f|--force) FORCE=1; shift ;;
	-l|--list) shift; cmd_import_list; exit 0 ;;
	-q|--quiet) QUIET=1; VERBOSE=0; shift ;;
	-v|--verbose) VERBOSE=1; shift ;;
	-h|--help) shift; cmd_import_usage; exit 0 ;;
	-V|--version) shift; cmd_import_version; exit 0 ;;
	--) shift; break ;;
esac done

[[ $err -ne 0 ]] && cmd_import_usage && exit 1
cmd_import "$path" "$@"
