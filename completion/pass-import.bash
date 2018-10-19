# pass-import completion file for bash

PASSWORD_STORE_EXTENSION_COMMANDS+=(import)

__password_store_extension_complete_import() {
	local importers=(1password 1password4 1password4pif bitwarden chrome
		chromesqlite dashlane enpass fpm gorilla kedpm keepass keepasscsv
		keepassx keepassx2 keepassxc lastpass networkmanager passwordexporter
		pwsafe revelation roboform)
	local lastarg="${COMP_WORDS[$COMP_CWORD-1]}"
	if [[ $lastarg == "-p" || $lastarg == "--path" ]]; then
		_pass_complete_folders
		compopt -o nospace
	elif  [[ ! $COMP_CWORD -gt 2 ]]; then
		COMPREPLY+=($(compgen -W "${importers[*]} -h --help -p --path -c --clean -e --extra -l --list -f --force -q --quiet -v --verbose -V --version" -- ${cur}))
		_pass_complete_entries
	fi
}
