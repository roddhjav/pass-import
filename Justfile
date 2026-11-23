# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2026 Alexandre Pujol <alexandre@pujol.io>
# SPDX-License-Identifier: GPL-3.0-or-later

# Usage: `just`

# Build settings

destdir := "/"
prefix := "/usr"
extdir := prefix / "lib/password-store/extensions"
build := ".build"
pkgdest := `pwd` / ".pkg"
pkgname := "pass-import"
gpgkey := "06A26D531D56C42D66805049C5469996F0DF68EC"

usage := "
Build variables available:
    build        " + BLUE + "# Build directory (default: " + build + ")" + NORMAL + "
    destdir      " + BLUE + "# Installation destination (default: " + destdir + ")" + NORMAL + "
    prefix       " + BLUE + "# Installation prefix (default: " + prefix + ")" + NORMAL + "
    extdir       " + BLUE + "# Pass system extension directory (default: " + extdir + ")" + NORMAL + "
    pkgdest      " + BLUE + "# Package output directory (default: " + pkgdest + ")" + NORMAL + "
"

# Show this help message
help:
	@just --list --unsorted
	@printf "%s\n" "{{usage}}"

# Build the python wheel
[group('build')]
build:
	@python3 -m build --wheel --no-isolation --outdir {{build}}

# Generate the man pages
[group('build')]
man:
	@pandoc -t man -s -o share/man/man1/pass-import.1 share/man/man1/pass-import.md
	@pandoc -t man -s -o share/man/man1/pimport.1 share/man/man1/pimport.md

# Install the python package
[group('install')]
install-python:
	@python3 -m installer --destdir="{{destdir}}" {{build}}/*.whl

# Install the pass extension, the man pages and the shell completions
[group('install')]
install-data:
	@install -Dm0755 pass_import/import.bash "{{destdir}}/{{extdir}}/import.bash"
	@install -Dm0644 -t "{{destdir}}/{{prefix}}/share/man/man1" share/man/man1/pass-import.1 share/man/man1/pimport.1
	@install -Dm0644 -t "{{destdir}}/{{prefix}}/share/bash-completion/completions" share/bash-completion/completions/pass-import share/bash-completion/completions/pimport
	@install -Dm0644 -t "{{destdir}}/{{prefix}}/share/zsh/site-functions" share/zsh/site-functions/_pass-import share/zsh/site-functions/_pimport

# Install pass-import
[group('install')]
install: install-python install-data

# Locally install pass-import and its pass extension
[group('install')]
local:
	@pipx install --force .
	@pimport --install-extension

# Run the tests
[group('tests')]
tests:
	@uv run --extra all pytest -n auto --cov=pass_import --cov-report=term --cov-report=html

# Run the linters
[group('linter')]
lint:
	@uv run ruff check pass_import share tests

# Run the security linters
[group('linter')]
security:
	@uv run bandit --ini .bandit -r pass_import tests share

# Generate the documentation and the man pages
[group('docs')]
docs: && man
	@PYTHONPATH=./ python3 share --docs

# Remove all build artifacts
clean:
	@rm -rf \
		debian/.debhelper debian/debhelper* debian/*.debhelper debian/pass-extension-import/ \
		debian/*.substvars debian/*.debhelper.log debian/files .pybuild \
		{{build}} build dist *.egg-info .coverage htmlcov \
		tests/assets/gnupg/random_seed tests/assets/test-results/
	@find . -name __pycache__ -type d -not -path './.venv/*' -prune -exec rm -rf {} +

# Get the current pass-import release version
[group('version')]
version:
	@sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml

# Create a new version number from the current release
[group('version')]
version-new:
	#!/usr/bin/env bash
	IFS="." read -r major minor <<< "$(just version)"
	echo "${major}.$(( minor + 1 ))"

# Create a new release
[group('release')]
release: clean tests lint commit archive publish

# Write the new release version to the package files, commit and tag it
[group('release')]
commit:
	#!/usr/bin/env bash
	set -eu -o pipefail
	version=`just version-new`
	git restore debian/changelog
	cat > debian/changelog.tmp <<-EOF
		{{pkgname}} (${version}-1) stable; urgency=medium

		  * Release {{pkgname}} v${version}

		 -- $(git config user.name) <$(git config user.email)>  $(date -R)

	EOF
	cat debian/changelog >> debian/changelog.tmp
	mv debian/changelog.tmp debian/changelog
	sed -i "s/^version = .*/version = \"$version\"/" pyproject.toml
	sed -i "s/^__version__ = .*/__version__ = '$version'/" pass_import/__about__.py
	# Stage only the version-bump line, rebuilt from HEAD, so any other
	# working-tree changes in these files never leak into the release commit.
	stage_bump() {
		local file="$1" expr="$2" mode blob
		mode=$(git ls-tree HEAD -- "$file" | awk '{print $1}')
		blob=$(git cat-file -p "HEAD:$file" | sed "$expr" | git hash-object -w --stdin)
		git update-index --cacheinfo "$mode,$blob,$file"
	}
	stage_bump pyproject.toml "s/^version = .*/version = \"$version\"/"
	stage_bump pass_import/__about__.py "s/^__version__ = .*/__version__ = '$version'/"
	git add debian/changelog
	git commit -S -m "Release {{pkgname}} v$version"
	git tag -a "v$version" -m "{{pkgname}} v$version" --local-user={{gpgkey}}

# Create a release archive
[group('release')]
archive: man
	#!/usr/bin/env bash
	set -eu -o pipefail
	version=`just version`
	mkdir -p {{pkgdest}}/release/
	git archive \
		--format=tar.gz \
		--prefix="{{pkgname}}-$version/share/man/man1/" \
		--add-file=share/man/man1/pimport.1 \
		--add-file=share/man/man1/pass-import.1 \
		--prefix="{{pkgname}}-$version/" \
		--output="{{pkgdest}}/release/{{pkgname}}-$version.tar.gz" \
		"v$version" ':!share/man/man1/*.md'
	gpg --armor --default-key {{gpgkey}} --detach-sig {{pkgdest}}/release/{{pkgname}}-$version.tar.gz
	gpg --verify {{pkgdest}}/release/{{pkgname}}-$version.tar.gz.asc

# Publish the new release on Github and PyPI
[group('release')]
publish:
	#!/usr/bin/env bash
	set -eu -o pipefail
	owner="roddhjav"
	version=`just version`
	git push origin main --tags
	gh release create "v$version" --notes-from-tag --repo $owner/{{pkgname}}
	gh release upload "v$version" --repo $owner/{{pkgname}} \
		{{pkgdest}}/release/{{pkgname}}-$version.tar.gz \
		{{pkgdest}}/release/{{pkgname}}-$version.tar.gz.asc
	uv build --out-dir {{build}}/pypi
	uv publish {{build}}/pypi/*
