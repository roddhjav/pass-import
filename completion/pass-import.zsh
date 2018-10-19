# pass-import completion file for zsh

PASSWORD_STORE_EXTENSION_SUBCOMMANDS+=(
	"import:Import data from most of the existing password manager"
)

__password_store_extension_complete_import() {
	local -a subcommands
	subcommands=(1password 1password4 1password4pif bitwarden chrome
		chromesqlite dashlane enpass fpm gorilla kedpm keepass keepasscsv
		keepassx keepassx2 keepassxc lastpass networkmanager passwordexporter
		pwsafe revelation roboform)
	_describe -t commands 'pass import' subcommands
	_arguments : \
		"-p[import the passwords to a specific subfolder]" \
		"--path[import the passwords to a specific subfolder]" \
		"-c[clean data before import]" \
		"--clean[clean data before import]" \
		"-e[also import all the extra data present]" \
		"--extra[also import all the extra data present]" \
		"-l[list the supported password managers]" \
		"--list[list the supported password managers]" \
		"-f[overwrite existing path]" \
		"--force[overwrite existing path]" \
		"-q[be quiet]" \
		"--quiet[be quiet]" \
		"-v[be verbose]" \
		"--verbose[be verbose]" \
		"-V[show version information]" \
		"--version[show version information]" \
		"-h[print help message]" \
		"--help[print help message]"
}
