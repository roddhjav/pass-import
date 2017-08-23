# pass import [![build][build-img]][build-url] [![coverage][cover-img]][cover-url] [![climate][clima-img]][clima-url]

A [pass][pass] extension for importing data from most of the existing
password manager.

## Description
**pass-import** is a password store extension allowing you to conveniently
import your password database to a password store repository.

It supports importation of data from the following password manager:
* 1password
* chrome
* enpass
* fpm
* gorrilla
* kedpm
* keepass
* keepass2csv
* keepassx
* kwallet
* lastpass
* password-exporter
* pwsafe
* revelation
* roboform


## Usage

		pass import - A generic importer extension for pass

		Vesion: 0.2

		Usage:
		    pass import <importer> [ARG]
			Import data to a password store.
			ARG depends of the importer script.
			<importer> can be: keepassx, revelation, roboform, pwsafe
			fpm, kwallet, kedpm, keepass, password-exporter, 1password
			lastpass, keepass2csv, gorilla, chrome

		Options:
		    -v, --version  Show version information.
		    -h, --help	   Print this help message and exit.

		More information may be found in the pass-import(1) man page.

See `man pass-import` for more information.


## Installation

**From git**
```sh
git clone https://github.com/roddhjav/pass-import/
cd pass-import
sudo make install
```

**OS X**
```sh
git clone https://github.com/roddhjav/pass-import/
cd pass-import
make install PREFIX=/usr/local
```

**Stable version**
```sh
wget https://github.com/roddhjav/pass-import/releases/download/v2.0/pass-import-2.0.tar.gz
tar xzf pass-import-2.0.tar.gz
cd pass-import-2.0
sudo make install
```

Releases and commits are signed using [`06A26D531D56C42D66805049C5469996F0DF68EC`][keys].
You should verify the signature:
```sh
gpg --verify pass-import-2.0.tar.gz.sig
```

**ArchLinux**

`pass-import` is available in the [Arch User Repository][aur].
```sh
pacaur -S pass-import # or your preferred AUR install method
```

**Requirements**
* `pass 1.7.0` or greater.
* `python 3`
* If you do not want to install this extension as system extension, you need to
enable user extension with `PASSWORD_STORE_ENABLE_EXTENSIONS=true pass`. You can
create an alias in `.bashrc`: `alias pass='PASSWORD_STORE_ENABLE_EXTENSIONS=true pass'`


## Contribution
Feedback, contributors, pull requests are all very welcome.


## License

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

[build-img]: https://travis-ci.org/roddhjav/pass-import.svg?branch=master
[build-url]: https://travis-ci.org/roddhjav/pass-import
[cover-img]: https://coveralls.io/repos/github/roddhjav/pass-import/badge.svg?branch=master
[cover-url]: https://coveralls.io/github/roddhjav/pass-import?branch=master
[clima-img]: https://codeclimate.com/github/roddhjav/pass-import/badges/gpa.svg
[clima-url]: https://codeclimate.com/github/roddhjav/pass-import

[pass]: https://www.passwordstore.org/
[keys]: https://pujol.io/keys
[aur]: https://aur.archlinux.org/packages/pass-import

