# pass import [![build][build-img]][build-url] [![coverage][cover-img]][cover-url] [![climate][clima-img]][clima-url]

A [pass][pass] extension for importing data from most of the existing
password manager.

## Description
`pass import` is a password store extension allowing you to conveniently
import your password database to a password store repository. It natively
supports import from 15 differents password managers. More manager support can
easily be added.

Passwords are imported in the existing default password store, therefore
the password store must has been initialized before with `pass init`.

By default pass, import entries at the root of the password store and only keeps
the main data (password, login, email, url, group). This behavior can be changed
using the provided options.

The following password managers are supported:

|          **Password Manager**          |         **How to export Data**         |             **Command line**            |
|:--------------------------------------:|:--------------------------------------:|:---------------------------------------:|
|         [1password][1password]         |                   * *                  |    `pass import onepassword file.xml`   |
|            [chrome][chrome]            |                   * *                  |      `pass import chrome file.xml`      |
|            [enpass][enpass]            |        *File > Export > As CSV*        |      `pass import enpass file.csv`      |
|               [fpm][fpm]               |  *File > Export Passwords: Plain XML*  |        `pass import fpm file.xml`       |
|          [gorrilla][gorrilla]          |     *File > Export: Yes: CSV Files*    |     `pass import gorrilla file.xml`     |
|             [kedpm][kedpm]             |                   * *                  |       `pass import kedpm file.xml`      |
|           [keepass][keepass]           |    *File > Export > Keepass2 (XML)*    |      `pass import keepass file.xml`     |
|         [keepass2csv][keepass]         |     *File > Export > Keepass (CSV)*    |    `pass import keepasscsv file.csv`    |
|          [keepassx][keepassx]          |  *File > Export to > Keepass XML File* |     `pass import keepassx file.xml`     |
|           [kwallet][kwallet]           |                   * *                  |      `pass import kwallet file.xml`     |
|          [lastpass][lastpass]          |   *More Options > Advanced > Export*   |     `pass import lastpass file.csv`     |
| [password-exporter][password-exporter] | *Add-ons Prefs: Export Passwords: CSV* | `pass import passwordexporter file.csv` |
|            [pwsafe][pwsafe]            |     *File > Export To > XML Format*    |      `pass import pwsafe file.xml`      |
|        [revelation][revelation]        |          *File > Export: XML*          |    `pass import revelation file.xml`    |
|          [roboform][roboform]          |                   * *                  |     `pass import roboform file.xml`     |







## Usage

```
pass import 2.0 - A generic importer extension for pass.

Usage:
    pass import [[-p folder] [-c] [-e] [-f] | -l] <manager> <file>
        Import data from most of the password manager. Passwords
        are imported in the existing default password store, therefore
        the password store must has been initialized before with 'pass init'

        <file> is the path to the file that contains the data to import, if
        empty read the data from stdin.

        <manager> can be:
        	onepassword chrome dashlane enpass fpm gorilla
        	kedpm keepass keepasscsv keepassx kwallet lastpass
        	passwordexporter pwsafe revelation roboform

Options:
    -p, --path     Import the passwords to a specific subfolder.
    -c, --clean    Clean data before import.
    -e, --extra    Also import all the extra data present.
    -l, --list     List the supported password managers.
    -f, --force    Overwrite existing path.
    -q, --quiet    Be quiet.
    -v, --verbose  Be verbose.
    -V, --version  Show version information.
    -h, --help	   Print this help message and exit.

More information may be found in the pass-import(1) man page.
```

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

[1password]: https://1password.com/
[chrome]: https://support.google.com/chrome
[enpass]: https://www.enpass.io/
[fpm]: http://fpm.sourceforge.net/
[gorrilla]: https://github.com/zdia/gorilla/wiki
[kedpm]: http://kedpm.sourceforge.net/
[keepass]: keepass.info
[keepassx]: https://www.keepassx.org/
[kwallet]: https://utils.kde.org/projects/kwalletmanager/
[lastpass]: https://www.lastpass.com/
[password-exporter]: https://addons.mozilla.org/en-US/firefox/addon/password-exporter/
[pwsafe]: https://pwsafe.org/
[revelation]: https://revelation.olasagasti.info/
[roboform]: https://www.roboform.com/
