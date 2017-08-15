#!/usr/bin/env bash

export test_description="Testing 'pass import'"

source ./setup

test_expect_success "Testing store not initialized" "
    test_must_fail _pass import keepass $PLAIN_DB/keepass
    "

test_init "sanitychecks" &> /dev/null
test_expect_success "Testing import from stdin" "
    cat $PLAIN_DB/lastpass | _pass import lastpass --verbose
    "

test_expect_success 'Testing corner cases' '
    test_must_fail _pass import --not-an-option &&
    test_must_fail _pass import not-a-manager &&
    _pass import --list
    '

test_expect_success 'Testing help message' '
    _pass import --help | grep "pass import" &&
    _pass import --version | grep "A generic importer extension for pass."
    '

test_done
