PREFIX ?= /usr
DESTDIR ?= /
LIBDIR ?= $(PREFIX)/lib
BINDIR ?= $(PREFIX)/bin
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
MANDIR ?= $(PREFIX)/share/man

BASHCOMPDIR ?= /etc/bash_completion.d
ZSHCOMPDIR ?= $(PREFIX)/share/zsh/site-functions

all:
	@python3 setup.py build
	@echo
	@echo "pass-import was built successfully. You can now install it wit \"make install\""
	@echo

install:
	@install -v -d "$(DESTDIR)$(MANDIR)/man1"
	@install -v -d "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/"
	@install -v -d "$(DESTDIR)$(BASHCOMPDIR)" "$(DESTDIR)$(ZSHCOMPDIR)"
	@install -v -m 0755 "scripts/import.bash" "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/import.bash"
	@install -v -m 0755 "scripts/pimport" "$(DESTDIR)$(BINDIR)/pimport"
	@install -v -m 0644 "docs/pass-import.1" "$(DESTDIR)$(MANDIR)/man1/pass-import.1"
	@install -v -m 0644 "completion/pass-import.bash" "$(DESTDIR)$(BASHCOMPDIR)/pass-import"
	@install -v -m 0644 "completion/pass-import.zsh" "$(DESTDIR)$(ZSHCOMPDIR)/_pass-import"
	@python3 setup.py install --root="$(DESTDIR)" --optimize=1 --skip-build
	@echo
	@echo "pass-import is installed succesfully"
	@echo

uninstall:
	@rm -vf \
		"$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/import.bash" \
		"$(DESTDIR)$(BINDIR)/pimport" \
		"$(DESTDIR)$(MANDIR)/man1/pass-import.1" \
		"$(DESTDIR)$(MANDIR)/man1/pimport.1" \
		"$(DESTDIR)$(BASHCOMPDIR)/pass-import" \
		"$(DESTDIR)$(ZSHCOMPDIR)/_pass-import" \
		"$(DESTDIR)$(BASHCOMPDIR)/pimport" \
		"$(DESTDIR)$(ZSHCOMPDIR)/_pimport"

PASSWORD_STORE_DIR ?= $(HOME)/.password-store
PASSWORD_STORE_EXTENSIONS_DIR ?= $(PASSWORD_STORE_DIR)/.extensions
local:
	@install -v -d "$(DESTDIR)$(PASSWORD_STORE_EXTENSIONS_DIR)/"
	@install -v -m 0755 "import.bash" "$(DESTDIR)$(PASSWORD_STORE_EXTENSIONS_DIR)/import.bash"
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
		-t dodgy -t mccabe -t pep257 -t pep8 \
		-t profile-validator -t pyflakes -t pyroma \
		pass_import/
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t pep257 -t pep8 \
		-t profile-validator -t pyflakes -t pyroma \
		docs/updatedoc.py setup.py
	@prospector --profile tests/assets/prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t mypy -t pep257 -t pep8 \
		-t profile-validator -t pyflakes -t pyroma \
		tests/

security:
	@bandit --ini .bandit -r pass_import tests setup.py docs/updatedoc.py

export PYTHONPATH = ./
docs:
	@python3 docs/updatedoc.py

clean:
	@rm -rf __pycache__/ .mypy_cache/ .ropeproject/ htmlcov/ \
		pass_import/**/__pycache__/ tests/**/__pycache__/ \
		tests/assets/test-results/ tests/assets/gnupg/random_seed \
		.coverage config.json

.PHONY: install uninstall local tests lint security docs clean
