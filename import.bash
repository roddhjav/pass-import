#!/usr/bin/env bash

# Copyright (C) 2017 Alexandre Pujol <alexandre@pujol.io>. All Rights Reserved.
# This file is licensed under the GPLv2+. Please see COPYING for more information.

# Import manager - Password Store Extenssion (https://www.passwordstore.org/)

IMPORTER_DIR="${PASSWORD_STORE_IMPORTER_DIR:-/usr/lib/password-store/importers}"
IMPORTERS=( "1password" "fpm" "gorrilla" "kedpm" "keepass" "keepass2csv"
			"keepassx" "kwallet" "lastpass" "password-exporter" "pwsafe" 
			"revelation" "roboform")

in_array() {
	local needle=$1; shift
	local item
	for item in "${@}"; do
		[[ ${item} == ${needle} ]] && return 0
	done
	return 1
}

cmd_import_usage() {
	cat <<-_EOF
	Usage:
	    $PROGRAM import <importer> [ARG] 
	        Import data to a password store repository.
	        ARG depends of the importer script.
	        <importer> can be: ${IMPORTERS[@]}

	More information may be found in the pass-import(1) man page.
	_EOF
}

cmd_import() {
	check_sneaky_paths "$1"
	local importer
	if in_array "$1" ${IMPORTERS[@]}; then
		importer=$(find "$IMPORTER_DIR/${1}2pass".*)
		[[ ! -x "$importer" ]] && die "Unable to find $importer"
		shift
		"$importer" $@
	else
		cmd_import_usage
	fi
}

cmd_import "$@"
