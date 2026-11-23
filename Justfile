# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2026 Alexandre Pujol <alexandre@pujol.io>
# SPDX-License-Identifier: GPL-3.0-or-later

# Usage: `just`

# Build settings

destdir := "/"
python := "python3"
prefix := "/usr"
extdir := prefix / "lib/password-store/extensions"
build := ".build"
pkgdest := `pwd` / ".pkg"
pkgname := "pass-import"
debname := "pass-extension-import"
gpgkey := "06A26D531D56C42D66805049C5469996F0DF68EC"
sign := "false"

usage := "
Build variables available:
    build        " + BLUE + "# Build directory (default: " + build + ")" + NORMAL + "
    python       " + BLUE + "# Python interpreter (default: " + python + ")" + NORMAL + "
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
	@{{python}} -m build --wheel --no-isolation --outdir {{build}}

# Generate the man pages
[group('build')]
man:
	@pandoc -t man -s -o share/man/man1/pass-import.1 share/man/man1/pass-import.md
	@pandoc -t man -s -o share/man/man1/pimport.1 share/man/man1/pimport.md

# Install the python package
[group('install')]
install-python:
	@{{python}} -m installer --destdir="{{destdir}}" {{build}}/*.whl

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

# Build the package on Arch Linux
[group('packages')]
build-pkg: (_ensure_pkgdest)
	@PKGDEST={{pkgdest}} BUILDDIR=/tmp/makepkg makepkg --syncdeps --force --cleanbuild --noconfirm --noprogressbar

# Build the package on Debian, the same package works on Ubuntu
[group('packages')]
build-dpkg: (_ensure_pkgdest)
	@dpkg-buildpackage -b -d {{ if sign == "true" { "--sign-key=" + gpgkey } else { "--no-sign" } }}
	@lintian --color always --display-info --pedantic --tag-display-limit 0 || true
	@mv ../{{debname}}_*.deb {{pkgdest}}/

# Build the package on openSUSE or Fedora
[group('packages')]
build-rpm: (_ensure_pkgdest)
	#!/usr/bin/env bash
	set -eu -o pipefail
	RPMBUILD_ROOT=$(mktemp -d /tmp/{{pkgname}}.XXXXXX)
	VERSION="$(just version)"
	readonly RPMBUILD_ROOT VERSION

	mkdir -p "$RPMBUILD_ROOT"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS/tmp}
	cp -p "dists/{{pkgname}}.spec" "$RPMBUILD_ROOT/SPECS/{{pkgname}}.spec"
	tar -czf "$RPMBUILD_ROOT/SOURCES/{{pkgname}}-$VERSION.tar.gz" --transform "s,^,{{pkgname}}-$VERSION/," ./*

	cd "$RPMBUILD_ROOT"
	sed -i "s/^Version:.*/Version:        $VERSION/" "SPECS/{{pkgname}}.spec"
	rpmbuild -bb --define "_topdir $RPMBUILD_ROOT" "SPECS/{{pkgname}}.spec"

	find "$RPMBUILD_ROOT/RPMS" -name '*.rpm' -exec mv -t "{{pkgdest}}/" {} +
	rm -rf "$RPMBUILD_ROOT"

# Build & install pass-import on Arch based systems
[group('packages')]
pkg: build-pkg
	@sudo pacman -U --noconfirm {{pkgdest}}/{{pkgname}}-`just version`-*.pkg.tar.zst

# Build & install pass-import on Debian based systems
[group('packages')]
dpkg: build-dpkg
	@sudo apt-get install -y {{pkgdest}}/{{debname}}_`just version`-*_all.deb

# Build & install pass-import on openSUSE or Fedora based systems
[group('packages')]
rpm: build-rpm
	@sudo rpm -ivh --force {{pkgdest}}/{{pkgname}}-`just version`-*.rpm

# Build the package in a clean OCI container
[group('packages')]
package dist release="":
	@bash dists/docker.sh {{dist}} {{release}}

# Build all packages in a clean OCI container
[group('packages')]
packages: clean
	#!/usr/bin/env bash
	set -eu -o pipefail
	declare -A matrix=(
		["archlinux"]="-"
		["debian"]="13"
		["opensuse"]="-"
		["fedora"]="44"
	)
	for dist in "${!matrix[@]}"; do
		IFS=' ' read -r -a releases <<< "${matrix[$dist]}"
		for release in "${releases[@]}"; do
			echo "{{ RED + BOLD }}Building package for $dist $release{{ NORMAL }}"
			bash dists/docker.sh $dist $release
		done
	done

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
		{{pkgdest}}/{{pkgname}}* {{pkgdest}}/{{debname}}* \
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
	sed -i "s/^pkgver=.*/pkgver=$version/" PKGBUILD
	sed -i "s/^Version:.*/Version:        $version/" dists/{{pkgname}}.spec
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
	stage_bump PKGBUILD "s/^pkgver=.*/pkgver=$version/"
	stage_bump dists/{{pkgname}}.spec "s/^Version:.*/Version:        $version/"
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

# Create & upload new release packages to the repositories
[group('release')]
repo path="../../../Packages":
	just --justfile {{path}}/pkgbuilds/Justfile publish {{pkgname}} `just version`
	just --justfile {{path}}/repo.pujol.io/Justfile publish {{pkgname}} `just version`

_ensure_pkgdest:
	@mkdir -p {{pkgdest}}
