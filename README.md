# pass import

A generic importer extension for the standard unix password manager
[pass](https://www.passwordstore.org/).

## Description
**pass-import** is a password store extension allowing you to conveniently
import your password database to a password store repository.

It supports importation of data from the following password manager:
* 1password
* chrome
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
			Import data to a password store repository.
			ARG depends of the importer script.
			<importer> can be: keepassx, revelation, roboform, pwsafe
			fpm, kwallet, kedpm, keepass, password-exporter, 1password
			lastpass, keepass2csv, gorilla, chrome

		Options:
		    -v, --version  Show version information.
		    -h, --help	   Print this help message and exit.

		More information may be found in the pass-import(1) man page.

See `man pass-import` for more information on import process


## Installation

**ArchLinux**

		pacaur -S pass-import

**Other linux**

		git clone https://github.com/roddhjav/pass-import/
		cd pass-import
		sudo make install

**Requirments**

In order to use extension with `pass`, you need:
* `pass 1.7.0` or greater. As of today this version has not been released yet.
Therefore you need to install it by hand from zx2c4.com:

		git clone https://git.zx2c4.com/password-store
		cd password-store
		sudo make install

* You need to enable the extensions in pass: `PASSWORD_STORE_ENABLE_EXTENSIONS=true pass`.
You can create an alias in `.bashrc`: `alias pass='PASSWORD_STORE_ENABLE_EXTENSIONS=true pass'`



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

