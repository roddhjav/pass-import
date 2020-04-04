#!/usr/bin/env bash

export test_description="Testing 'pass import'"
cd tests
source ./commons.sh
test_cleanup

mapfile -t PASSWORDS_MANAGERS < <(_pass import --list --quiet)
IGNORE="csv gnome-keyring keepass keepassx2 keepassxc"

_extension() {
    local manager="$1"
    case $manager in
    	fpm|kedpm|keepass-xml|keepassx|pwsafe|revelation) echo '.xml' ;;
    	enpass6|andotp|aegis|gnome-authenticator) echo '.json' ;;
        networkmanager|pass) echo '' ;;
        apple-keychain) echo '.txt' ;;
        1password4pif) echo '.1pif' ;;
    	passpie) echo '.yml' ;;
    	*) echo '.csv' ;;
    esac
}

for manager in "${PASSWORDS_MANAGERS[@]}"; do
    if _in "$IGNORE" "$manager"; then
        continue
    fi
    ext=$(_extension "$manager")
    test_init "$manager" &> /dev/null
	test_expect_success "Testing $manager database" "
        _pass import $manager $DB/$manager$ext --all
    "
done

test_done
