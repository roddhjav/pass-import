#!/usr/bin/env bash

export test_description="Testing 'pass import'"

source ./setup
test_cleanup

PASSWORDS_MANAGERS=("1password" "1password4" "1password4pif" "bitwarden"
    "chrome" "dashlane" "enpass" "fpm" "gorilla" "kedpm" "keepass" "keepassx"
    "keepassxc" "keepasscsv" "lastpass" "networkmanager" "passwordexporter"
    "pwsafe" "revelation" "roboform")

XML="fpm keepassx keepass pwsafe revelation kedpm"

for manager in "${PASSWORDS_MANAGERS[@]}"; do
	test_init "$manager" &> /dev/null
    _in "$XML" "$manager" && ext=".xml" || ext=".csv"
    [[ "$manager" =~ "pif" ]] && ext=".1pif"
    [[ "$manager" == "networkmanager" ]] && ext=""
	test_expect_success "Testing $manager database" "
        _pass import $manager $DB/$manager$ext --extra
    "
done

test_done
