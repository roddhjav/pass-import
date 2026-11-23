# Maintainer: Alexandre Pujol <alexandre@pujol.io>
# shellcheck disable=SC2034,SC2154,SC2164

# Warning: for development only, use https://aur.archlinux.org/packages/pass-import for production use.

pkgname=pass-import
pkgver=3.5
pkgrel=1
pkgdesc='A pass extension for importing data from most existing password managers.'
arch=('any')
url='https://github.com/roddhjav/pass-import'
license=('GPL-3.0-or-later')
depends=(
  'pass'
  'python'
  'python-yaml'
  'python-requests'
  'python-zxcvbn'
)
makedepends=('python-build' 'python-installer' 'python-setuptools' 'rsync' 'just')
optdepends=(
  'python-defusedxml: xml based importers'
  'python-pykeepass: direct keepass database import'
  'python-secretstorage: gnome-keyring import'
  'python-cryptography: password encrypted otp import'
  'python-magic: Detection of file decryption'
  'python-jsonpath-ng: json based filter'
)

prepare() {
  rsync -a --delete "$startdir/" "$srcdir/$pkgname"
}

build() {
  cd "$srcdir/$pkgname"
  just build
}

package() {
  cd "$srcdir/$pkgname"
  just destdir="$pkgdir" install
}
