#!/usr/bin/env bash

export test_description="Testing 'pass import'"

source ./setup
test_cleanup

PASSWORDS_MANAGERS=("gorilla" "keepasscsv" "lastpass"  "passwordexporter")

for manager in "${PASSWORDS_MANAGERS[@]}"; do
	test_init "$manager" &> /dev/null
	test_expect_success "Testing $manager database" "
        _pass import $manager $PLAIN_DB/$manager --verbose
    "
done

test_done
