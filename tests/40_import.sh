#!/usr/bin/env bash

export test_description="Testing 'pass import'"

source ./setup
test_cleanup

PASSWORDS_MANAGERS=("1password" "1password4" "chrome" "dashlane" "enpass"
    "fpm" "gorilla" "keepass" "keepassx" "keepassxc" "keepasscsv"
    "lastpass" "passwordexporter" "pwsafe" "revelation" "roboform")

XML="fpm keepassx keepass pwsafe revelation kedpm"

for manager in "${PASSWORDS_MANAGERS[@]}"; do
	test_init "$manager" &> /dev/null
    _in "$XML" "$manager" && ext="xml" || ext="csv"
	test_expect_success "Testing $manager database" "
        _pass import $manager $PLAIN_DB/$manager.$ext
    "
done

test_done
