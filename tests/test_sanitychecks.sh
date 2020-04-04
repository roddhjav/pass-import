#!/usr/bin/env bash

export test_description="Testing 'pass import'"
cd tests
source ./commons.sh

test_expect_success "Testing store not initialized" "
    test_must_fail _pass import bitwarden $DB/bitwarden.csv
    "

test_init 'sanitychecks' &> /dev/null
# test_expect_success "Testing read password from stdin" "
#     echo $MASTERPASSWORD | _pass import keepass $DB/keepass.kdbx
#     "

test_expect_success 'Testing import from not a file' '
    test_must_fail _pass import lastpass not-a-file
    '

test_expect_success 'Testing corner cases' '
    test_must_fail _pass import --not-an-option &&
    test_must_fail _pass import not-a-manager &&
    _pass import --list
    '

test_expect_success 'Testing help message' '
    _pass import --help | grep "[manager] [file]" &&
    _pass import --version | grep "pass import"
    '

test_done
