% pimport(1)
% pimport was written by Alexandre Pujol (alexandre@pujol.io)
% February 2024

# NAME

pimport —  A passwords importer swiss army knife

# SYNOPSIS

**pimport** [*options…*] *dst* *src* [*src*]

# DESCRIPTION

**pimport** is a passwords importer swiss army knife allowing you to import your password database to a password store repository conveniently. It natively supports import from <!-- NB BEGIN -->62<!-- NB END --> password managers, and export to <!-- NB EXPORT BEGIN -->8<!-- NB EXPORT END --> destination password managers. More manager support can easily be added.

Passwords are imported into the existing default password store, therefore the password store must have been initialized before.

By default, pass imports entries at the root of the password store and only keeps the main data (password, login, email, URL, group). This behaviour can be changed using the provided options. It handles duplicates and imports OTP secret.

# COMMAND

**pimport** [*options…*] *dst* *src* [*src*]

*dst*

: Refer to one of the supported destination password managers to which you want to export your data. The complete list of supported destination managers can be found in the section *SUPPORTED DESTINATION MANAGERS*.  It can also be found with `pimport --list-exporters`.

*src* [*src*]

: Can refer to two things: the path to the data to import or to the password manager name followed by the path to the data to import. If only the path to the data to import is given, pass-import automatically detects the data
  format to import. The complete list of supported managers can be found in the section *SUPPORTED MANAGERS*. It can also be found with `pimport --list-importers`.

`--out=<prefix>, or -o <prefix>`

: Provide a path where the destination password manager lives. It can be a file, a directory, or even a login depending on the manager.

`--root=<path>`, `-r <path>` and `--path=<path>`, `-p <path>`

: Specific root source and destination directory to use in the password store. Where *`--root`* refer to the source repository and will only import the password from a specific subfolder. *`--path`* refer to the destination repository and will import the passwords to a specific subfolder.

`--key=<path>`, `-k <path>`

: If required by a password manager, a key file can be given using the `--key` or `-k` option along with the path to the keyfile to use.

`--all`, `-a`

: Conserve and import all the data present in the backup file. Otherwise, only title, password, login, URL, comments, and group data are imported.

`--force`, `-f`

: The import process will overwrite existing password entry if it already exists.

`--clean`, `-c`

: Clean the password path in order to be more command line friendly.

`--convert`, `-C`

: Convert the invalid characters present in the paths before import. Invalid characters for both Windows and Unix systems are supported. The default separator replaces the invalid characters: '-'

`--sep=<char>`

: Provide a character of replacement for the path separator. Default: '-'

`--del=<char>`

: Provide an alternative CSV delimiter character. Default: ','

`--cols=<char>`

: Set the expected CSV columns to map columns to credential attributes. Only used for the generic csv importer.

`--config=<path>`

: pass-import will consider this config file instead of the default one *.import*.

`--list-importers`, `-l`

: Print the list of the available source password manager. With the verbose option (*-v*) it provides the python class name to use to be given as *src*. It can be useful to bypass the automatic format detection. Also support the quiet option (*-q*).

`--list-exporters`, `-e`

: Print the list of the available destination password manager. Support the quiet option (*-q*).

`--help`, `-h`

: Print the program usage. If the option is specified along with an argument and if this argument is a supported password manager, prints usage for this manager.

`--verbose`, `-v`

: Be more verbose. This option can be specified multiple times to set the verbosity level.

`--quiet`, `-q`

: Be quiet


# BASIC USAGE

To import password from any supported password manager simply run:
```sh
pimport <new_pm> path/to/passwords --out path/to/destination/pm
```

If *pimport* is not able to detect the format, you need to provide the password manager *<former_pm>* you want to import data from:
```sh
pimport <new_pm> <former_pm> path/to/passwords --out path/to/destination/pm
```

If you want to import data to a *pass*, run:
```sh
pass import <pm> path/to/passwords
```

# EXAMPLES

### Import Lastpass file to a keepass kdbx db

```sh
pimport keepass lastpass.csv --out keepass.kdbx
(*) Importing passwords from lastpass to keepass
 .  Passwords imported from: lastpass.csv
 .  Passwords exported to: keepass.kdbx
 .  Number of password imported: 6
 .  Passwords imported:
          Social/mastodon.social
          Social/twitter.com
          Social/news.ycombinator.com
          Servers/ovh.com/bynbyjhqjz
          Servers/ovh.com/jsdkyvbwjn
          Bank/aib
```

### Import a password store to a CSV file

```sh
pimport csv ~/.password-store --out file.csv`
```

### Import passwords from keepass to bitwarden in a subfolder
```sh
pimport bitwarden  keepass.kdbx --out <login> -p Import/
(*) Importing passwords from keepass to bitwarden
 .  Passwords imported from: keepass.kdbx
 .  Passwords exported to: <login>
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

### Other examples

- If the manager is not correctly detected, you can pass it at source argument
  ```sh
  pimport pass dashlane dashlane.csv --out ~/.password-store
  ```
- Import NetworkManager password on default dir
  ```sh
  pimport pass networkmanager --out ~/.password-store
  ```
- Import a NetworkManager INI file
  ```sh
  pimport pass nm.ini --out ~/.password-store
  ```
- Import a One password 1PIF
  ```sh
  pimport pass 1password.1pif
  ```
- Import a One password CSV
  ```sh
  pimport pass 1password.csv
  ```
- Import a Passman JSON file
  ```sh
  pimport pass passman.json
  ```
- Import Lastpass file to a keepass db
  ```sh
  pimport keepass lastpass.csv --out keepass.kdbx
  ```
- Import a password store to a CSV file
  ```sh
  pimport csv ~/.password-store --out file.csv
  ```

# SECURITY CONSIDERATION

## Direct import

Passwords should not be written in plain text form on the drive. Therefore, when possible, you should import it directly from the encrypted data. For instance, with an encrypted keepass database:

```sh
pimport pass keepass file.kdbx --out ~/.password-store
```

## Secure erasure

Otherwise, if your password manager does not support it, you should take care of securely removing the plain text password database:

```sh
pimport keepass lastpass data.csv
shred -u data.csv
```

## Encrypted file

Alternatively, pimport can decrypt gpg encrypted file before importing it. For example:


```sh
pimport keepass lastpass lastpass.csv.gpg
```

## Mandatory Access Control (MAC)

AppArmor profiles for *pimport* are available in **apparmor.d**.
If your distribution support AppArmor, you can clone the repository and run:

```sh
make
sudo make install pass-import
```

to only install these apparmor security profiles.

## Network

pimport only needs to establish network connection to support cloud based password manager. If you do not use these importers you can ensure pimport is not using the network by removing the *network* rules in the apparmor profile of pass-import.


# CONFIGURATION FILE

Some configurations can be read from a configuration file called *.import* if it is present at the root of the password repository. The configuration read from this file will be overwritten by their corresponding command-line option if present.

Example of the *.import* configuration file for the default password repository

: **zx2c4@laptop ~ $ cat .import**

```yml
---

# Separator string
separator: '-'

# The list of string that should be replaced by other string. Only activated
# if the `clean` option is enabled.
cleans:
  ' ': '-'
  '&': 'and'

# The list of protocol. To be removed from the title.
protocols:
  - http://

# The list of invalid characters. Replaced by the separator.
invalids:
  - '<'
  - '>'
```

# SUPPORTED DESTINATION MANAGERS

<!-- LIST DST BEGIN -->
### csv (csv) 

 You should use the --cols option to map columns to credential attributes.
 The recognized column names by pass-import are the following:
 'title', 'password', 'login', 'email', 'url', 'comments',
 'otpauth', 'group'
 ``title`` and ``group`` field are used to generate the password
 path. If you have otp data, they should be named as ``otpauth``.
 These are the *standard* field names. You can add any other field
 you want.



**Command:** pimport csv src [src]

### gopass (gopass) 
**Website:** *https://www.gopass.pw/*

**Command:** pimport gopass src [src]

### keepass (kdbx) 
**Website:** *https://www.keepass.info*

**Command:** pimport keepass src [src]

### keepassx2 (kdbx) 
**Website:** *https://www.keepassx.org*

**Command:** pimport keepassx2 src [src]

### keepassxc (kdbx) 
**Website:** *https://keepassxc.org*

**Command:** pimport keepassxc src [src]

### lastpass (cli) 
**Website:** *https://www.lastpass.com*

**Command:** pimport lastpass src [src]

### pass (pass) 
**Website:** *https://passwordstore.org*

**Command:** pimport pass src [src]

### sphinx  
**Website:** *https://github.com/stef/pwdsphinx/*

**Command:** pimport sphinx src [src]

<!-- LIST DST END -->

# SUPPORTED SOURCE MANAGERS

<!-- LIST BEGIN -->
### 1password (csv)  v8
**Website:** *https://1password.com*

**Export:** See this guide: https://support.1password.com/export

**Command:** pass import 1password file.csv

### 1password (1pif)  v4
**Website:** *https://1password.com*

**Export:** See this guide: https://support.1password.com/export

**Command:** pass import 1password file.1pif

### 1password (csv)  v4
**Website:** *https://1password.com*

**Export:** See this guide: https://support.1password.com/export

**Command:** pass import 1password file.csv

### 1password (csv)  v6
**Website:** *https://1password.com*

**Export:** See this guide: https://support.1password.com/export

**Command:** pass import 1password file.csv

### aegis (json) 
**Website:** *https://github.com/beemdevelopment/Aegis*

**Export:** Settings> Tools: Export Plain

**Command:** pass import aegis file.json

### aegis (json) 
**Website:** *https://github.com/beemdevelopment/Aegis*

**Export:** Settings> Tools: Export encrypted

**Command:** pass import aegis file.json

### andotp (json) 
**Website:** *https://github.com/andOTP/andOTP*

**Export:** Backups> Backup plain

**Command:** pass import andotp file.json

### apple-keychain (keychain) 
**Website:** *https://support.apple.com/guide/keychain-access*

**Export:** See this guide: https://gist.github.com/santigz/601f4fd2f039d6ceb2198e2f9f4f01e0

**Command:** pass import applekeychain file.txt

### bitwarden (csv) 
**Website:** *https://bitwarden.com*

**Export:** Tools> Export Vault> File Format: .csv

**Command:** pass import bitwarden file.csv

### bitwarden (csv) 
**Website:** *https://bitwarden.com*

**Export:** Tools> Export Vault> File Format: .csv

**Command:** pass import bitwarden file.csv

### bitwarden (json) 
**Website:** *https://bitwarden.com*

**Export:** Tools> Export Vault> File Format: .json

**Command:** pass import bitwarden file.json

### bitwarden (json) 
**Website:** *https://bitwarden.com*

**Export:** Tools> Export Vault> File Format: .json

**Command:** pass import bitwarden file.json

### blur (json) 
**Website:** *https://abine.com*

**Export:** Settings: Export Data: Export Blur Data

**Command:** pass import blur file.json

### blur (csv) 
**Website:** *https://abine.com*

**Export:** Settings: Export Data: Export CSV: Accounts: Export CSV

**Command:** pass import blur file.csv

### buttercup (csv) 
**Website:** *https://buttercup.pw*

**Export:** File > Export > Export File to CSV

**Command:** pass import buttercup file.csv

### chrome (csv) 
**Website:** *https://support.google.com/chrome*

**Export:** In chrome://password-manager/settings under 2Export passwordsDownload File

**Command:** pass import chrome file.csv

### chrome (csv) 
**Website:** *https://support.google.com/chrome*

**Export:** See this guide: https://support.google.com/chrome/answer/95606#see

**Command:** pass import chrome file.csv

### clipperz (html) 
**Website:** *https://clipperz.is*

**Export:** Settings > Data > Export: HTML + JSON

**Command:** pass import clipperz file.html

### csv (csv) 

 You should use the --cols option to map columns to credential attributes.
 The recognized column names by pass-import are the following:
 'title', 'password', 'login', 'email', 'url', 'comments',
 'otpauth', 'group'
 ``title`` and ``group`` field are used to generate the password
 path. If you have otp data, they should be named as ``otpauth``.
 These are the *standard* field names. You can add any other field
 you want.



**Export:** Nothing to do

**Command:** pass import csv file.csv --cols 'url,login,,password'

### dashlane (csv) 
**Website:** *https://www.dashlane.com*

**Export:** File > Export > Unsecured Archive in CSV

**Command:** pass import dashlane file.csv

### dashlane (json) 
**Website:** *https://www.dashlane.com*

**Export:** File > Export > Unsecured Archive in JSON

**Command:** pass import dashlane file.json

### encryptr (csv) 
**Website:** *https://spideroak.com/encryptr*

**Export:** Compile from source and follow instructions from this guide: https://github.com/SpiderOak/Encryptr/issues/295#issuecomment-322449705

**Command:** pass import encryptr file.csv

### enpass (json)  v6
**Website:** *https://www.enpass.io*

**Export:** Menu > File > Export > As JSON

**Command:** pass import enpass file.json

### enpass (csv) 
**Website:** *https://www.enpass.io*

**Export:** File > Export > As CSV

**Command:** pass import enpass file.csv

### firefox (csv) 
**Website:** *https://www.mozilla.org/en-US/firefox/lockwise/*

**Export:** In about:logins Menu: Export logins

**Command:** pass import firefox file.csv

### firefox (csv) 
**Website:** *https://github.com/kspearrin/ff-password-exporter*

**Export:** Add-ons Prefs: Export Passwords: CSV

**Command:** pass import firefox file.csv

### fpm (xml) 
**Website:** *http://fpm.sourceforge.net*

**Export:** File > Export Passwords: Plain XML

**Command:** pass import fpm file.xml

### freeotp+ (json) 
**Website:** *https://github.com/helloworld1/FreeOTPPlus*

**Export:** Settings> Export> Export JSON Format

**Command:** pass import freeotp+ file.json

### gnome (libsecret) 
**Website:** *https://wiki.gnome.org/Projects/GnomeKeyring*

 You can provide a gnome-keyring collection label to import. It can be empty
 to import all collections.



**Export:** Nothing to do

**Command:** pass import gnome-keyring <label>

### gnome-auth (json) 
**Website:** *https://gitlab.gnome.org/World/Authenticator*

**Export:** Backup > in a plain-text JSON file

**Command:** pass import gnome-authenticator file.json

### gopass (gopass) 
**Website:** *https://www.gopass.pw/*

**Export:** Nothing to do

**Command:** pass import gopass path/to/store

### gorilla (csv) 
**Website:** *https://github.com/zdia/gorilla/wiki*

**Export:** File > Export: Yes: CSV Files

**Command:** pass import gorilla file.csv

### kedpm (xml) 
**Website:** *http://fpm.sourceforge.net*

**Export:** File > Export Passwords: Plain XML

**Command:** pass import kedpm file.xml

### keepass (kdbx) 
**Website:** *https://www.keepass.info*

**Export:** Nothing to do

**Command:** pass import keepass file.kdbx

### keepass (csv) 
**Website:** *https://www.keepass.info*

**Export:** File > Export > Keepass (CSV)

**Command:** pass import keepass file.csv

### keepass (xml) 
**Website:** *https://www.keepass.info*

**Export:** File > Export > Keepass (XML)

**Command:** pass import keepass file.xml

### keepassx (xml) 
**Website:** *https://www.keepassx.org*

**Export:** File > Export to > Keepass XML File

**Command:** pass import keepassx file.xml

### keepassx2 (kdbx) 
**Website:** *https://www.keepassx.org*

**Export:** Nothing to do

**Command:** pass import keepassx2 file.kdbx

### keepassx2 (csv) 
**Website:** *https://www.keepassx.org*

**Export:** Database > Export to CSV File

**Command:** pass import keepassx2 file.csv

### keepassxc (kdbx) 
**Website:** *https://keepassxc.org*

**Export:** Nothing to do

**Command:** pass import keepassxc file.kdbx

### keepassxc (csv) 
**Website:** *https://keepassxc.org*

**Export:** Database > Export to CSV File

**Command:** pass import keepassxc file.csv

### keeper (csv) 
**Website:** *https://keepersecurity.com*

**Export:** Settings > Export : Export to CSV File

**Command:** pass import keeper file.csv

### lastpass (cli) 
**Website:** *https://www.lastpass.com*

**Export:** Nothing to do

**Command:** pass import lastpass <login>

### lastpass (csv) 
**Website:** *https://www.lastpass.com*

**Export:** More Options > Advanced > Export

**Command:** pass import lastpass file.csv

### myki (csv) 
**Website:** *https://myki.com*

**Export:** See this guide: https://support.myki.com/myki-app/exporting-your-passwords-from-the-myki-app/how-to-export-your-passwords-account-data-from-myki

**Command:** pass import myki file.csv

### network-manager (nm) 
**Website:** *https://wiki.gnome.org/Projects/NetworkManager*

 Support import from the installed network configuration but also from a
 specific directory of NetworkManager configuration file or from a given
 file.

 Example:
 -------
 - From directory of ini file: `pass import networkmanager dir/`.
 - From ini file: `pass import networkmanager file.ini`.



**Export:** Also support specific networkmanager dir and ini file

**Command:** pass import networkmanager

### nordpass (csv) 
**Website:** *https://nordpass.com/*

**Export:** Settings > Export Items

**Command:** pass import nordpass file.csv

### padlock (csv) 
**Website:** *https://padloc.app*

**Export:** Settings > Export Data and copy text into a .csv file

**Command:** pass import padlock file.csv

### pass (pass) 
**Website:** *https://passwordstore.org*

**Export:** Nothing to do

**Command:** pass import pass path/to/store

### passman (csv) 
**Website:** *https://passman.cc*

**Export:** Settings > Export credentials  > Export type: CSV

**Command:** pass import passman file.csv

### passman (json) 
**Website:** *https://passman.cc*

**Export:** Settings > Export credentials  > Export type: JSON

**Command:** pass import passman file.json

### passpack (csv) 
**Website:** *https://www.passpack.com*

**Export:** Settings > Export > Save to CSV

**Command:** pass import passpack file.csv

### passpie (yaml)  v1.0
**Website:** *https://www.enpass.io*

**Export:** `passpie export file.yml`

**Command:** pass import passpie file.yml

### pwsafe (xml) 
**Website:** *https://pwsafe.org*

**Export:** File > Export To > XML Format

**Command:** pass import pwsafe file.xml

### revelation (xml) 
**Website:** *https://revelation.olasagasti.info*

**Export:** File > Export: XML

**Command:** pass import revelation file.xml

### roboform (csv) 
**Website:** *https://www.roboform.com*

**Export:** Roboform > Options > Data & Sync > Export To: CSV file

**Command:** pass import roboform file.csv

### safeincloud (csv) 
**Website:** *https://safeincloud.ladesk.com/*

**Export:** File > Export > Comma-Separated Values (CSV)

**Command:** pass import safeincloud file.csv

### saferpass (csv) 
**Website:** *https://saferpass.net*

**Export:** Settings > Export Data: Export data

**Command:** pass import saferpass file.csv

### upm (csv) 
**Website:** *http://upm.sourceforge.net*

**Export:** Database > Export

**Command:** pass import upm file.csv

### zoho (csv) 
**Website:** *https://www.zoho.com/vault*

**Export:** Tools > Export Secrets: Zoho Vault Format CSV

**Command:** pass import zoho file.csv

### zoho (csv) 
**Website:** *https://www.zoho.com/vault*

**Export:** Tools > Export Secrets: Zoho Vault Format CSV

**Command:** pass import zoho file.csv

<!-- LIST END -->

# SEE ALSO
`pass(1)`, `pass-tomb(1)`, `pass-update(1)`, `pass-otp(1)`, `pimport(1)`, `pass-audit(1)`
