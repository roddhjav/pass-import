PREFIX ?= /usr
DESTDIR ?=
LIBDIR ?= $(PREFIX)/lib
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
IMPORTERS_DIR ?= $(LIBDIR)/password-store/importers
MANDIR ?= $(PREFIX)/share/man

all:
	@echo "Pass Import is a shell script, so there is nothing to do. Try \"make install\" instead."

install-common:
	@install -v -d "$(DESTDIR)$(MANDIR)/man1" && install -m 0644 -v pass-import.1 "$(DESTDIR)$(MANDIR)/man1/pass-import.1"

install-importers:
	@install -v -d "$(DESTDIR)$(IMPORTERS_DIR)/"
	@install -Dm0755 -t "$(DESTDIR)$(IMPORTERS_DIR)/" importers/*

install: install-common install-importers
	@install -v -d "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/"
	@install -Dm0755 import.bash "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/import.bash"

uninstall:
	@rm -vrf \
		"$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/import.bash" \
		"$(DESTDIR)$(MANDIR)/man1/pass-import.1" \

.PHONY: install uninstall install-common install-importers
