#!/usr/bin/env bash
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
# SPDX-License-Identifier: GPL-3.0-or-later

cmd_import() {
	local run=(python3 -m pass_import)
	# pimport works when pass-import lives in its own venv (pipx, uv tool)
	command -v pimport &>/dev/null && run=(pimport)
	export PASSWORD_STORE_DIR=$PREFIX GIT_DIR PASSWORD_STORE_GPG_OPTS
	export X_SELECTION CLIP_TIME PASSWORD_STORE_UMASK GENERATED_LENGTH
	export CHARACTER_SET CHARACTER_SET_NO_SYMBOLS EXTENSIONS PASSWORD_STORE_KEY
	export PASSWORD_STORE_ENABLE_EXTENSIONS PASSWORD_STORE_SIGNING_KEY
	export GNUPGHOME PYTHONIOENCODING="UTF-8" _PASSWORD_STORE_EXTENSION="$COMMAND"
	"${run[@]}" "$@"
}

cmd_import "$@"
exit $?
