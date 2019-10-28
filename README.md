<h1 align="center">pass import</h1>
<p align="center">
    <a href="https://travis-ci.org/roddhjav/pass-import">
        <img src="https://img.shields.io/travis/roddhjav/pass-import/master.svg?style=flat-square"
             alt="Build Status" /></a>
    <a href="https://gitlab.com/roddhjav/pass-import/pipelines">
        <img src="https://gitlab.com/roddhjav/pass-import/badges/master/pipeline.svg?style=flat-square"
             alt="Pipeline Status" /></a>
    <a href="https://roddhjav.gitlab.io/pass-import/">
        <img src="https://gitlab.com/roddhjav/pass-import/badges/master/coverage.svg?style=flat-square"
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
import from <!-- NB BEGIN -->39<!-- NB END --> different password managers.
More manager support can easily be added.

Passwords are imported into the existing default password store, therefore
the password store must have been initialised before with `pass init`.

By default, pass imports entries at the root of the password store and only keeps
the main data (password, login, email, URL, group). This behaviour can be changed
using the provided options.

Pass import handles duplicates and is compatible with [browserpass]. It imports
OTP secret in a way that is compatible with [pass-otp].

**The following password managers are supported:**

<!-- SUPPORTED LIST BEGIN -->
| **Password Manager** | **How to export Data** | **Command line** |
|:--------------------:|:----------------------:|:----------------:|
| [1password](https://1password.com/) | *See this [guide](https://support.1password.com/export/)* | `pass import 1password file.csv` |
| [1password4](https://1password.com/) | *See this [guide](https://support.1password.com/export)* | `pass import 1password4 file.csv` |
| [1password4pif](https://1password.com/) | *See this [guide](https://support.1password.com/export/)* | `pass import 1password4pif file.1pif` |
| [aegis](https://github.com/beemdevelopment/Aegis) | *Settings> Tools: Export (Plain or encrypted)* | `pass import aegis file.json` |
| [andotp](https://github.com/andOTP/andOTP) | *Backups> Backup plain, gpg or password encrypted* | `pass import andotp file.{json, json.aes, gpg}` |
| [apple-keychain](https://support.apple.com/guide/keychain-access) | *See this [guide](https://gist.github.com/santigz/601f4fd2f039d6ceb2198e2f9f4f01e0)* | `pass import apple-keychain file.txt` |
| [bitwarden](https://bitwarden.com/) | *Tools: Export* | `pass import bitwarden file.csv` |
| [buttercup](https://buttercup.pw/) | *File > Export > Export File to CSV* | `pass import buttercup file.csv` |
| [chrome](https://support.google.com/chrome) | *See this [guide](https://www.axllent.org/docs/view/export-chrome-passwords/)* | `pass import chrome file.csv` |
| [chromesqlite](https://support.google.com/chrome) | *See this [guide](https://www.axllent.org/docs/view/export-chrome-passwords/)* | `pass import chromesqlite file.csv` |
| [csv]() | *generic csv importer* | `pass import csv file.csv --cols 'url,login,,password'` |
| [dashlane](https://www.dashlane.com/) | *File > Export > Unsecured Archive in CSV* | `pass import dashlane file.csv` |
| [encryptr](https://spideroak.com/encryptr/) | *Compile from source and follow instructions from this [guide](https://github.com/SpiderOak/Encryptr/issues/295#issuecomment-322449705)* | `pass import encryptr file.csv` |
| [enpass](https://www.enpass.io/) | *File > Export > As CSV* | `pass import enpass file.csv` |
| [enpass6](https://www.enpass.io/) | *Menu > File > Export > As JSON* | `pass import enpass6 file.json` |
| [fpm](http://fpm.sourceforge.net/) | *File > Export Passwords: Plain XML* | `pass import fpm file.xml` |
| [gnome-authenticator](https://gitlab.gnome.org/World/Authenticator) | *Backup > in a plain-text JSON file* | `pass import gnome-authenticator json.csv` |
| [gnome-keyring](https://wiki.gnome.org/Projects/GnomeKeyring) | *Nothing to do* | `pass import gnome-keyring` |
| [gorilla](https://github.com/zdia/gorilla/wiki) | *File > Export: Yes: CSV Files* | `pass import gorilla file.csv` |
| [kedpm](http://fpm.sourceforge.net/) | *File > Export Passwords: Plain XML* | `pass import fpm file.xml` |
| [keepass](https://www.keepass.info) | *Nothing to do* | `pass import keepass file.kdbx` |
| [keepass-csv](https://www.keepass.info) | *File > Export > Keepass (CSV)* | `pass import keepass-csv file.csv` |
| [keepass-xml](https://www.keepass.info) | *File > Export > Keepass2 (XML)* | `pass import keepass-xml file.xml` |
| [keepassx](https://www.keepassx.org/) | *File > Export to > Keepass XML File* | `pass import keepassx file.xml` |
| [keepassx2](https://www.keepassx.org/) | *Nothing to do* | `pass import keepassx2 file.kdbx` |
| [keepassx2-csv](https://www.keepassx.org/) | *Database > Export to CSV File* | `pass import keepassx2-csv file.csv` |
| [keepassxc](https://keepassxc.org/) | *Nothing to do* | `pass import keepassxc file.kdbx` |
| [keepassxc-csv](https://keepassxc.org/) | *Database > Export to CSV File* | `pass import keepassxc-csv file.csv` |
| [keeper](https://keepersecurity.com/) | *Settings > Export : Export to CSV File* | `pass import keeper file.csv` |
| [lastpass](https://www.lastpass.com/) | *More Options > Advanced > Export* | `pass import lastpass file.csv` |
| [myki](https://myki.com/) | *See this [guide](https://support.myki.com/myki-app/exporting-your-passwords-from-the-myki-app/how-to-export-your-passwords-account-data-from-myki)* | `pass import myki file.csv` |
| [networkmanager](https://wiki.gnome.org/Projects/NetworkManager) | *Also support specific networkmanager dir and ini file* | `pass import networkmanager` |
| [pass](https://passwordstore.org) | *Nothing to do* | `pass import pass path/to/store` |
| [passpie](https://passpie.readthedocs.io) | *`passpie export file.yml`* | `pass import passpie file.yml` |
| [passwordexporter](https://github.com/kspearrin/ff-password-exporter) | *Add-ons Prefs: Export Passwords: CSV* | `pass import passwordexporter file.csv` |
| [pwsafe](https://pwsafe.org/) | *File > Export To > XML Format* | `pass import pwsafe file.xml` |
| [revelation](https://revelation.olasagasti.info/) | *File > Export: XML* | `pass import revelation file.xml` |
| [roboform](https://www.roboform.com/) | *Roboform > Options > Data & Sync > Export To: CSV file* | `pass import roboform file.csv` |
| [upm](http://upm.sourceforge.net/) | *Database > Export* | `pass import upm file.csv` |
<!-- SUPPORTED LIST END -->

## Usage

<!-- USAGE BEGIN -->
```
usage: pass import [-h] [-p PATH] [-a] [-c] [-C] [-s CAR] [--cols COLS]
                   [--config CONFIG] [-l] [-f] [-V] [-q | -v]
                   [manager] [file]

  Import data from most of the password manager. Passwords
  are imported in the existing default password store, therefore
  the password store must have been initialised before with 'pass init'

positional arguments:
  manager               Can be: 1password, 1password4, 1password4pif, aegis,
                        andotp, apple-keychain, bitwarden, buttercup, chrome,
                        chromesqlite, csv, dashlane, encryptr, enpass,
                        enpass6, fpm, gnome-authenticator, gnome-keyring,
                        gorilla, kedpm, keepass, keepass-csv, keepass-xml,
                        keepassx, keepassx2, keepassx2-csv, keepassxc,
                        keepassxc-csv, keeper, lastpass, networkmanager, myki,
                        pass, passpie, passwordexporter, pwsafe, revelation,
                        roboform, upm.
  file                  Path to the file or directory that contains the data
                        to import. Can also be a label.

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Import the passwords to a specific subfolder.
  -a, --all             Also import all the extra data present.
  -c, --clean           Make the paths more command line friendly.
  -C, --convert         Convert invalid caracters present in the paths.
  -s CAR, --sep CAR     Provide a caracter of replacement for the path
                        separator. Default: '-'
  --cols COLS           CSV expected columns to map columns to credential
                        attributes. Only used for the generic csv importer.
  --config CONFIG       Set a config file. Default: '.import'
  -l, --list            List the supported password managers.
  -f, --force           Overwrite existing path.
  -V, --version         Show the program version and exit.
  -q, --quiet           Be quiet.
  -v, --verbose         Be verbose.

More information may be found in the pass-import(1) man page.

```
<!-- USAGE END -->

See `man pass-import` for more information.

## Examples
**Import password from KeePass**
```
pass import keepassxml keepass.xml
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
pass import keepass keepass.kdbx
```

**Import password to a subfolder**
```
pass import keepassxml keepass.xml -p Import/
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

Example of the `.import` configuration file for the default password repository in `~/.password-store/.import`:
```yaml
---

# Separator string
separator: '-'

# The list of string that should be replaced by other string. Only activated
# if the `clean` option is enabled.
cleans:
  ' ': '-'
  '&': 'and'
  '@': At
  "'": ''
  '[': ''
  ']': ''

# The list of protocol. To be removed from the title.
protocols:
  - http://
  - https://

# The list of invalid caracters. Replaced by the separator.
invalids:
  - '<'
  - '>'
  - ':'
  - '"'
  - '/'
  - '\\'
  - '|'
  - '?'
  - '*'
  - '\0'
```

## Security consideration

Passwords should not be written in plain text form on the drive.
Therefore when possible you should import it directly from the encrypted data:
```sh
pass import keepass file.kdbx
```

Otherwise, if your password manager does not support it, you should take care
of securely removing the plain text password database:
```sh
pass import lastpass data.csv
shred -u data.csv
```

You might also want to update the passwords imported using [`pass-update`][update].

## Installation

**Requirements**
* `pass 1.7.0` or greater.
* Python 3.4+
* `python3-setuptools` to build and install it.
* `python3-yaml` (`apt install python3-yaml` or `pip3 install pyaml`)

**Optional Requirements**

| **Dependency** | **Required for** | **apt** | **pip** |
|:--------------:|:----------------:|:-------:|:-------:|
| [defusedxml] | XML based importers | `apt install python3-defusedxml` | `pip3 install defusedxml` |
| [pykeepass] | Keepass import from KDBX file | N/A | `pip3 install pykeepass` |
| [secretstorage] | Gnome Keyring import | `apt install python3-secretstorage` | `pip3 install secretstorage` |
| [cryptography] | AndOTP or Aegis encrypted import | `apt install python3-cryptography` | `pip3 install cryptography` |

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
wget https://github.com/roddhjav/pass-import/releases/download/v2.6/pass-import-2.6.tar.gz
tar xzf pass-import-2.6.tar.gz
cd pass-import-2.6
make
sudo make install  # For OSX: make install PREFIX=/usr/local
```

[Releases][releases] and commits are signed using [`06A26D531D56C42D66805049C5469996F0DF68EC`][keys].
You should check the key's fingerprint and verify the signature:
```sh
wget https://github.com/roddhjav/pass-import/releases/download/v2.6/pass-import-2.6.tar.gz.asc
gpg --recv-keys 06A26D531D56C42D66805049C5469996F0DF68EC
gpg --verify pass-import-2.6.tar.gz.asc
```

**Local install**

Alternatively, from git or a stable version you can do a local install with:
```sh
cd pass-import
make local
```


## Contribution
Feedback, contributors, pull requests are all very welcome. Please read the
[`CONTRIBUTING.md`](CONTRIBUTING.md) file for more details on the contribution process.


## License

    Copyright (C) 2017-2019  Alexandre PUJOL

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
[browserpass]: https://github.com/browserpass/browserpass-extension
[pass-otp]: https://github.com/tadfisher/pass-otp

[defusedxml]: https://github.com/tiran/defusedxml
[pyaml]: https://pyyaml.org/
[pykeepass]: https://github.com/pschmitt/pykeepass
[secretstorage]: https://secretstorage.readthedocs.io/en/latest/
[cryptography]: https://cryptography.io
