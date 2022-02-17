% pimport(1)
% pimport was written by Alexandre Pujol (alexandre@pujol.io)
% February 2022

# NAME

pimport —  A passwords importer swiss army knife

# SYNOPSIS

**pimport** [*options…*] *dst* *src* [*src*]

# DESCRIPTION

**import** is a passwords importer swiss army knife allowing you to import
your password database to your new password manager repository conveniently.
It natively supports import from <!-- NB BEGIN --><!-- NB END --> password
managers, and export to <!-- NB EXPORT BEGIN --><!-- \# NB EXPORT END -->
destination password managers. More manager support can easily be added.

Passwords are imported into an existing password repository; therefore, the
password repository must have been initialised before.

By default, pimport imports entries at the root of the password store and only
keeps the primary data (password, login, email, URL, group). This behaviour can
be changed using the provided options. It also handles duplicates and support
OTP secret.

# COMMAND

**pimport** [*options…*] *dst* *src* [*src*]

*dst*

: Refer to one of the supported destination password managers to which you want
  to export your data. The complete list of supported destination managers can
  be found in the section *SUPPORTED DESTINATION MANAGERS*.  It can also be
  found with `pimport --list-exporters`.

*src* [*src*]

: Can refer to two things: the path to the data to import or to the
  password manager name followed by the path to the data to import. If only the
  path to the data to import is given, pass-import automatically detects the data
  format to import. The complete list of supported managers can be found in the
  section *SUPPORTED MANAGERS*. It can also be found with
  `pimport --list-importers`.

`--out=<prefix>, or -o <prefix>`

: Provide a path where the destination password manager lives. It can be a file,
  a directory, or even a login depending on the manager.

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

`--list-importers`, `-l`

: Print the list of the available source password manager. With the verbose
  option (*-v*) it provides the python class name to use to be given as *src*.
  It can be useful to bypass the automatic format detection. Also support the
  quiet option (*-q*).

`--list-exporters`, `-e`

: Print the list of the available destination password manager. Support the
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
pimport <new_pm> path/to/passwords --out path/to/destination/pm
```

If *pimport* is not able to detect the format, you need provide the password
manager *<former_pm>* you want to import data from:
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

Passwords should not be written in plain text form on the drive.
Therefore when possible, you should import it directly from the encrypted data.
For instance, with an encrypted keepass database:

```sh
pimport pass keepass file.kdbx --out ~/.password-store
```

## Secure erasure

Otherwise, if your password manager does not support it, you should take care
of securely removing the plain text password database:

```sh
pimport keepass lastpass data.csv
shred -u data.csv
```

## Encrypted file

Alternatively, pass-import can decrypt gpg encrypted file before importing it.
For example:

```sh
pimport keepass lastpass lastpass.csv.gpg
```

## Mandatory Access Control (MAC)

AppArmor profiles for *pimport* is available in **apparmor.d**.
If your distribution support AppArmor, you can clone the repository and run:

```sh
sudo ./pick pass-import
```

to only install these apparmor security profiles.

## Network

pimport only needs to etablish network connection to support cloud based password manager. If you do not use these importers you can ensure pimport is
not using the network by removing the *network* rules in the apparmor profile of
pimport.


# CONFIGURATION FILE

Some configurations can be read from a configuration file called *.import* if
it is present at the root of the password repository. The configuration read from
this file will be overwritten by their corresponding command-line option
if present.

Example of the .import configuration file for the default password repository

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
<!-- LIST DST END -->

# SUPPORTED SOURCE MANAGERS

<!-- LIST BEGIN -->
<!-- LIST END -->

# SEE ALSO
`pass(1)`, `pass-tomb(1)`, `pass-update(1)`, `pass-otp(1)`, `pimport(1)`, `pass-audit(1)`
