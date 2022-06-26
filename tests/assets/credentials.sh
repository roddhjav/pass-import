#!/usr/bin/env bash
# Read tests secret credentials from the local password store repository and
# export these credentials for use in the test suite.
#

# Usage:
# Export credentials: eval $(./tests/assets/credentials.sh)
# Enable tests: export T_BITWARDEN=true T_LASTPASS=true T_ONEPASSWORD=true

declare -A MANAGERS
MANAGERS=([BITWARDEN]=bitwarden.com
          [LASTPASS]=lastpass.com
          [ONEPASSWORD]=1password.com)

main() {
    local tmp

    for manager in "${!MANAGERS[@]}"; do
    	if tmp="$(pass "Tests/pass-import/${MANAGERS[$manager]}/password")"; then
		    echo "export TESTS_${manager}_PASS='$tmp'"
	    fi
    	if tmp="$(pass "Tests/pass-import/${MANAGERS[$manager]}/login")"; then
		    echo "export TESTS_${manager}_LOGIN='$tmp'"
	    fi
    	if tmp="$(pass "Tests/pass-import/${MANAGERS[$manager]}/key" 2> /dev/null)"; then
		    echo "export TESTS_${manager}_SECRETKEY='$tmp'"
	    fi
    done
}

main
