#!/usr/bin/make -f
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
# SPDX-License-Identifier: GPL-3.0-or-later

EXT = import
PREFIX ?= /usr
DESTDIR ?=
LIBDIR ?= $(PREFIX)/lib
MANDIR ?= $(PREFIX)/share/man
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
BASHCOMPDIR ?= $(PREFIX)/share/bash-completion/completions
ZSHCOMPDIR ?= $(PREFIX)/share/zsh/site-functions

all:
	@python3 -m build --wheel --no-isolation
	@echo "pass-import was built successfully. You can now install it with \"make install\""

install:
	@python3 -m installer --destdir="$(DESTDIR)" dist/*.whl
	@install -Dm0755 pass_import/import.bash "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/import.bash"
	@install -Dm0644 -t "$(DESTDIR)$(MANDIR)/man1" share/man/man1/pass-import.1 share/man/man1/pimport.1
	@install -Dm0644 -t "$(DESTDIR)$(BASHCOMPDIR)" share/bash-completion/completions/pass-import share/bash-completion/completions/pimport
	@install -Dm0644 -t "$(DESTDIR)$(ZSHCOMPDIR)" share/zsh/site-functions/_pass-import share/zsh/site-functions/_pimport
	@echo "pass-import is installed successfully"

local:
	@pipx install --force .
	@pimport --install-extension
	@echo "pass-import is locally installed successfully."

tests:
	@python3 -m pytest -n auto --cov=pass_import --cov-report=term --cov-report=html

lint:
	@ruff check pass_${EXT} share tests

security:
	@bandit --ini .bandit -r pass_${EXT} tests share

export PYTHONPATH = ./
docs:
	@python3 share --docs
	@pandoc -t man -s -o share/man/man1/pass-${EXT}.1 share/man/man1/pass-${EXT}.md
	@pandoc -t man -s -o share/man/man1/pimport.1 share/man/man1/pimport.md

commitdocs:
	@git add .
	@git commit -S -m "doc: update documentation prior release"

VERSION ?=
GPGKEY ?= 06A26D531D56C42D66805049C5469996F0DF68EC
archive:
	@python3 share --release ${VERSION}
	@git tag v${VERSION} -m "pass-${EXT} v${VERSION}" --local-user=${GPGKEY}
	@git archive \
		--format=tar.gz \
		--prefix=pass-${EXT}-${VERSION}/share/man/man1/ \
		--add-file=share/man/man1/pimport.1 \
		--add-file=share/man/man1/pass-${EXT}.1 \
		--prefix=pass-${EXT}-${VERSION}/ \
		--output=pass-${EXT}-${VERSION}.tar.gz \
		v${VERSION} ':!debian' ':!share/man/man1/*.md'
	@gpg --armor --default-key ${GPGKEY} --detach-sig pass-${EXT}-${VERSION}.tar.gz
	@gpg --verify pass-${EXT}-${VERSION}.tar.gz.asc

PKGNAME := pass-extension-${EXT}
BUILDIR := /home/build/${PKGNAME}
BASEIMAGE := registry.gitlab.com/roddhjav/builders/debian
CTNAME := builder-debian-pass-${EXT}
debian:
	@docker stop ${CTNAME} &> /dev/null || true
	@docker pull ${BASEIMAGE}
	@docker run --rm -tid --name ${CTNAME} --volume ${PWD}:${BUILDIR} \
		--volume ${HOME}/.gnupg:/home/build/.gnupg ${BASEIMAGE} &> /dev/null || true
	@docker exec ${CTNAME} sudo apt-get update -q
	@docker exec ${CTNAME} sudo apt-get install -y \
		dh-python python3-setuptools python3-requests python3-zxcvbn python3-yaml
	@docker exec --workdir=${BUILDIR} ${CTNAME} \
		dpkg-buildpackage -b -d -us -ui --sign-key=${GPGKEY}
	@docker exec ${CTNAME} bash -c 'mv ~/${PKGNAME}*.* ~/${PKGNAME}'
	@docker exec ${CTNAME} bash -c 'mv ~/pass-${EXT}*.* ~/${PKGNAME}'

pip:
	@python3 -m build
	@twine check dist/*
	@gpg --detach-sign -a dist/*
	@twine upload --sign --identity ${GPGKEY} dist/*

release: tests lint security docs commitdocs archive

clean:
	@rm -rf .coverage .mypy_cache .pybuild .ropeproject build config.json \
		debian/.debhelper debian/debhelper* debian/pass-extension-${EXT}* \
		debian/files *.deb *.buildinfo *.changes \
		dist *.egg-info htmlcov pass_${EXT}/**/__pycache__/ */__pycache__/ \
		__pycache__ session.baseline.sqlite session.sqlite \
		tests/assets/gnupg/random_seed tests/assets/test-results/ \
		tests/**/__pycache__/

.PHONY: install uninstall local tests lint security docs commitdocs archive pip debian release clean
