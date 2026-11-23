#!/usr/bin/env bash
# Build the package in a clean Archlinux/openSUSE/Fedora/Debian/Ubuntu container
# Copyright (C) 2022-2026 Alexandre Pujol <alexandre@pujol.io>
# SPDX-License-Identifier: GPL-3.0-or-later

# Usage:
#  just package debian 13
#  just package archlinux
#  just package opensuse
#  just package fedora 44

set -eu -o pipefail

readonly BASEIMAGE="${BASEIMAGE:-registry.gitlab.com/roddhjav/builders}"
readonly PREFIX="builder-"
readonly PKGNAME=pass-import
readonly VOLUME=/tmp/build
readonly BUILDIR=/home/build/tmp
readonly OUTPUT=".pkg"
readonly DISTRIBUTION="$1"
RELEASE="${2:-}"
PACKAGER="$(git config user.name) <$(git config user.email)>"
[[ "$RELEASE" == "-" ]] && RELEASE=""
readonly RELEASE PACKAGER

_start() {
	local img="$1"
	docker start "$img" || return 1
}

_is_running() {
	local img="$1"
	[[ "$(docker inspect -f '{{ .State.Running }}' "$img" 2>/dev/null)" == true ]]
}

_exist() {
	local img="$1"
	docker inspect -f '{{ .State.Running }}' "$img" &>/dev/null
}

_ensure() {
	local img="$1"
	if ! _is_running "$img"; then
		_start "$img"
	fi
}

sync() {
	mkdir -p "$VOLUME"
	rsync -ra --delete --exclude .venv --exclude .pkg --exclude .password \
		. "$VOLUME/$PKGNAME"
}

build_in_docker_makepkg() {
	local dist="$1"
	local img="$PREFIX$dist"

	if _exist "$img"; then
		_ensure "$img"
	else
		docker pull "$BASEIMAGE/$dist"
		docker run -tid --name "$img" --volume "$VOLUME:$BUILDIR" \
			--env PKGDEST="$BUILDIR" --env PACKAGER="$PACKAGER" \
			"$BASEIMAGE/$dist"
		docker exec "$img" sudo pacman -Sy --noconfirm --noprogressbar
	fi

	docker exec --workdir="$BUILDIR/$PKGNAME" "$img" just build-pkg
	mv "$VOLUME/$PKGNAME/$OUTPUT/$PKGNAME"*.pkg.* "$OUTPUT"
}

build_in_docker_dpkg() {
	local dist="$1" release="$2"
	local img="$PREFIX$dist$release"

	if _exist "$img"; then
		_ensure "$img"
	else
		docker pull "$BASEIMAGE/$dist:$release"
		docker run -tid --name "$img" --volume "$VOLUME:$BUILDIR" \
			"$BASEIMAGE/$dist:$release"
		docker exec "$img" sudo apt-get update -q
	fi

	docker exec --workdir="$BUILDIR/$PKGNAME" "$img" sudo apt-get build-dep -y .
	docker exec --workdir="$BUILDIR/$PKGNAME" "$img" just build-dpkg
	mv "$VOLUME/$PKGNAME/$OUTPUT/pass-extension-import"*.deb "$OUTPUT"
}

build_in_docker_rpm() {
	local dist="$1" release="${2:-}"
	local img="$PREFIX$dist$release"
	local tag="${release:-latest}"

	if _exist "$img"; then
		_ensure "$img"
	else
		docker pull "$BASEIMAGE/$dist:$tag"
		docker run -tid --name "$img" --volume "$VOLUME:$BUILDIR" \
			"$BASEIMAGE/$dist:$tag"
	fi

	case "$dist" in
	opensuse) docker exec --workdir="$BUILDIR/$PKGNAME" "$img" bash -c \
		"sudo zypper install -y \$(rpmspec -q --buildrequires dists/$PKGNAME.spec)" ;;
	fedora) docker exec --workdir="$BUILDIR/$PKGNAME" "$img" sudo dnf -y builddep dists/$PKGNAME.spec ;;
	esac

	docker exec --workdir="$BUILDIR/$PKGNAME" "$img" just build-rpm
	mv "$VOLUME/$PKGNAME/$OUTPUT/$PKGNAME"*.rpm "$OUTPUT"
}

main() {
	case "$DISTRIBUTION" in
	archlinux)
		sync
		build_in_docker_makepkg "$DISTRIBUTION"
		;;

	debian | ubuntu)
		sync
		build_in_docker_dpkg "$DISTRIBUTION" "$RELEASE"
		;;

	opensuse | fedora)
		sync
		build_in_docker_rpm "$DISTRIBUTION" "$RELEASE"
		;;

	*)
		echo "Unsupported distribution: $DISTRIBUTION" >&2
		exit 1
		;;
	esac
}

mkdir -p "$OUTPUT"
main "$@"
