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

IMPORTER_DIR="${PASSWORD_STORE_IMPORTER_DIR:-/usr/lib/password-store/importers}"

# Dependencies list
P2="python2"; P3="python3"; PERL="perl"; BASH="bash"; RUBY="ruby"

typeset -A IMPORTERS
IMPORTERS=( ["1password"]="$RUBY" ["fpm"]="$PERL" ["gorilla"]="$RUBY" ["kedpm"]="$P2"
			["keepass"]="$P2" ["keepass2csv"]="$P3" ["keepassx"]="$P2" ["kwallet"]="$P2"
			["lastpass"]="$RUBY" ["password-exporter"]="$P2" ["pwsafe"]="$BASH"
			["revelation"]="$P2" ["roboform"]="$RUBY" ["chrome"]="$P3")

#
# Commons color and functions
#
bold='\e[1m'
Bred='\e[1;31m'
reset='\e[0m'
_error() { echo -e " ${Bred}[*]${reset}${bold} Error :${reset} ${*}"; }
_die() { _error "${@}" && exit 1; }

# Check importers dependencies
#
_ensure_dependencies() {
	local importer="$1";
	command -v "${IMPORTERS[$importer]}" &>/dev/null || _die "$PROGRAM $COMMAND $importer requires ${IMPORTERS[$importer]}"
}

in_array() {
	local needle=$1; shift
	local item
	for item in "${@}"; do
		[[ "${item}" == "${needle}" ]] && return 0
	done
	return 1
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

# Global options
opts="$($GETOPT -o vh -l version,help -n "$PROGRAM $COMMAND" -- "$@")"
err=$?
eval set -- "$opts"
while true; do case $1 in
	-h|--help) shift; cmd_import_usage; exit 0 ;;
	-V|--version) shift; cmd_import_verion; exit 0 ;;
	--) shift; break ;;
esac done

[[ $err -ne 0 ]] && cmd_import_usage && exit 1
cmd_import "$@"
