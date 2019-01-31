<h1 align="center">pass import</h1>
<p align="center">
    <a href="https://travis-ci.org/roddhjav/pass-import">
        <img src="https://img.shields.io/travis/roddhjav/pass-import/master.svg?style=flat-square"
             alt="Build Status" /></a>
    <a href="https://gitlab.com/roddhjav/pass-import/pipelines">
        <img src="https://gitlab.com/roddhjav/pass-import/badges/master/pipeline.svg"
             alt="Pipeline Status" /></a>
    <a href="https://www.codacy.com/app/roddhjav/pass-import">
        <img src="https://img.shields.io/codacy/coverage/783d8cf291434d2b8f1c063b51cfebbb/master.svg?style=flat-square"
             alt="Code Coverage" /></a>
    <a href="https://www.codacy.com/app/roddhjav/pass-import">
        <img src="https://img.shields.io/codacy/grade/783d8cf291434d2b8f1c063b51cfebbb/master.svg?style=flat-square"
             alt="Code Quality" /></a>
    <a href="https://github.com/roddhjav/pass-import/releases/latest">
        <img src="https://img.shields.io/github/release/roddhjav/pass-import.svg?maxAge=600&style=flat-square"
             alt="Last Release" /></a>
</p>
<p align="center">
    A <a href="https://www.passwordstore.org/">pass</a> extension for importing
    data from most of the existing password manager.
</p>

## Description
`pass import` is a password store extension allowing you to import your password
database to a password store repository conveniently. It natively supports
import from 24 different password managers. More manager support can easily
be added.

Passwords are imported into the existing default password store, therefore
the password store must have been initialised before with `pass init`.

By default, pass imports entries at the root of the password store and only keeps
the main data (password, login, email, URL, group). This behaviour can be changed
using the provided options.

Pass import handles duplicates and is compatible with [browserpass][bp].

**The following password managers are supported:**

| **Password Manager** | **How to export Data** | **Command line** |
|:--------------------:|:----------------------:|:----------------:|
| [1password][1password] | *See this [guide][export-1password]* | `pass import 1password file.csv` |
| [1password4][1password] | *File > Export: CSV* | `pass import 1password4 file.csv` |
| [1password4pif][1password] | *File > Export: 1PIF* | `pass import 1password4pif file.1pif` |
| [bitwarden][bitwarden] | *Tools: Export* | `pass import bitwarden file.csv` |
| [buttercup][buttercup] | *File > Export > Export File to CSV* | `pass import buttercup file.csv` |
| [chrome][chrome] | *See this [guide][export-chrome]* | `pass import chrome file.csv` |
| [chromesqlite][chrome] | *See this [guide][export-chrome]* | `pass import chrome file.csv` |
| [enpass][enpass] | *File > Export > As CSV* | `pass import enpass file.csv` |
| [enpass6][enpass] | *Menu > File > Export > As JSON* | `pass import enpass6 file.json` |
| [dashlane][dashlane] | *File > Export > Unsecured Archive in CSV* | `pass import dashlane file.csv` |
| [fpm][fpm] | *File > Export Passwords: Plain XML* | `pass import fpm file.xml` |
| [gorilla][gorilla] | *File > Export: Yes: CSV Files* | `pass import gorilla file.csv` |
| [kedpm][kedpm] | *File > Export Passwords: Plain XML* | `pass import kedpm file.xml` |
| [keepass][keepass] | *File > Export > Keepass2 (XML)* | `pass import keepass file.xml` |
| [keepass2csv][keepass] | *File > Export > Keepass (CSV)* | `pass import keepasscsv file.csv` |
| [keepassx][keepassx] | *File > Export to > Keepass XML File* | `pass import keepassx file.xml` |
| [keepassx2][keepassx] | *Database > Export to CSV File* | `pass import keepassx2 file.csv` |
| [keepassxc][keepassxc] | *Database > Export to CSV File* | `pass import keepassxc file.csv` |
| [lastpass][lastpass] | *More Options > Advanced > Export* | `pass import lastpass file.csv` |
| [networkmanager][networkmanager] | *Also support specific networkmanager dir and ini file* | `pass import networkmanager` |
| [password-exporter][password-exporter] | *Add-ons Prefs: Export Passwords: CSV* | `pass import passwordexporter file.csv` |
| [pwsafe][pwsafe] | *File > Export To > XML Format* | `pass import pwsafe file.xml` |
| [revelation][revelation] | *File > Export: XML* | `pass import revelation file.xml` |
| [roboform][roboform] | *Roboform > Options > Data & Sync > Export To: CSV file* | `pass import roboform file.csv` |
| [upm][upm] | *Database > Export* | `pass import upm file.csv` |

## Usage

```
usage: pass import [-h] [-V] [[-p PATH] [-c] [-C] [-s] [-e] [-f] | -l] <manager> [file]

  Import data from most of the password manager. Passwords
  are imported in the existing default password store, therefore
  the password store must have been initialised before with 'pass init'

positional arguments:
  manager               Can be: 1password, 1password4, 1password4pif,
                        bitwarden, chrome, chromesqlite, dashlane, enpass,
                        fpm, gorilla, kedpm, keepass, keepasscsv, keepassx,
                        keepassx2, keepassxc, lastpass, networkmanager,
                        passwordexporter, pwsafe, revelation, roboform, upm.
  file                  File is the path to the file that contains the data to
                        import, if empty read the data from stdin.

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Import the passwords to a specific subfolder.
  -e, --extra           Also import all the extra data present.
  -c, --clean           Make the paths more command line friendly.
  -C, --convert         Convert the invalid caracters present in the paths.
  -s CAR, --separator CAR
                        Provide a caracter of replacement for the path
                        separator. Default: '-'
  -l, --list            List the supported password managers.
  -f, --force           Overwrite existing path.
  -q, --quiet           Be quiet.
  -v, --verbose         Be verbose.
  -V, --version         Show the program version and exit.

More information may be found in the pass-import(1) man page.
```

See `man pass-import` for more information.

## Examples
**Import password from KeePass**
```
pass import keepass keepass.xml
(*) Importing passwords from keepass
 .  File: keepass.xml
 .  Number of password imported: 6
 .  Passwords imported:
       Social/mastodon.social
       Social/twitter.com
       Social/news.ycombinator.com
       Servers/ovh.com/bynbyjhqjz
       Servers/ovh.com/jsdkyvbwjn
       Bank/aib
```

**Import password to a different password store**
```
export PASSWORD_STORE_DIR="~/.mypassword-store"
pass init <gpg-id>
pass import keepass keepass.xml
```

**Import password to a subfolder**
```
pass import keepass keepass.xml -p Import/
(*) Importing passwords from keepass
 .  File: db/keepass.xml
 .  Root path: Import
 .  Number of password imported: 6
 .  Passwords imported:
      Import/Social/mastodon.social
      Import/Social/twitter.com
      Import/Social/news.ycombinator.com
      Import/Servers/ovh.com/bynbyjhqjz
      Import/Servers/ovh.com/jsdkyvbwjn
      Import/Bank/aib
```

## Configuration file

Some configuration can be read from a configuration file called `.import` if it
is present at the root of the password repository. The configuration read from
this file will be overwritten by their coresponding command line option
if present.

Example of the `.import` configuration file for the default password repository:
```sh
$ cat ~/.password-store/.import
[convert]
separator = -
```

## Security consideration

Passwords should not be written in plain text form on the drive.
Therefore when possible you should pipe your passwords to pass import:
```sh
my_password_manager_export_cmd | pass import keepass
```

Otherwise, if your password manager lacks this command line option, you
should take care of securely removing the plain text password database:
```sh
pass import lastpass data.csv
shred -u data.csv
```

You might also want to update the passwords imported using [`pass-update`][update].

## Installation

**Requirements**
* `pass 1.7.0` or greater.
* `python3` (python 3.4, 3.5, 3.6 and 3.7 are supported)
* `python3-setuptools` to build and install it.
* `python3-defusedxml`
  - Debian/Ubuntu: `sudo apt-get install python3-defusedxml`
  - OSX: `pip3 install defusedxml`

**ArchLinux**

`pass-import` is available in the [Arch User Repository][aur].
```sh
yay -S pass-import  # or your preferred AUR install method
```

**Gentoo Linux**
```sh
layman -a wjn-overlay
emerge app-admin/pass-import
```

**NixOS**
```sh
nix-env -iA nixos.passExtensions.pass-import
```

**From git**
```sh
git clone https://github.com/roddhjav/pass-import/
cd pass-import
make
sudo make install  # For OSX: make install PREFIX=/usr/local
```

**Stable version**
```sh
wget https://github.com/roddhjav/pass-import/releases/download/v2.4/pass-import-2.4.tar.gz
tar xzf pass-import-2.4.tar.gz
cd pass-import-2.4
make
sudo make install  # For OSX: make install PREFIX=/usr/local
```

[Releases][releases] and commits are signed using [`06A26D531D56C42D66805049C5469996F0DF68EC`][keys].
You should check the key's fingerprint and verify the signature:
```sh
wget https://github.com/roddhjav/pass-import/releases/download/v2.4/pass-import-2.4.tar.gz.asc
gpg --recv-keys 06A26D531D56C42D66805049C5469996F0DF68EC
gpg --verify pass-import-2.4.tar.gz.asc
```


## Contribution
Feedback, contributors, pull requests are all very welcome. Please read the
[`CONTRIBUTING.md`](CONTRIBUTING.md) file for more details on the contribution process.


## License

    Copyright (C) 2017  Alexandre PUJOL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

[keys]: https://pujol.io/keys
[aur]: https://aur.archlinux.org/packages/pass-import
[releases]: https://github.com/roddhjav/pass-import/releases
[keybase]: https://keybase.io/roddhjav
[update]: https://github.com/roddhjav/pass-update

[1password]: https://1password.com/
[bitwarden]: https://bitwarden.com/
[buttercup]: https://buttercup.pw/
[chrome]: https://support.google.com/chrome
[dashlane]: https://www.dashlane.com/
[enpass]: https://www.enpass.io/
[fpm]: http://fpm.sourceforge.net/
[gorilla]: https://github.com/zdia/gorilla/wiki
[kedpm]: http://kedpm.sourceforge.net/
[keepass]: https://keepass.info/
[keepassx]: https://www.keepassx.org/
[keepassxc]: https://keepassxc.org/
[kwallet]: https://utils.kde.org/projects/kwalletmanager/
[lastpass]: https://www.lastpass.com/
[networkmanager]: https://wiki.gnome.org/Projects/NetworkManager
[password-exporter]: https://github.com/kspearrin/ff-password-exporter
[pwsafe]: https://pwsafe.org/
[revelation]: https://revelation.olasagasti.info/
[roboform]: https://www.roboform.com/
[upm]: http://upm.sourceforge.net/

[bp]: https://github.com/dannyvankooten/browserpass
[export-chrome]: https://www.axllent.org/docs/view/export-chrome-passwords/
[export-1password]: https://support.1password.com/export/
