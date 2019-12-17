PROG ?= import
PREFIX ?= /usr
DESTDIR ?= /
LIBDIR ?= $(PREFIX)/lib
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
MANDIR ?= $(PREFIX)/share/man

BASHCOMPDIR ?= /etc/bash_completion.d
ZSHCOMPDIR ?= $(PREFIX)/share/zsh/site-functions

all:
	@python3 setup.py build
	@echo
	@echo "pass-$(PROG) was built successfully. You can now install it with \"make install\""
	@echo
	@echo "To run pass $(PROG) one needs to have some tools installed on the system:"
	@echo "     pass, python3 and python3-defusedxml"

install:
	@install -v -d "$(DESTDIR)$(MANDIR)/man1"
	@install -v -d "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/"
	@install -v -d "$(DESTDIR)$(BASHCOMPDIR)" "$(DESTDIR)$(ZSHCOMPDIR)"
	@install -v -m 0755 "$(PROG).bash" "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/$(PROG).bash"
	@install -v -m 0644 "pass-$(PROG).1" "$(DESTDIR)$(MANDIR)/man1/pass-$(PROG).1"
	@install -v -m 0644 "completion/pass-$(PROG).bash" "$(DESTDIR)$(BASHCOMPDIR)/pass-$(PROG)"
	@install -v -m 0644 "completion/pass-$(PROG).zsh" "$(DESTDIR)$(ZSHCOMPDIR)/_pass-$(PROG)"
	@python3 setup.py install --root="$(DESTDIR)" --optimize=1 --skip-build
	@echo
	@echo "pass-$(PROG) is installed succesfully"
	@echo

uninstall:
	@rm -vrf \
		"$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/$(PROG).bash" \
		"$(DESTDIR)$(MANDIR)/man1/pass-$(PROG).1" \
		"$(DESTDIR)$(BASHCOMPDIR)/pass-$(PROG)" \
		"$(DESTDIR)$(ZSHCOMPDIR)/_pass-$(PROG)"


PASSWORD_STORE_DIR ?= $(HOME)/.password-store
PASSWORD_STORE_EXTENSIONS_DIR ?= $(PASSWORD_STORE_DIR)/.extensions
local:
	@install -v -d "$(DESTDIR)$(PASSWORD_STORE_EXTENSIONS_DIR)/"
	@install -v -m 0755 "$(PROG).bash" "$(DESTDIR)$(PASSWORD_STORE_EXTENSIONS_DIR)/$(PROG).bash"
	@python3 setup.py install --user --prefix= --optimize=1
	@echo
	@echo "pass-$(PROG) is localy installed succesfully."
	@echo "Remember to set to 'true' PASSWORD_STORE_ENABLE_EXTENSIONS for the extension to be enabled."
	@echo "Warning, because it is a local installation, there is no manual page or shell completion."


tests:
	@python3 -m green -vvv --run-coverage --termcolor --processes $(shell nproc)
	@coverage html

lint:
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t mypy -t pep257 -t pep8 \
		-t profile-validator -t pyflakes -t pyroma \
		pass_import/ docs/.updatedoc.py setup.py
	@prospector --profile tests/.prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t mypy -t pep257 -t pep8 \
		-t profile-validator -t pyflakes -t pyroma \
		tests/

security:
	@bandit --ini .bandit -r pass_import tests setup.py docs/.updatedoc.py

clean:
	@rm -rf __pycache__/ .mypy_cache/ .ropeproject/ htmlcov/ \
		pass_import/**/__pycache__/ tests/**/__pycache__/ \
		tests/assets/test-results/ tests/assets/gnupg/random_seed \
		.coverage config.json

.PHONY: install uninstall local tests lint security clean
