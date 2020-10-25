[<img src="https://gitlab.com/uploads/-/system/project/avatar/2296403/logo.png" align="right" height="110"/>][github-link]

# pass import

[![][travis]][travis-link] [![][gitlab]][gitlab-link] [![][coverage]][coverage-link] [![][quality]][quality-link] [![
][release]][release-link]

**A [pass] extension for importing data from most of the existing password manager.**


## Description
`pass import` is a password store extension allowing you to import your password
database to a password store repository conveniently. It natively supports
import from <!-- NB BEGIN -->53<!-- NB END --> different password managers.
More manager support can easily be added.

Passwords are imported into the existing default password store, therefore
the password store must have been initialised before with `pass init`.

By default, pass imports entries at the root of the password store and only keeps
the main data (password, login, email, URL, group). This behavior can be changed
using the provided options.

Pass import handles duplicates and is compatible with [browserpass]. It imports
OTP secret in a way that is compatible with [pass-otp].

pass-import also provides a `pimport` script that allows importing passwords to
other password managers. For instance, you can import passwords to a Keepass
database to a generic CSV file...

**The following password managers are supported:**

<!-- LIST BEGIN -->
<table>
  <thead>
    <th align="center">Password Manager</th>
    <th align="center">Formats</th>
    <th align="center">How to export Data</th>
    <th align="center">Command line</th>
  </thead>
  <tbody>
    <tr>
      <td align="center" rowspan="3"><a href="https://1password.com">1password</a></td>
      <td align="center"><code>csv v6</code></td>
      <td align="center"><i>See <a href="https://support.1password.com/export">this guide</a></i></td>
      <td align="center"><code>pass import 1password file.csv</code></td>
    </tr>
    <tr>
      <td align="center"><code>1pif v4</code></td>
      <td align="center"><i>See <a href="https://support.1password.com/export">this guide</a></i></td>
      <td align="center"><code>pass import 1password file.1pif</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv v4</code></td>
      <td align="center"><i>See <a href="https://support.1password.com/export">this guide</a></i></td>
      <td align="center"><code>pass import 1password file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://github.com/beemdevelopment/Aegis">aegis</a></td>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Settings> Tools: Export Plain</i></td>
      <td align="center"><code>pass import aegis file.json</code></td>
    </tr>
    <tr>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Settings> Tools: Export encrypted</i></td>
      <td align="center"><code>pass import aegis file.json</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://github.com/andOTP/andOTP">andotp</a></td>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Backups> Backup plain</i></td>
      <td align="center"><code>pass import andotp file.json</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://support.apple.com/guide/keychain-access">apple-keychain</a></td>
      <td align="center"><code>keychain</code></td>
      <td align="center"><i>See <a href="https://gist.github.com/santigz/601f4fd2f039d6ceb2198e2f9f4f01e0">this guide</a></i></td>
      <td align="center"><code>pass import applekeychain file.txt</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://bitwarden.com">bitwarden</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Tools> Export Vault> File Format: .csv</i></td>
      <td align="center"><code>pass import bitwarden file.csv</code></td>
    </tr>
    <tr>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Tools> Export Vault> File Format: .json</i></td>
      <td align="center"><code>pass import bitwarden file.json</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://abine.com">blur</a></td>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Settings: Export Data: Export Blur Data</i></td>
      <td align="center"><code>pass import blur file.json</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Settings: Export Data: Export CSV: Accounts: Export CSV</i></td>
      <td align="center"><code>pass import blur file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://buttercup.pw">buttercup</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>File > Export > Export File to CSV</i></td>
      <td align="center"><code>pass import buttercup file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://support.google.com/chrome">chrome</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>See <a href="https://support.google.com/chrome/answer/95606#see">this guide</a></i></td>
      <td align="center"><code>pass import chrome file.csv</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>See <a href="https://support.google.com/chrome/answer/95606#see">this guide</a></i></td>
      <td align="center"><code>pass import chrome file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://clipperz.is">clipperz</a></td>
      <td align="center"><code>html</code></td>
      <td align="center"><i>Settings > Data > Export: HTML + JSON</i></td>
      <td align="center"><code>pass import clipperz file.html</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="">csv</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Nothing to do</i></td>
      <td align="center"><code>pass import csv file.csv --cols 'url,login,,password'</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://www.dashlane.com">dashlane</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>File > Export > Unsecured Archive in CSV</i></td>
      <td align="center"><code>pass import dashlane file.csv</code></td>
    </tr>
    <tr>
      <td align="center"><code>json</code></td>
      <td align="center"><i>File > Export > Unsecured Archive in JSON</i></td>
      <td align="center"><code>pass import dashlane file.json</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://spideroak.com/encryptr">encryptr</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Compile from source and follow instructions from <a href="https://github.com/SpiderOak/Encryptr/issues/295#issuecomment-322449705">this guide</a></i></td>
      <td align="center"><code>pass import encryptr file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://www.enpass.io">enpass</a></td>
      <td align="center"><code>json v6</code></td>
      <td align="center"><i>Menu > File > Export > As JSON</i></td>
      <td align="center"><code>pass import enpass file.json</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>File > Export > As CSV</i></td>
      <td align="center"><code>pass import enpass file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://github.com/kspearrin/ff-password-exporter">firefox</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Add-ons Prefs: Export Passwords: CSV</i></td>
      <td align="center"><code>pass import firefox file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="http://fpm.sourceforge.net">fpm</a></td>
      <td align="center"><code>xml</code></td>
      <td align="center"><i>File > Export Passwords: Plain XML</i></td>
      <td align="center"><code>pass import fpm file.xml</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://github.com/helloworld1/FreeOTPPlus">freeotp+</a></td>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Settings> Export> Export JSON Format</i></td>
      <td align="center"><code>pass import freeotp+ file.json</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://wiki.gnome.org/Projects/GnomeKeyring">gnome</a></td>
      <td align="center"><code>libsecret</code></td>
      <td align="center"><i>Nothing to do</i></td>
      <td align="center"><code>pass import gnome-keyring &lt;label&gt;</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://gitlab.gnome.org/World/Authenticator">gnome-auth</a></td>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Backup > in a plain-text JSON file</i></td>
      <td align="center"><code>pass import gnome-authenticator file.json</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://github.com/zdia/gorilla/wiki">gorilla</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>File > Export: Yes: CSV Files</i></td>
      <td align="center"><code>pass import gorilla file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="http://fpm.sourceforge.net">kedpm</a></td>
      <td align="center"><code>xml</code></td>
      <td align="center"><i>File > Export Passwords: Plain XML</i></td>
      <td align="center"><code>pass import kedpm file.xml</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="3"><a href="https://www.keepass.info">keepass</a></td>
      <td align="center"><code>kdbx</code></td>
      <td align="center"><i>Nothing to do</i></td>
      <td align="center"><code>pass import keepass file.kdbx</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>File > Export > Keepass (CSV)</i></td>
      <td align="center"><code>pass import keepass file.csv</code></td>
    </tr>
    <tr>
      <td align="center"><code>xml</code></td>
      <td align="center"><i>File > Export > Keepass (XML)</i></td>
      <td align="center"><code>pass import keepass file.xml</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://www.keepassx.org">keepassx</a></td>
      <td align="center"><code>xml</code></td>
      <td align="center"><i>File > Export to > Keepass XML File</i></td>
      <td align="center"><code>pass import keepassx file.xml</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://www.keepassx.org">keepassx2</a></td>
      <td align="center"><code>kdbx</code></td>
      <td align="center"><i>Nothing to do</i></td>
      <td align="center"><code>pass import keepassx2 file.kdbx</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Database > Export to CSV File</i></td>
      <td align="center"><code>pass import keepassx2 file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://keepassxc.org">keepassxc</a></td>
      <td align="center"><code>kdbx</code></td>
      <td align="center"><i>Nothing to do</i></td>
      <td align="center"><code>pass import keepassxc file.kdbx</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Database > Export to CSV File</i></td>
      <td align="center"><code>pass import keepassxc file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://keepersecurity.com">keeper</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Settings > Export : Export to CSV File</i></td>
      <td align="center"><code>pass import keeper file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://www.lastpass.com">lastpass</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>More Options > Advanced > Export</i></td>
      <td align="center"><code>pass import lastpass file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://myki.com">myki</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>See <a href="https://support.myki.com/myki-app/exporting-your-passwords-from-the-myki-app/how-to-export-your-passwords-account-data-from-myki">this guide</a></i></td>
      <td align="center"><code>pass import myki file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://wiki.gnome.org/Projects/NetworkManager">network-manager</a></td>
      <td align="center"><code>nm</code></td>
      <td align="center"><i>Also support specific networkmanager dir and ini file</i></td>
      <td align="center"><code>pass import networkmanager</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://padloc.app">padlock</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Settings > Export Data and copy text into a .csv file</i></td>
      <td align="center"><code>pass import padlock file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://passwordstore.org">pass</a></td>
      <td align="center"><code>pass</code></td>
      <td align="center"><i>Nothing to do</i></td>
      <td align="center"><code>pass import pass path/to/store</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://passman.cc">passman</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Settings > Export credentials  > Export type: CSV</i></td>
      <td align="center"><code>pass import passman file.csv</code></td>
    </tr>
    <tr>
      <td align="center"><code>json</code></td>
      <td align="center"><i>Settings > Export credentials  > Export type: JSON</i></td>
      <td align="center"><code>pass import passman file.json</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://www.passpack.com">passpack</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Settings > Export > Save to CSV</i></td>
      <td align="center"><code>pass import passpack file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://www.enpass.io">passpie</a></td>
      <td align="center"><code>yaml v1.0</code></td>
      <td align="center"><i>`passpie export file.yml`</i></td>
      <td align="center"><code>pass import passpie file.yml</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://pwsafe.org">pwsafe</a></td>
      <td align="center"><code>xml</code></td>
      <td align="center"><i>File > Export To > XML Format</i></td>
      <td align="center"><code>pass import pwsafe file.xml</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://revelation.olasagasti.info">revelation</a></td>
      <td align="center"><code>xml</code></td>
      <td align="center"><i>File > Export: XML</i></td>
      <td align="center"><code>pass import revelation file.xml</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://www.roboform.com">roboform</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Roboform > Options > Data & Sync > Export To: CSV file</i></td>
      <td align="center"><code>pass import roboform file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="https://saferpass.net">saferpass</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Settings > Export Data: Export data</i></td>
      <td align="center"><code>pass import saferpass file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><a href="http://upm.sourceforge.net">upm</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Database > Export</i></td>
      <td align="center"><code>pass import upm file.csv</code></td>
    </tr>
    <tr>
      <td align="center" rowspan="2"><a href="https://www.zoho.com/vault">zoho</a></td>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Tools > Export Secrets: Zoho Vault Format CSV</i></td>
      <td align="center"><code>pass import zoho file.csv</code></td>
    </tr>
    <tr>
      <td align="center"><code>csv</code></td>
      <td align="center"><i>Tools > Export Secrets: Zoho Vault Format CSV</i></td>
      <td align="center"><code>pass import zoho file.csv</code></td>
    </tr>
  </tbody>
</table>
<!-- LIST END -->


**The following destination password managers are supported:**

<!-- LIST DST BEGIN -->
| **Exporters Password Manager** | **Format** | **Command line** |
|:------------------------------:|:----------:|:----------------:|
| [csv]() | csv | `pimport csv src [src]` |
| [keepass](https://www.keepass.info) | kdbx | `pimport keepass src [src]` |
| [keepassx2](https://www.keepassx.org) | kdbx | `pimport keepassx2 src [src]` |
| [keepassxc](https://keepassxc.org) | kdbx | `pimport keepassxc src [src]` |
| [pass](https://passwordstore.org) | pass | `pimport pass src [src]` |

<!-- LIST DST END -->

## Usage

### Basic use
To import password from any supported password manager simply run:
```sh
pass import path/to/passwords
```

If `pass-import` is not able to detect the format, you need provide the password
manager `<pm>` you want to import data from:
```sh
pass import <pm> path/to/passwords
```

If you want to import data to a password manager other than `pass`, run:
```sh
pimport <new_pm> <former_pm> path/to/passwords --out path/to/destination/pm
```

### Help
<!-- USAGE BEGIN -->
```
usage: pass import [-r path] [-p path] [-k KEY] [-a] [-f] [-c] [-C] [--sep CHAR] [--del CHAR] [--cols COLS]
                   [--config CONFIG] [-l] [-h] [-V] [-v | -q]
                   [src [src ...]]

  Import data from most of the password manager. Passwords are imported into
  the existing default password store; therefore, the password store must have
  been initialised before with 'pass init'.

Password managers:
  src                   Path to the data to import. Can also be the password manager name followed by the path to
                        the data to import. The password manager name can be: 1password, aegis, andotp, apple-
                        keychain, bitwarden, blur, buttercup, chrome, clipperz, csv, dashlane, encryptr, enpass,
                        firefox, fpm, freeotp+, gnome, gnome-auth, gorilla, kedpm, keepass, keepassx, keepassx2,
                        keepassxc, keeper, lastpass, myki, network-manager, padlock, pass, passman, passpack,
                        passpie, pwsafe, revelation, roboform, saferpass, upm, zoho

Common optional arguments:
  -r path, --root path  Only import the password from a specific subfolder.
  -p path, --path path  Import the passwords to a specific subfolder.
  -k KEY, --key KEY     Path to a keyfile if required by a manager.
  -a, --all             Also import all the extra data present.
  -f, --force           Overwrite existing passwords.
  -c, --clean           Make the paths more command line friendly.
  -C, --convert         Convert invalid characters present in the paths.

Extra optional arguments:
  --sep CHAR            Provide a characters of replacement for the path separator. Default: '-'
  --del CHAR            Provide an alternative CSV delimiter character. Default: ','
  --cols COLS           CSV expected columns to map columns to credential attributes. Only used by the csv importer.
  --config CONFIG       Set a config file. Default: '.import'

Help related optional arguments:
  -l, --list            List the supported password managers.
  -h, --help            Show this help message and exit.
  -V, --version         Show the program version and exit.
  -v, --verbose         Set verbosity level, can be used more than once.
  -q, --quiet           Be quiet.

More information may be found in the pass-import(1) man page.
```
<!-- USAGE END -->

Usage for `pimport` can been seen with `pimport -h` or `man pimport`.

## Examples

**Import password from KeePass**
```
pass import keepass.xml
(*) Importing passwords from keepass to pass
 .  Passwords imported from: keepass.xml
 .  Passwords exported to: ~/.password-store
 .  Number of password imported: 6
 .  Passwords imported:
       Social/mastodon.social
       Social/twitter.com
       Social/news.ycombinator.com
       Servers/ovh.com/bynbyjhqjz
       Servers/ovh.com/jsdkyvbwjn
       Bank/aib
```

This is the same than: `pimport pass keepass.xml --out ~/.password-store`

**Import password to a different password store**
```
export PASSWORD_STORE_DIR="~/.mypassword-store"
pass init <gpg-id>
pass import keepass.kdbx
```

**Import password to a subfolder**
```
pass import bitwarden.json -p Import/
(*) Importing passwords from bitwarden to pass
 .  Passwords imported from: bitwarden.json
 .  Passwords exported to: ~/.password-store
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

**Other examples:**
- If the manager is not correctly detected, you can pass it at source argument:
  `pass import dashlane dashlane.csv`
- Import NetworkManager password on default dir: `pass import networkmanager`
- Import a NetworkManager INI file: `pass import nm.ini`
- Import a One password 1PIF: `pass import 1password.1pif`
- Import a One password CSV: `pass import 1password.csv`
- Import a Passman JSON file: `pass import passman.json`
- Import Lastpass file to a keepass db: `pimport keepass lastpass.csv --out keepass.kdbx`
- Import a password store to a CSV file: `pimport csv ~/.password-store --out file.csv`


## GPG keyring

Before importing data to pass, your password-store repository must exist and your
GPG keyring must be usable. In order words you need to ensure that:
- All the public gpgids are present in the keyring.
- All the public gpgids are trusted enough.
- At least one private key is present in the keyring.

Otherwise you will get the following error:
`invalid credentials, password encryption/decryption aborted.`

To set the trust on a GPG key, one can run `gpg --edit-key <gpgid>` then `trust`.


## Security consideration

**Direct import**

Passwords should not be written in plain text form on the drive.
Therefore when possible, you should import it directly from the encrypted data.
For instance, with an encrypted keepass database:
```sh
pass import keepass file.kdbx
```

**Secure erasure**

Otherwise, if your password manager does not support it, you should take care
of securely removing the plain text password database:
```sh
pass import lastpass data.csv
shred -u data.csv
```

**Encrypted file**

Alternatively, pass-import can decrypt gpg encrypted file before importing it.
For example:
```sh
pass import lastpass lastpass.csv.gpg
```

You might also want to update the passwords imported using [`pass-update`][update].


## Configuration file

Some configurations can be read from a configuration file called `.import` if it
is present at the root of the password repository. The configuration read from
this file will be overwritten by their corresponding command-line option
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

# The list of protocols. To be removed from the title.
protocols:
  - http://
  - https://

# The list of invalid characters. Replaced by the separator.
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


## Installation

**Requirements**
* `pass 1.7.0` or greater.
* Python 3.6+
* `python3-setuptools` to build and install it.
* `python3-yaml` (`apt install python3-yaml` or `pip3 install pyaml`)

**Optional Requirements**

| **Dependency** | **Required for** | **apt** | **pip** |
|:--------------:|:----------------:|:-------:|:-------:|
| [defusedxml] | Recommended XML library | `apt install python3-defusedxml` | `pip3 install defusedxml` |
| [pykeepass] | Keepass import from KDBX file | N/A | `pip3 install pykeepass` |
| [secretstorage] | Gnome Keyring import | `apt install python3-secretstorage` | `pip3 install secretstorage` |
| [cryptography] | AndOTP or Aegis encrypted import | `apt install python3-cryptography` | `pip3 install cryptography` |
| [file-magic] | Detection of file decryption | `apt install python-magic` | `pip3 install file-magic` |

**ArchLinux**

`pass-import` is available in the [Arch User Repository][aur].
```sh
yay -S pass-import  # or your preferred AUR install method
```

**Debian/Ubuntu**

`pass-import` is available under my own debian repository with the package name
`pass-extension-import`. Both the repository and the package are signed with
my GPG key: [`06A26D531D56C42D66805049C5469996F0DF68EC`][keys].
```sh
wget -qO - https://pkg.pujol.io/debian/gpgkey | sudo apt-key add -
echo 'deb [arch=amd64] https://pkg.pujol.io/debian/repo all main' | sudo tee /etc/apt/sources.list.d/pkg.pujol.io.list
sudo apt-get update
sudo apt-get install pass-extension-import
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

**Using pip**
```sh
pip install pass-import
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
wget https://github.com/roddhjav/pass-import/releases/download/v3.1/pass-import-3.1.tar.gz
tar xzf pass-import-3.1.tar.gz
cd pass-import-3.1
make
sudo make install  # For OSX: make install PREFIX=/usr/local
```

[Releases][releases] and commits are signed using [`06A26D531D56C42D66805049C5469996F0DF68EC`][keys].
You should check the key's fingerprint and verify the signature:
```sh
wget https://github.com/roddhjav/pass-import/releases/download/v3.1/pass-import-3.1.tar.gz.asc
gpg --recv-keys 06A26D531D56C42D66805049C5469996F0DF68EC
gpg --verify pass-import-3.1.tar.gz.asc
```

**Local install**

Alternatively, from git or a stable version you can do a local install with:
```sh
cd pass-import
make local
```


## The import Library

One can use pass-import as a python library. Simply import the classes of the
password manager you want to import and export. Then use them in a
context manager. For instance, to import password from a cvs Lastpass exported
file to password-store:

```python
from pass_import.managers.lastpass import LastpassCSV
from pass_import.managers.passwordstore import PasswordStore

with LastpassCSV('lastpass-export.csv') as importer:
    importer.parse()

    with PasswordStore('~/.password-store') as exporter:
        exporter.data = importer.data
        exporter.clean()
        for entry in exporter.data:
            exporter.insert(entry)
```

Alternatively, you can import the same Lastpass file to a Keepass database:

```python
from pass_import.managers.keepass import Keepass
from pass_import.managers.lastpass import LastpassCSV

with LastpassCSV('lastpass-export.csv') as importer:
    importer.parse()

    with Keepass('keepass.kdbx') as exporter:
        exporter.data = importer.data
        exporter.clean()
        for entry in exporter.data:
            exporter.insert(entry)
```


## Contribution
Feedback, contributors, pull requests are all very welcome. Please read the
[`CONTRIBUTING.md`](CONTRIBUTING.md) file for more details on the contribution process.


## License

    Copyright (C) 2017-2020  Alexandre PUJOL

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

[github-link]: https://github.com/roddhjav/pass-import
[travis]: https://img.shields.io/travis/roddhjav/pass-import/master.svg?style=flat-square
[travis-link]: https://travis-ci.com/roddhjav/pass-import
[gitlab]: https://gitlab.com/roddhjav/pass-import/badges/master/pipeline.svg?style=flat-square
[gitlab-link]: https://gitlab.com/roddhjav/pass-import/pipelines
[coverage]: https://gitlab.com/roddhjav/pass-import/badges/master/coverage.svg?style=flat-square
[coverage-link]: https://roddhjav.gitlab.io/pass-import/
[quality]: https://img.shields.io/codacy/grade/783d8cf291434d2b8f1c063b51cfebbb/master.svg?style=flat-square
[quality-link]: https://www.codacy.com/app/roddhjav/pass-import
[release]: https://img.shields.io/github/release/roddhjav/pass-import.svg?maxAge=600&style=flat-square
[release-link]: https://github.com/roddhjav/pass-import/releases/latest

[pass]: https://www.passwordstore.org/
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
[file-magic]: https://www.darwinsys.com/file/
