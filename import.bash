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
IMPORTERS=( "1password" "fpm" "gorrilla" "kedpm" "keepass" "keepass2csv"
			"keepassx" "kwallet" "lastpass" "password-exporter" "pwsafe" 
			"revelation" "roboform")

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
	        Import data to a password store repository.
	        ARG depends of the importer script.
	        <importer> can be: ${!IMPORTERS[@]}

	Options:
	    -v, --version  Show version information.
	    -h, --help	   Print this help message and exit.
	    
	More information may be found in the pass-import(1) man page.
	_EOF
}

cmd_import() {
	if in_array "$1" "${IMPORTERS[@]}"; then
		importer=$(find "$IMPORTER_DIR/${1}2pass".*)
		[[ ! -x "$importer" ]] && die "Unable to find $importer"
		"$importer" "$@"
	local importer_path importer="$1"; shift;
	[[ -z "$importer" ]] && _die "$PROGRAM $COMMAND <importer> [ARG]"
	check_sneaky_paths "$importer"
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
