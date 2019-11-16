# pass-import completion file for bash

PASSWORD_STORE_EXTENSION_COMMANDS+=(import)

__password_store_extension_complete_import() {
	# importers begin
	local importers=(1password 1password4 1password4pif aegis andotp 
		apple-keychain bitwarden buttercup chrome chromesqlite csv dashlane 
		encryptr enpass enpass6 fpm gnome-authenticator gnome-keyring gorilla 
		kedpm keepass keepass-csv keepass-xml keepassx keepassx2 keepassx2-csv 
		keepassxc keepassxc-csv keeper lastpass myki networkmanager pass 
		passpie passwordexporter pwsafe revelation roboform upm)
	# importers end
	local args=(-h --help -p --path -a --all -c --clean -C --convert -s --sep
		  --cols --config -l --list -f --force -q --quiet -v --verbose -V
		  --version)
	local lastarg="${COMP_WORDS[$COMP_CWORD-1]}"
	if [[ $lastarg == "-p" || $lastarg == "--path" ]]; then
		_pass_complete_folders
		compopt -o nospace
	elif [[ $COMP_CWORD -gt 2 ]]; then
		COMPREPLY+=($(compgen -W "${args[*]}" -- ${cur}))
	else
		COMPREPLY+=($(compgen -W "${importers[*]} ${args[*]}" -- ${cur}))
	fi
}
