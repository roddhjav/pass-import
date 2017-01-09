# pass import

A generic importer extension for the standard unix password manager `pass`
(https://www.passwordstore.org/).


## Description
**pass-import** is a password store extension allowing you to conveniently
import your password database to a password store repository.

It support importation of data from the following password manager:
* 1password
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

		pass import <importer> [args]

See `man pass-import` for more information on import process


## Installation

		git clone https://github.com/alexandrepujol/pass-import/
		cd pass-import
		sudo make install


Please be advised, `pass-import` requires `pass>1.6.5` for extension support.


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

