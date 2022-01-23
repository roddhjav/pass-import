#!/usr/bin/env bash
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
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

cmd_import() {
	local ret=0
	export PASSWORD_STORE_DIR=$PREFIX GIT_DIR PASSWORD_STORE_GPG_OPTS
	export X_SELECTION CLIP_TIME PASSWORD_STORE_UMASK GENERATED_LENGTH
	export CHARACTER_SET CHARACTER_SET_NO_SYMBOLS EXTENSIONS PASSWORD_STORE_KEY
	export PASSWORD_STORE_ENABLE_EXTENSIONS PASSWORD_STORE_SIGNING_KEY
	export GNUPGHOME PYTHONIOENCODING="UTF-8" _PASSWORD_STORE_EXTENSION="$COMMAND"
	if [[ -t 0 ]]; then
		python3 -m pass_import "$@"
		ret=$?
	else
		cat | python3 -m pass_import "$@"
		ret=$?
	fi
	return $ret
}

cmd_import "$@"
exit $?
