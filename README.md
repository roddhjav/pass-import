<h1 align="center">pass import</h1>

<p align="center">
<a href="https://travis-ci.org/roddhjav/pass-import"><img src="https://img.shields.io/travis/roddhjav/pass-import/master.svg" alt="Build Status" /></a>
<a href="https://www.codacy.com/app/roddhjav/pass-import"><img src="https://img.shields.io/codacy/coverage/783d8cf291434d2b8f1c063b51cfebbb/master.svg" alt="Code Coverage" /></a>
<a href="https://www.codacy.com/app/roddhjav/pass-import"><img src="https://img.shields.io/codacy/grade/783d8cf291434d2b8f1c063b51cfebbb/master.svg" alt="Code Quality" /></a>
<a href="https://github.com/roddhjav/pass-import/releases/latest"><img src="https://img.shields.io/github/release/roddhjav/pass-import.svg?maxAge=600" alt="Last Release" /></a>
</p>

<p align="center">
A <a href="https://www.passwordstore.org/">pass</a> extension for importing data from most of the existing password manager.
</p>

## Description
`pass import` is a password store extension allowing you to conveniently
import your password database to a password store repository. It natively
supports import from 18 different password managers. More manager support can
easily be added.

Passwords are imported in the existing default password store, therefore
the password store must has been initialized before with `pass init`.

By default pass, imports entries at the root of the password store and only keeps
the main data (password, login, email, url, group). This behavior can be changed
using the provided options.

Pass import handles duplicates and is compatible with [browserpass][bp].

**The following password managers are supported:**

| **Password Manager** | **How to export Data** | **Command line** |
|:--------------------------------------:|:---------------------------------------------------------------:|:---------------------------------------:|
| [1password][1password] | *Select all items [Ctrl+A]: Click Right> Settings> Export: CSV* | `pass import 1password file.csv` |
| [1password4][1password] | *File > Export: CSV* | `pass import 1password4 file.csv` |
| [bitwarden][bitwarden] | *Tools: Export* | `pass import bitwarden file.csv` |
| [chrome][chrome] | *See this [guide][export-chrome]* | `pass import chrome file.csv` |
| [enpass][enpass] | *File > Export > As CSV* | `pass import enpass file.csv` |
| [dashlane][dashlane] | *File > Export > Unsecured Archive in CSV* | `pass import dashlane file.csv` |
| [fpm][fpm] | *File > Export Passwords: Plain XML* | `pass import fpm file.xml` |
| [gorilla][gorilla] | *File > Export: Yes: CSV Files* | `pass import gorilla file.csv` |
| [kedpm][kedpm] | *File > Export Passwords: Plain XML* | `pass import kedpm file.xml` |
| [keepass][keepass] | *File > Export > Keepass2 (XML)* | `pass import keepass file.xml` |
| [keepass2csv][keepass] | *File > Export > Keepass (CSV)* | `pass import keepasscsv file.csv` |
| [keepassx][keepassx] | *File > Export to > Keepass XML File* | `pass import keepassx file.xml` |
| [keepassxc][keepassxc] | *Database > Export to CSV File* | `pass import keepassxc file.csv` |
| [lastpass][lastpass] | *More Options > Advanced > Export* | `pass import lastpass file.csv` |
| [password-exporter][password-exporter] | *Add-ons Prefs: Export Passwords: CSV* | `pass import passwordexporter file.csv` |
| [pwsafe][pwsafe] | *File > Export To > XML Format* | `pass import pwsafe file.xml` |
| [revelation][revelation] | *File > Export: XML* | `pass import revelation file.xml` |
| [roboform][roboform] | *Roboform > Options > Data & Sync > Export To: CSV file* | `pass import roboform file.csv` |


## Usage

```
usage: pass import [-h] [-V] [[-p PATH] [-c] [-e] [-f] | -l] [manager] [file]

  Import data from most of the password manager. Passwords
  are imported in the existing default password store, therefore
  the password store must has been initialized before with 'pass init'

positional arguments:
  manager               Can be: 1password, 1password4, chrome, dashlane,
                        enpass, fpm, gorilla, kedpm, keepass, keepasscsv,
                        keepassx, keepassxc, lastpass, passwordexporter,
                        pwsafe, revelation, roboform.
  file                  File is the path to the file that contains the data to
                        import, if empty read the data from stdin.

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Import the passwords to a specific subfolder.
  -c, --clean           Clean data before import.
  -e, --extra           Also import all the extra data present.
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
       Servers/ovh.com
       Servers/ovh.com0
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
      Import/Servers/ovh.com
      Import/Servers/ovh.com0
      Import/Bank/aib
```

## Security consideration

Passwords should generally not be written in a plain text form on the drive.
Therefore when possible you should pipe your passwords to pass import:
```sh
my_password_manager_export_cmd | pass import keepass
```

Otherwise, if your password manager does not have this command line option, you
should take care of securely removing the plain text password database:
```sh
pass import lastpass data.csv
srm data.csv
```

You might also want to update the passwords imported using [`pass-update`][update].

## Installation

**Requirements**
* `pass 1.7.0` or greater.
* `python3` (python 3.4, 3.5 and 3.6 are supported)
* `python-defusedxml`
  - Debian/Ubuntu: `sudo apt-get install python3-defusedxml`
  - OSX: `pip3 install defusedxml`
* If you do not want to install this extension as system extension, you need to
enable user extension with `PASSWORD_STORE_ENABLE_EXTENSIONS=true pass`. You can
create an alias in `.bashrc`: `alias pass='PASSWORD_STORE_ENABLE_EXTENSIONS=true pass'`

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

**ArchLinux**

`pass-import` is available in the [Arch User Repository][aur].
```sh
pacaur -S pass-import # or your preferred AUR install method
```

**Stable version**
```sh
wget https://github.com/roddhjav/pass-import/releases/download/v2.1/pass-import-2.1.tar.gz
tar xzf pass-import-2.1.tar.gz
cd pass-import-2.1
sudo make install
```

[Releases][releases] and commits are signed using [`06A26D531D56C42D66805049C5469996F0DF68EC`][keys].
You should check the key's fingerprint and verify the signature:
```sh
wget https://github.com/roddhjav/pass-import/releases/download/v2.1/pass-import-2.1.tar.gz.asc
gpg --recv-keys 06A26D531D56C42D66805049C5469996F0DF68EC
gpg --verify pass-import-2.1.tar.gz.asc
```


## Contribution
Feedback, contributors, pull requests are all very welcome. Please read the
[`CONTRIBUTING.md`](CONTRIBUTING.md) file for more details on the contribution process.


## Donations
If you really like this software and would like to donate, you can send donations using one of the following currencies:
* In Bitcoin: `1HQaENhbThLHYzgjzmRpVMT7ErTSGzHEzq` (see [proof][keybase])
* In Ethereum: `0x4296ee83cd0d66e1cb3e0622c8f8fef82532c968`
* In Zcash: `t1StE9pbFvep296pdQmKVdaBaRkvnXBKkR1` (see [proof][keybase])
* In Litecoin: `LTjxtZhkYHT31aveumozMd7bCKJ5uymMAC`
* In Bitcoin Cash: `1FCEjKXUGXYctHt53EYifSm4XeQgC1piis`


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
[password-exporter]: https://addons.mozilla.org/en-US/firefox/addon/password-exporter/
[pwsafe]: https://pwsafe.org/
[revelation]: https://revelation.olasagasti.info/
[roboform]: https://www.roboform.com/

[bp]: https://github.com/dannyvankooten/browserpass
[export-chrome]: https://www.axllent.org/docs/view/export-chrome-passwords/
