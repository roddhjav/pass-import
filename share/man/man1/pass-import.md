% pass-import(1)
% pass import was written by Alexandre Pujol (alexandre@pujol.io)
% February 2022

# NAME

pass-import — A **pass**(1) extension for importing data from most of
the existing password manager.

# SYNOPSIS

**pass import** [*options…*] *src* [*src*]

# DESCRIPTION

**pass import** is a password store extension allowing you to import your
password database to a password store repository conveniently. It natively
supports import from <!-- NB BEGIN --><!-- NB END --> different password
managers. More manager support can easily be added.

Passwords are imported into the existing default password store; therefore,
the password store must have been initialised before with **pass init**.

By default, pass imports entries at the root of the password store and only
keeps the primary data (password, login, email, URL, group). This behavior can
be changed using the provided options.

Pass import handles duplicates and is compatible with *browserpass*. It
imports OTP secret in a way that is compatible with *pass-otp*.

# COMMAND

**pass import** [*options…*] *src* [*src*]

*src* [*src*]

: Can refer to two things: the path to the data to import or to the
  password manager name followed by the path to the data to import. If only the
  path to the data to import is given, pass-import automatically detects the data
  format to import. The complete list of supported managers can be found in the
  section *SUPPORTED MANAGERS*. It can also be found with `pass import --list`.

`--root=<path>`, `-r <path>` and `--path=<path>`, `-p <path>`

: Specific root source and destination directory to use in the password store.
  Where *`--root`* refer to the source repository and will only import the password from a specific subfolder. *`--path`* refer to the destination repository and
  will import the passwords to a specific subfolder.

`--key=<path>`, `-k <path>`

: If required by a password manager, a key file can be given using the
  `--key` or `-k` option along with the path to the keyfile to use.

`--all`, `-a`

: Conserve and import all the data present in the backup file. Otherwise, only
  title, password, login, URL, comments, and group data are imported.

`--force`, `-f`

: The import process will overwrite existing password entry if it already exists.

`--clean`, `-c`

: Clean the password path in order to be more command line friendly.

`--convert`, `-C`

: Convert the invalid characters present in the paths before import. Invalid
  characters for both Windows and Unix systems are supported. The default separator
  replaces the invalid characters: '-'

`--sep=<char>`

: Provide a character of replacement for the path separator. Default: '-'

`--del=<char>`

: Provide an alternative CSV delimiter character. Default: ','

`--cols=<char>`

: Set the expected CSV columns to map columns to credential attributes. Only used
  for the generic csv importer.

`--config=<path>`

: pass-import will consider this config file instead of the default one *.import*.

`--list`, `-l`

: Print the list of the available password manager. With the verbose
  option (*-v*) it provides the python class name to use to be given as *src*.
  It can be useful to bypass the automatic format detection. Also support the
  quiet option (*-q*).

`--help`, `-h`

: Print the program usage. If the option is specified along with an argument and
  if this argument is a supported password manager, prints usage for this manager.

`--verbose`, `-v`

: Be more verbose. This option can be specified multiple times to set the
  verbosity level.

`--quiet`, `-q`

: Be quiet


# BASIC USAGE

To import password from any supported password manager simply run:
```sh
pass import path/to/passwords
```

If *pass-import* is not able to detect the format, you need provide the password
manager *<pm>* you want to import data from:
```sh
pass import <pm> path/to/passwords
```

If you want to import data to a password manager other than *pass*, run:
```sh
pimport <new_pm> <former_pm> path/to/passwords --out path/to/destination/pm
```

# EXAMPLES

### Import password from KeePass

```sh
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

This is the same than: *pimport pass keepass.xml --out ~/.password-store*

### Import password to a different password store

```sh
export PASSWORD_STORE_DIR="~/.mypassword-store"
pass init <gpg-id>
pass import keepass.kdbx
```

## Import password to a subfolder

```sh
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

### Other examples

- If the manager is not correctly detected, you can pass it at source argument
  ```sh
  pass import dashlane dashlane.csv
  ```
- Import NetworkManager password on default dir
  ```sh
  pass import networkmanager
  ```
- Import a NetworkManager INI file
  ```sh
  pass import nm.ini
  ```
- Import a One password 1PIF
  ```sh
  pass import 1password.1pif
  ```
- Import a One password CSV
  ```sh
  pass import 1password.csv
  ```
- Import a Passman JSON file
  ```sh
  pass import passman.json
  ```
- Import Lastpass file to a keepass db
  ```sh
  pimport keepass lastpass.csv --out keepass.kdbx
  ```
- Import a password store to a CSV file
  ```sh
  pimport csv ~/.password-store --out file.csv
  ```

# GPG KEYRING

Before importing data to pass, your password-store repository must exist and your
GPG keyring must be usable. In order words you need to ensure that:

- All the public gpgids are present in the keyring.
- All the public gpgids are trusted enough.
- At least one private key is present in the keyring.

Otherwise you will get the following error:
*invalid credentials, password encryption/decryption aborted.*. 
To set the trust on a GPG key, one can run `gpg --edit-key <gpgid>` then `trust`.

# SECURITY CONSIDERATION

## Direct import

Passwords should not be written in plain text form on the drive.
Therefore when possible, you should import it directly from the encrypted data.
For instance, with an encrypted keepass database:

```sh
pass import keepass file.kdbx
```

## Secure erasure

Otherwise, if your password manager does not support it, you should take care
of securely removing the plain text password database:

```sh
pass import lastpass data.csv
shred -u data.csv
```

## Encrypted file

Alternatively, pass-import can decrypt gpg encrypted file before importing it.
For example:

```sh
pass import lastpass lastpass.csv.gpg
```

## Mandatory Access Control (MAC)

AppArmor profiles for *pass* and *pass-import* are available in **apparmor.d**.
If your distribution support AppArmor, you can clone the repository and run:

```sh
sudo ./pick pass pass-import
```

to only install these apparmor security profiles.

## Network

pass-import only needs to etablish network connection to support cloud based password manager. If you do not use these importers you can ensure pass-import is
not using the network by removing the *network* rules in the apparmor profile of
pass-import.

## Password Update

You might also want to update the passwords imported using **pass-update**(1).

# CONFIGURATION FILE

Some configurations can be read from a configuration file called *.import* if
it is present at the root of the password repository. The configuration read from
this file will be overwritten by their corresponding command-line option
if present.

Example of the .import configuration file for the default password repository

: **zx2c4@laptop ~ $ cat ~/.password-store/.import**

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

# SUPPORTED MANAGERS

<!-- LIST BEGIN -->
<!-- LIST END -->

# SEE ALSO
`pass(1)`, `pass-tomb(1)`, `pass-update(1)`, `pass-otp(1)`, `pimport(1)`, `pass-audit(1)`
