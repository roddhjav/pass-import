#!/usr/bin/make -f
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
# SPDX-License-Identifier: GPL-3.0-or-later

EXT = import
DESTDIR ?= /

all:
	@python3 setup.py build
	@echo "pass-import was built successfully. You can now install it wit \"make install\""

install:
	@python3 setup.py install --root="${DESTDIR}" --optimize=1 --skip-build
	@echo "pass-import is installed succesfully"

local:
	@python3 setup.py install --user --optimize=1
	@echo "pass-import is localy installed succesfully."
	@echo "Remember to set PASSWORD_STORE_ENABLE_EXTENSIONS to 'true' for the extension to be enabled."

tests:
	@green -vvv --run-coverage --termcolor --processes $(shell nproc)
	@coverage html

lint:
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t pydocstyle -t pycodestyle \
		-t profile-validator -t pyflakes -t pyroma \
		pass_${EXT}
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t pydocstyle -t pycodestyle \
		-t profile-validator -t pyflakes -t pyroma \
		share
	@prospector --profile tests/assets/prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t mypy -t pydocstyle -t pycodestyle \
		-t profile-validator -t pyflakes -t pyroma \
		tests

security:
	@bandit --ini .bandit -r pass_${EXT} tests setup.py share

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
	@python3 setup.py sdist bdist_wheel
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
