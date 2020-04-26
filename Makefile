PREFIX ?= /usr
DESTDIR ?= /
BINDIR ?= $(PREFIX)/bin
LIBDIR ?= $(PREFIX)/lib
MANDIR ?= $(PREFIX)/share/man
PYTHON ?= yes

SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions

BASHCOMPDIR ?= $(PREFIX)/share/bash-completion/completions
ZSHCOMPDIR ?= $(PREFIX)/share/zsh/site-functions

all:
	@[ "$(PYTHON)" = "yes" ] || exit 0; python3 setup.py build
	@echo
	@echo "pass-import was built successfully. You can now install it wit \"make install\""
	@echo

install:
	@install -vd "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/" "$(DESTDIR)$(BINDIR)/" \
				 "$(DESTDIR)$(MANDIR)/man1" "$(DESTDIR)$(BASHCOMPDIR)" \
				 "$(DESTDIR)$(ZSHCOMPDIR)"
	@install -vm 0755 scripts/import.bash "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/import.bash"
	@install -vm 0755 scripts/pimport "$(DESTDIR)$(BINDIR)/pimport"
	@install -vm 0644 docs/pass-import.1 "$(DESTDIR)$(MANDIR)/man1/pass-import.1"
	@install -vm 0644 docs/pimport.1 "$(DESTDIR)$(MANDIR)/man1/pimport.1"
	@install -vm 0644 completion/pass-import.bash "$(DESTDIR)$(BASHCOMPDIR)/pass-import"
	@install -vm 0644 completion/pass-import.zsh "$(DESTDIR)$(ZSHCOMPDIR)/_pass-import"
	@install -vm 0644 completion/pimport.bash "$(DESTDIR)$(BASHCOMPDIR)/pimport"
	@install -vm 0644 completion/pimport.zsh "$(DESTDIR)$(ZSHCOMPDIR)/_pimport"
	@[ "$(PYTHON)" = "yes" ] || exit 0; python3 setup.py install --root="$(DESTDIR)" --optimize=1 --skip-build
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
	@install -vd "$(DESTDIR)$(PASSWORD_STORE_EXTENSIONS_DIR)/"
	@install -vm 0755 import.bash "$(DESTDIR)$(PASSWORD_STORE_EXTENSIONS_DIR)/import.bash"
	@python3 setup.py install --user --optimize=1
	@echo
	@echo "pass-import is localy installed succesfully."
	@echo "Remember to set PASSWORD_STORE_ENABLE_EXTENSIONS to 'true' for the extension to be enabled."
	@echo "Warning, because it is a local installation, there is no manual page or shell completion."


tests:
	@python3 -m green -vvv --run-coverage --termcolor --processes $(shell nproc)
	@coverage html

lint:
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t pep257 -t pep8 -t pylint \
		-t profile-validator -t pyflakes -t pyroma \
		pass_import/
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t pep257 -t pep8 -t pylint \
		-t profile-validator -t pyflakes -t pyroma \
		docs/updatedoc.py setup.py
	@prospector --profile tests/assets/prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t mypy -t pep257 -t pep8 -t pylint \
		-t profile-validator -t pyflakes -t pyroma \
		tests/

security:
	@bandit --ini .bandit -r pass_import tests setup.py docs/updatedoc.py

export PYTHONPATH = ./
docs:
	@python3 docs/updatedoc.py

clean:
	@rm -rf .coverage .mypy_cache .pybuild .ropeproject build config.json \
		debian/.debhelper debian/debhelper* debian/pass-extension-import* \
		dist *.egg-info htmlcov pass_import/**/__pycache__/ */__pycache__/ \
		__pycache__ session.baseline.sqlite session.sqlite \
		tests/assets/gnupg/random_seed tests/assets/test-results/ \
		tests/**/__pycache__/

.PHONY: install uninstall local tests lint security docs clean
