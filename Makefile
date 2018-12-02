PROG ?= import
PREFIX ?= /usr
DESTDIR ?= /
LIBDIR ?= $(PREFIX)/lib
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
MANDIR ?= $(PREFIX)/share/man

BASHCOMPDIR ?= /etc/bash_completion.d

all:
	@python3 setup.py build
	@echo
	@echo "pass-$(PROG) was builded succesfully. You can now install it wit \"make install\""
	@echo
	@echo "To run pass $(PROG) one needs to have some tools installed on the system:"
	@echo "     password-store, python3 and python3-defusedxml"

install:
	@install -v -d "$(DESTDIR)$(MANDIR)/man1"
	@install -v -d "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/"
	@install -v -d "$(DESTDIR)$(BASHCOMPDIR)"
	@install -v -m 0755 "$(PROG).bash" "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/$(PROG).bash"
	@install -v -m 0644 "pass-$(PROG).1" "$(DESTDIR)$(MANDIR)/man1/pass-$(PROG).1"
	@install -v -m 0644 "completion/pass-$(PROG).bash" "$(DESTDIR)$(BASHCOMPDIR)/pass-$(PROG)"
	@python3 setup.py install --root="$(DESTDIR)" --prefix="$(PREFIX)" --optimize=1 --skip-build
	@echo
	@echo "pass-$(PROG) is installed succesfully"
	@echo

uninstall:
	@rm -vrf \
		"$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/$(PROG).bash" \
		"$(DESTDIR)$(MANDIR)/man1/pass-$(PROG).1" \


PASS_TEST_OPTS ?= --verbose --immediate --chain-lint --root=/tmp/sharness
T = $(sort $(wildcard tests/test_*.sh))

tests:
	@python3 setup.py green -vvv --run-coverage --termcolor --processes $(shell nproc)
	@make tests_bash

tests_bash: $(T)

$(T):
	@$@ $(PASS_TEST_OPTS)

lint:
	@prospector --profile .prospector.yaml \
		-t dodgy -t frosted -t mccabe -t mypy -t pep257 -t pep8 \
		-t profile-validator -t pyflakes -t pylint -t pyroma -t vulture \
		pass_import.py setup.py
	@prospector --profile tests/.prospector.yaml \
		-t dodgy -t frosted -t mccabe -t mypy -t pep257 -t pep8 \
		-t profile-validator -t pyflakes -t pylint -t pyroma \
		tests/*.py

clean:
	@rm -vrf tests/test-results/ tests/gnupg/random_seed

.PHONY: install uninstall tests tests_bash $(T) lint clean
