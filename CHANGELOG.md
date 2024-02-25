# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog].

## [3.5] - 2024-02-25

### Added

- Add the new filter option [#208](https://github.com/roddhjav/pass-import/pull/208)

### Changed

- Update chrome CSV format [#200](https://github.com/roddhjav/pass-import/pull/200)
- Add a unified way to generate otpauth url.
- Support 1PIF file format for 1Password v7.9 [#207](https://github.com/roddhjav/pass-import/pull/207)
- Set a timeout to the audit api.

## [3.4] - 2022-12-10

### Added

- Added a `--dry-run` option [#188](https://github.com/roddhjav/pass-import/issues/188)

### Changed

- Dropped support for python 3.7
- The manpage is now generated during the release process. Dropped pandoc build deps. [#192](https://github.com/roddhjav/pass-import/issues/192), [#186](https://github.com/roddhjav/pass-import/issues/186).
- Automated release process.

### Fixed

- Fix KDBX import bug  [#190](https://github.com/roddhjav/pass-import/pull/190)


## [3.3] - 2022-09-10

### Added

- Added password audit support.
- Added haveibeenpwned.com audit integration (require the `--pwned` option).
- Add support for pwdsphinx [#183](https://github.com/roddhjav/pass-import/pull/183)
- Add support for nordpass [#178](https://github.com/roddhjav/pass-import/pull/178)
- Add support for 1Password8 [#169](https://github.com/roddhjav/pass-import/pull/169)
- Add support for SafeInCloud [#168](https://github.com/roddhjav/pass-import/pull/168)
- Add support for Lastpass CLI (with `lpass`) import & export.
- Read OTP from 1Password's 1pif format [#157](https://github.com/roddhjav/pass-import/pull/157)
- Add support fot Bitwarden Organisation export in CSV & JSON. 

### Changed

- Support for python 3.10, dropped support for python 3.6
- Remove Travis CI in favor of Github Action.
- The man pages are now generated from markdown with pandoc.
- Various refractor, style and linter improvments.

### Fixed

- Fix KDBX export group creation [#185](https://github.com/roddhjav/pass-import/pull/185)
- Fix pykeepass use of find_groups path parameter [#182](https://github.com/roddhjav/pass-import/pull/182)
- Honor sroot in passwordstore exports [#181](https://github.com/roddhjav/pass-import/pull/181)
- As safety measure, terminate the GnuPG commandline [#165](https://github.com/roddhjav/pass-import/pull/165)
- Raise an exception upon invalid LastPass CSV data. [#156](https://github.com/roddhjav/pass-import/pull/156)
- Fix possible path corruption in deduplication. [#154](https://github.com/roddhjav/pass-import/issues/154) [#155](https://github.com/roddhjav/pass-import/pull/155)
- Other various fixed on multiple password managers.


## [3.2] - 2021-05-16

### Added
- Keepass: initial support for TOTP [#137](https://github.com/roddhjav/pass-import/pull/137)
- Add support for modern firefox import. [#134](https://github.com/roddhjav/pass-import/issues/134)
- Keepass: enable reference substitution [#132](https://github.com/roddhjav/pass-import/pull/132)
- Add gopass support [#130](https://github.com/roddhjav/pass-import/pull/130)

### Changed
- Fully deprecate Makefile in favor of setup.py
- Make pimport a setuptools script [#138](https://github.com/roddhjav/pass-import/pull/138)
- Support for `pykeepass` 4.0.0 [#136](https://github.com/roddhjav/pass-import/issues/136)
- Support for python 3.9

### Fixed
- Update Dashlane Json format [#133](https://github.com/roddhjav/pass-import/issues/133) 
- Fix importer var name. [#127](https://github.com/roddhjav/pass-import/issues/127) 
- Fix install for MacOS. [#125](https://github.com/roddhjav/pass-import/pull/125)
- Update Bitwarden Json format. [#123](https://github.com/roddhjav/pass-import/issues/123) 


## [3.1] - 2020-10-25

### Added
- Support for direct classname selection.
- Support for `pyhton-magic` [#115](https://github.com/roddhjav/pass-import/pull/115)
- Support for the `--root` option in keepass.  [#112](https://github.com/roddhjav/pass-import/issues/112) 
- Support for custom fields in Bitwarden. [#111](https://github.com/roddhjav/pass-import/pull/111) 

### Changed
- Use setup.py to manage the full installation.
- Support for `pykeepass` 3.2.1

### Fixed
- Ensure each pass entry has a name. [#118](https://github.com/roddhjav/pass-import/issues/118)
- Rewrite PasswordStore.list() with Pathlib. [#109](https://github.com/roddhjav/pass-import/pull/109)
- New Chrome documentation. [#106](https://github.com/roddhjav/pass-import/pull/106)
- Ensure the password manager action is a capability. [#105](https://github.com/roddhjav/pass-import/issues/105)
- Fix import.bash path in local make target [#104](https://github.com/roddhjav/pass-import/pull/104)
- Ensure the magic module is `file-magic`. [#103](https://github.com/roddhjav/pass-import/issues/103)
- Update Buttercup CSV format. [#102](https://github.com/roddhjav/pass-import/issues/102)


## [3.0] - 2020-04-26

It is the second major rewrite of pass-import. pass import was originally
written as a wrapper for a few scripts to import passwords to password-store.
Then, in version `2.0`, a first full rewrite has been done. pass-import was
a small python script that can natively import password to pass.

From `v3.0`, pass-import became a real python program that can be used as it
or as a library to import passwords. It also supports more than pass as a
targeted password manager.


### Added
- pass-import is now password manager agnostic, meaning it is not linked to
  password-store anymore. More destination password manager support will be
  added in future releases. In this release, it supports the following
  destination password manager:
  * `keepass`
  * `csv`
  * and also to `pass`.

- For a given manager name, pass-import automatically detects the format of the
  file to import and uses the importer accordingly.
- pass-import can file encrypted by one of the supported algo before to import it.
- pass import is now available in three way:
  * As a `pass` extension `pass import`
  * As an independant command line program: `pimport`
  * As a python library `pass_import`

- Added support for the following password managers:
  * Bitwarden (json)
  * Clipperz (html)
  * Dashlane (json)
  * Freeotp+ (json)
  * Padlock (csv)
  * Passman (csv and json)
  * Passpack (csv)
  * Saferpass (csv)
  * Zoho (csv)

- Added Debian packaging.
- Added pip packaging.

### Changed
- The command line interface changed completly. See `pass import -h`
- The old password manager name are not valid anymore
- Removed old bash tests
- Dropped support for python 3.4 & python 3.5
- Implement changing of CSV delimiter character [#88](https://github.com/roddhjav/pass-import/pull/88)
- Handle field names of Revelation entry types other than Generic [#82](https://github.com/roddhjav/pass-import/pull/82)
- Better entry name deduplication [#81](https://github.com/roddhjav/pass-import/pull/81)

### Fixed
- Fixed errored error message when missing optional dependencies [#97](https://github.com/roddhjav/pass-import/issues/97)
- Use human dates for AppleKeychain [#85](https://github.com/roddhjav/pass-import/pull/85)
- Handle missing pif web form field name
- Do not interpret password names as flags [#93](https://github.com/roddhjav/pass-import/pull/93)


## [2.6] - 2019-08-06

### Added
- Added support for generic OTP entry import
- Added support for binary attachements for manager that support it. [#63](https://github.com/roddhjav/pass-import/issues/63)
- Added support for the 10 following password managers: [#84](https://github.com/roddhjav/pass-import/pull/84)
  * passpie
  * keeper
  * keepass with kdbx file
  * Gnome Keyring
  * AndOTP for:
    - password encrypted backup,
    - plain text backup,
    - GPG encrypted backup.
  * Aegis for:
    * plain backup,
    * password encrypted backup.
  * Myki
  * Gnome Authenticator
  * Generic CSV
  * password-store (yes it can import itself ;))

- Added Importer docstring.
- Added full docstring.
- Added zsh completion.
- Added the following optional dependencies:
  * `pykeepass`: Keepass import from KDBX file,
  * `secretstorage`: Gnome Keyring import,
  * `cryptography`: AndOTP & Aegis encrypted import.

### Changed
- Changed the config file format from `ini` to `yaml`.
- The config file now accept much more settings.
- The default Keepass, KeepassX2 and KkeepassXC importers now use Kdbx importer.
- Defusedxml is now an optional dependency only required for XML based import.
- Improve GPG key listing check.
- Dropped the support for reading data file from stdin due to issues with a
  lot of password managers.
- The README and the man page are now automatically updated with the data from
  the importer docstring.

### Fixed
- Remove OS separaror from title [#64](https://github.com/roddhjav/pass-import/issues/64)
- Add `\t` to the clean least [#65](https://github.com/roddhjav/pass-import/issues/65)
- Fix some typos [#83](https://github.com/roddhjav/pass-import/issues/83)


## [2.5] - 2019-19-05

### Added
- Added a local install command with: `make local`.
- Added support for Enpass 6: `pass import enpass6` [#73](https://github.com/roddhjav/pass-import/pull/73)
- Added support for Buttercup: `pass import buttercup` [#74](https://github.com/roddhjav/pass-import/pull/74)
- Added support for Apple Keychain: `pass import applekeychain` [#79](https://github.com/roddhjav/pass-import/pull/79)
- Add support for Encryptr: `pass import encryptr` [#80](https://github.com/roddhjav/pass-import/pull/80)

### Changed
- Renamed the `--extra`, `-e` option into `--all`, `-a`.
- Changed the way to collect password entries.
- Added missing unit tests to achieve 100% coverage.
- The importer tests have been simplified and are much more strict and do not allow partial import.

### Fixed
- The extra/all option was not implemented for XML based importer. [#66](https://github.com/roddhjav/pass-import/issues/66)
- Wrong python prefix for debian based distribution [#67](https://github.com/roddhjav/pass-import/issues/67)
- Use the separator when cleaning data. [#78](https://github.com/roddhjav/pass-import/issues/78)


## [2.4] - 2018-12-02

### Added
- Added support for UPM (Universal Password Manager) with the command `upm`.
- Ensure the GPG recipients are in the keyring before to import. [#54](https://github.com/roddhjav/pass-import/issues/54)
- Ensure the success messages print real data. [#54](https://github.com/roddhjav/pass-import/issues/54)
- Added completion for bash.
- Add a `--convert`, `-C` option to convert not allowed in path. [#55](https://github.com/roddhjav/pass-import/issues/55)
- Add a `--separator` option to set a different character of replacement when converting not allowed characters. [#56](https://github.com/roddhjav/pass-import/issues/56)
- Add a `.import` configuration file for import personalisation. [#56](https://github.com/roddhjav/pass-import/issues/56)

### Changed
- Changed the extension structure to a classic python program: [#53](https://github.com/roddhjav/pass-import/issues/53)
  * The extension is now installed using setuptools for the python part,
  * Use `prospector` and `bandit` as python linter tool and security checker,
  * Add Gitlab CI,
  * Add SAST [security dashboard](https://gitlab.com/roddhjav/pass-import/security/dashboard),
  * Simplify the tests.

- Changed the way to handle duplicated path.
  * Create sub-folder if the titles are identical. [#41](https://github.com/roddhjav/pass-import/issues/41) [#49](https://github.com/roddhjav/pass-import/issues/49)
  * Use the new separator to duplicate paths. [#43](https://github.com/roddhjav/pass-import/issues/43)

### Fixed
- Stop assuming a title cannot be empty. [#57](https://github.com/roddhjav/pass-import/issues/57)
- Import fix for the importers:
  1. `KeepassX`, [#48](https://github.com/roddhjav/pass-import/pull/48)
  2. `Keepass`. [#52](https://github.com/roddhjav/pass-import/pull/52)

Special thanks to [@christian-weiss](github.com/christian-weiss) for all its
feedbacks.


## [2.3] - 2018-07-19

### Added
- Add support for the following importers:
  * KeepassX 2 (`keepassx2`) [#45](https://github.com/roddhjav/pass-import/issues/45)
  * Chrome with sqlite3 (`chromesqlite`) [#42](https://github.com/roddhjav/pass-import/issues/42)
  * NetworkManager to import wifi passwords (`networkmanager`) [#39](https://github.com/roddhjav/pass-import/pull/39)

- Add a nice error if defusedxml is not present [#24](https://github.com/roddhjav/pass-import/issues/24)
- Add the few missing unit tests
- Add changelog

### Changed
- Firefox: support FF-Password-Exporter instead of Password Exporter. [#40](https://github.com/roddhjav/pass-import/issues/40)


## [2.2] - 2018-03-18

### Added
- Add support for 1PIF file [#36](https://github.com/roddhjav/pass-import/pull/36).

### Changed
- Important clean-up & code improvement [#34](https://github.com/roddhjav/pass-import/pull/34).
- Pwsafe: add support for:
  * Multiline notes [#29](https://github.com/roddhjav/pass-import/pull/29),
  * Password history [#30](https://github.com/roddhjav/pass-import/pull/30),
  * Email [#32](https://github.com/roddhjav/pass-import/pull/32).

- Do not remove protocol in url [#31](https://github.com/roddhjav/pass-import/pull/31).
- Update chrome CSV format for Chrome 66 [#26](https://github.com/roddhjav/pass-import/pull/26) & [#27](https://github.com/roddhjav/pass-import/pull/27).
- Update 1password format [#27](https://github.com/roddhjav/pass-import/pull/27) & [#28](https://github.com/roddhjav/pass-import/pull/28).

### Fixed
- Fix typos & improve code coverage.


## [2.1] - 2017-12-21

### Added
- Add support for bitwarden [#19](https://github.com/roddhjav/pass-import/pull/19).

### Fixed
- Fix typos [#22](https://github.com/roddhjav/pass-import/pull/22)
- Fix a lot of python linter errors.
- Improve installation documentation.


## [2.0] - 2017-12-03

### Changed
`pass-import` now natively supports import from other password manager and
therefore, it does not require the importer scripts any-more. Moreover, all the
importer's systems have been intensely tested against a test database.

**pass-import now supports the following 17 password managers:**
- 1password6
- 1password4
- cautionhrome
- dashlane
- enpass
- fpm
- gorilla
- kedpm
- keepass
- keepasscsv
- keepassx
- keepassxc
- lastpass
- passwordexporter
- pwsafe
- revelation
- roboform


## [1.0] - 2017-12-01

### Fixed
- KDE wallet: unicode bugfix [#16](https://github.com/roddhjav/pass-import/pull/16).


## [0.2] - 2017-09-15

### Added
- keepass2csv: add username and do not add empty lines [#13](https://github.com/roddhjav/pass-import/pull/13).
- Add Enpass [#9](https://github.com/roddhjav/pass-import/pull/9).
- Add Chrome importer [#3](https://github.com/roddhjav/pass-import/pull/3).

### Fixed
- Lastpass: Ensure UTF-8 encoding [#5](https://github.com/roddhjav/pass-import/pull/5).


## [0.1] - 2017-09-01

- Initial release.

[3.5]: https://github.com/roddhjav/pass-import/releases/tag/v3.5
[3.4]: https://github.com/roddhjav/pass-import/releases/tag/v3.4
[3.3]: https://github.com/roddhjav/pass-import/releases/tag/v3.3
[3.2]: https://github.com/roddhjav/pass-import/releases/tag/v3.2
[3.1]: https://github.com/roddhjav/pass-import/releases/tag/v3.1
[3.0]: https://github.com/roddhjav/pass-import/releases/tag/v3.0
[2.7]: https://github.com/roddhjav/pass-import/releases/tag/v2.7
[2.6]: https://github.com/roddhjav/pass-import/releases/tag/v2.6
[2.5]: https://github.com/roddhjav/pass-import/releases/tag/v2.5
[2.4]: https://github.com/roddhjav/pass-import/releases/tag/v2.4
[2.3]: https://github.com/roddhjav/pass-import/releases/tag/v2.3
[2.2]: https://github.com/roddhjav/pass-import/releases/tag/v2.2
[2.1]: https://github.com/roddhjav/pass-import/releases/tag/v2.1
[2.0]: https://github.com/roddhjav/pass-import/releases/tag/v2.0
[1.0]: https://github.com/roddhjav/pass-import/releases/tag/v1.0
[0.2]: https://github.com/roddhjav/pass-import/releases/tag/v0.2
[0.1]: https://github.com/roddhjav/pass-import/releases/tag/v0.1

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
