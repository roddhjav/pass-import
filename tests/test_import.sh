#!/usr/bin/env bash

export test_description="Testing 'pass import'"
cd tests
source ./commons.sh
test_cleanup

mapfile -t PASSWORDS_MANAGERS < <(_pass import --list --quiet)
XML="fpm keepassx keepass pwsafe revelation kedpm"

for manager in "${PASSWORDS_MANAGERS[@]}"; do
    test_init "$manager" &> /dev/null
    _in "$XML" "$manager" && ext=".xml" || ext=".csv"
    [[ "$manager" =~ "apple-keychain" ]] && ext=".txt"
    [[ "$manager" =~ "pif" ]] && ext=".1pif"
    [[ "$manager" == "enpass6" ]] && ext=".json"
    [[ "$manager" == "networkmanager" ]] && ext=""
	test_expect_success "Testing $manager database" "
        _pass import $manager $DB/$manager$ext --all
    "
done

test_done
