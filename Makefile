PROG ?= import
PREFIX ?= /usr
DESTDIR ?=
LIBDIR ?= $(PREFIX)/lib
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
EXTENSION_LIB ?= $(LIBDIR)/password-store/$(PROG)
MANDIR ?= $(PREFIX)/share/man

all:
	@echo "pass-$(PROG) is a shell script and does not need compilation, it can be simply executed."
	@echo
	@echo "To install it try \"make install\" instead."
	@echo
	@echo "To run pass $(PROG) one needs to have some tools installed on the system:"
	@echo "     password store"
	@echo "     python3"
	@echo "     python3-defusedxml"

install:
	@install -v -d "$(DESTDIR)$(MANDIR)/man1"
	@install -v -d "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/"
	@install -v -d "$(DESTDIR)$(EXTENSION_LIB)/"
	@trap 'rm -f .import.bash' EXIT; sed "s|/usr/lib|$(LIBDIR)|" "$(PROG).bash" > ".$(PROG).bash" && \
	install -v -m 0755 ".$(PROG).bash" "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/$(PROG).bash"
	@install -v -m 0755 "lib/$(PROG).py" "$(DESTDIR)$(EXTENSION_LIB)/$(PROG).py"
	@install -v -m 0644 "pass-$(PROG).1" "$(DESTDIR)$(MANDIR)/man1/pass-$(PROG).1"
	@echo
	@echo "pass-$(PROG) is installed succesfully"
	@echo

uninstall:
	@rm -vrf \
		"$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/$(PROG).bash" \
		"$(DESTDIR)$(EXTENSION_LIB)" \
		"$(DESTDIR)$(MANDIR)/man1/pass-$(PROG).1" \

tests:
	make -C tests

lint:
	shellcheck -s bash $(PROG).bash

clean:
	@rm -vrf tests/test-results/ tests/gnupg/random_seed

.PHONY: install uninstall tests lint clean
