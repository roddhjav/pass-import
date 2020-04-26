Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_.


`3.0`_ - 2020-04-26
-------------------

It is the second major rewrite of pass-import. pass import was originally
written as a wrapper for a few scripts to import passwords to password-store.
Then, in version ``2.0``, a first full rewrite has been done. pass-import was
a small python script that can natively import password to pass.

From ``v3.0``, pass-import became a real python program that can be used as it
or as a library to import passwords. It also supports more than pass as a
targeted password manager.


Added
~~~~~
- pass-import is now password manager agnostic, meaning it is not linked to
  password-store anymore. More destination password manager support will be
  added in future releases. In this release, it supports the following
  destination password manager:
    * ``keepass``
    * ``csv``
    * and also to ``pass``.

- For a given manager name, pass-import automatically detects the format of the
  file to import and uses the importer accordingly.
- pass-import can file encrypted by one of the supported algo before to import it.
- pass import is now available in three way:

   - As a ``pass`` extension ``pass import``
   - As an independant command line program: ``pimport``
   - As a python library ``pass_import``

- Added support for the following password managers:

    - Bitwarden (json)
    - Clipperz (html)
    - Dashlane (json)
    - Freeotp+ (json)
    - Padlock (csv)
    - Passman (csv and json)
    - Passpack (csv)
    - Saferpass (csv)
    - Zoho (csv)

- Added Debian packaging.
- Added pip packaging.

Changed
~~~~~~~
- The command line interface changed completly. See ``pass import -h``
- The old password manager name are not valid anymore
- Removed old bash tests
- Dropped support for python 3.4 & python 3.5
- Implement changing of CSV delimiter character `#88 <https://github.com/roddhjav/pass-import/pull/88>`__
- Handle field names of Revelation entry types other than Generic `#82 <https://github.com/roddhjav/pass-import/pull/82>`__
- Better entry name deduplication `#81 <https://github.com/roddhjav/pass-import/pull/81>`__

Fixed
~~~~~
- Fixed errored error message when missing optional dependencies `#97 <https://github.com/roddhjav/pass-import/issues/97>`__
- Use human dates for AppleKeychain `#85 <https://github.com/roddhjav/pass-import/pull/85>`__
- Handle missing pif web form field name
- Do not interpret password names as flags `#93 <https://github.com/roddhjav/pass-import/pull/93>`__


`2.6`_ - 2019-08-06
-------------------
Added
~~~~~
- Added support for generic OTP entry import
- Added support for binary attachements for manager that support it. `#63 <https://github.com/roddhjav/pass-import/issues/63>`__
- Added support for the 10 following password managers: `#84 <https://github.com/roddhjav/pass-import/pull/84>`__

  - passpie
  - keeper
  - keepass with kdbx file
  - Gnome Keyring
  - AndOTP for:

      - password encrypted backup,
      - plain text backup,
      - GPG encrypted backup.

  - Aegis for:

      - plain backup,
      - password encrypted backup.

  - Myki
  - Gnome Authenticator
  - Generic CSV
  - password-store (yes it can import itself ;))

- Added Importer docstring.
- Added full docstring.
- Added zsh completion.
- Added the following optional dependencies:

  - ``pykeepass``: Keepass import from KDBX file,
  - ``secretstorage``: Gnome Keyring import,
  - ``cryptography``: AndOTP & Aegis encrypted import.

Changed
~~~~~~~
- Changed the config file format from ``ini`` to ``yaml``.
- The config file now accept much more settings.
- The default Keepass, KeepassX2 and KkeepassXC importers now use Kdbx importer.
- Defusedxml is now an optional dependency only required for XML based import.
- Improve GPG key listing check.
- Dropped the support for reading data file from stdin due to issues with a
  lot of password managers.
- The README and the man page are now automatically updated with the data from
  the importer docstring.

Fixed
~~~~~
- Remove OS separaror from title `#64 <https://github.com/roddhjav/pass-import/issues/64>`__
- Add ``\t`` to the clean least `#65 <https://github.com/roddhjav/pass-import/issues/65>`__
- Fix some typos `#83 <https://github.com/roddhjav/pass-import/issues/83>`__


`2.5`_ - 2019-19-05
-------------------
Added
~~~~~
- Added a local install command with: ``make local``.
- Added support for Enpass 6: ``pass import enpass6`` `#73 <https://github.com/roddhjav/pass-import/pull/73>`__
- Added support for Buttercup: ``pass import buttercup`` `#74 <https://github.com/roddhjav/pass-import/pull/74>`__
- Added support for Apple Keychain: ``pass import applekeychain`` `#79 <https://github.com/roddhjav/pass-import/pull/79>`__
- Add support for Encryptr: ``pass import encryptr`` `#80 <https://github.com/roddhjav/pass-import/pull/80>`__

Changed
~~~~~~~
- Renamed the ``--extra``, ``-e`` option into ``--all``, ``-a``.
- Changed the way to collect password entries.
- Added missing unit tests to achieve 100% coverage.
- The importer tests have been simplified and are much more strict and do not allow partial import.

Fixed
~~~~~
- The extra/all option was not implemented for XML based importer. `#66 <https://github.com/roddhjav/pass-import/issues/66>`__
- Wrong python prefix for debian based distribution `#67 <https://github.com/roddhjav/pass-import/issues/67>`__
- Use the separator when cleaning data. `#78 <https://github.com/roddhjav/pass-import/issues/78>`__


`2.4`_ - 2018-12-02
-------------------
Added
~~~~~
- Added support for UPM (Universal Password Manager) with the command `upm`.
- Ensure the GPG recipients are in the keyring before to import. `#54 <https://github.com/roddhjav/pass-import/issues/54>`__
- Ensure the success messages print real data. `#54 <https://github.com/roddhjav/pass-import/issues/54>`__
- Added completion for bash.
- Add a ``--convert``, ``-C`` option to convert not allowed in path. `#55 <https://github.com/roddhjav/pass-import/issues/55>`__
- Add a ``--separator`` option to set a different character of replacement when converting not allowed characters. `#56 <https://github.com/roddhjav/pass-import/issues/56>`__
- Add a ``.import`` configuration file for import personalisation. `#56 <https://github.com/roddhjav/pass-import/issues/56>`__

Changed
~~~~~~~
- Changed the extension structure to a classic python program: `#53 <https://github.com/roddhjav/pass-import/issues/53>`__

  - The extension is now installed using setuptools for the python part,
  - Use `prospector` and `bandit` as python linter tool and security checker,
  - Add Gitlab CI,
  - Add SAST `security dashboard <https://gitlab.com/roddhjav/pass-import/security/dashboard>`__,
  - Simplify the tests.

- Changed the way to handle duplicated path.

  - Create sub-folder if the titles are identical. `#41 <https://github.com/roddhjav/pass-import/issues/41>`__ `#49 <https://github.com/roddhjav/pass-import/issues/49>`__
  - Use the new separator to duplicate paths. `#43 <https://github.com/roddhjav/pass-import/issues/43>`__

Fixed
~~~~~
- Stop assuming a title cannot be empty. `#57 <https://github.com/roddhjav/pass-import/issues/57>`__
- Import fix for the importers:

  1) `KeepassX`, `#48 <https://github.com/roddhjav/pass-import/pull/48>`__
  2) `Keepass`. `#52 <https://github.com/roddhjav/pass-import/pull/52>`__

Special thanks to `@christian-weiss <github.com/christian-weiss>`__ for all its
feedbacks.


`2.3`_ - 2018-07-19
-------------------
Added
~~~~~
- Add support for the following importers:

  - KeepassX 2 (``keepassx2``) `#45 <https://github.com/roddhjav/pass-import/issues/45>`__
  - Chrome with sqlite3 (``chromesqlite``) `#42 <https://github.com/roddhjav/pass-import/issues/42>`__
  - NetworkManager to import wifi passwords (``networkmanager``) `#39 <https://github.com/roddhjav/pass-import/pull/39>`__

- Add a nice error if defusedxml is not present `#24 <https://github.com/roddhjav/pass-import/issues/24>`__
- Add the few missing unit tests
- Add changelog

Changed
~~~~~~~
- Firefox: support FF-Password-Exporter instead of Password Exporter. `#40 <https://github.com/roddhjav/pass-import/issues/40>`__


`2.2`_ - 2018-03-18
-------------------
Added
~~~~~
- Add support for 1PIF file `#36 <https://github.com/roddhjav/pass-import/pull/36>`__.

Changed
~~~~~~~
- Important clean-up & code improvement `#34 <https://github.com/roddhjav/pass-import/pull/34>`__.
- Pwsafe: add support for:

  - Multiline notes `#29 <https://github.com/roddhjav/pass-import/pull/29>`__,
  - Password history `#30 <https://github.com/roddhjav/pass-import/pull/30>`__,
  - Email `#32 <https://github.com/roddhjav/pass-import/pull/32>`__.

- Do not remove protocol in url `#31 <https://github.com/roddhjav/pass-import/pull/31>`__.
- Update chrome CSV format for Chrome 66 `#26 <https://github.com/roddhjav/pass-import/pull/26>`__ & `#27 <https://github.com/roddhjav/pass-import/pull/27>`__.
- Update 1password format `#27 <https://github.com/roddhjav/pass-import/pull/27>`__ & `#28 <https://github.com/roddhjav/pass-import/pull/28>`__.

Fixed
~~~~~
- Fix typos & improve code coverage.


`2.1`_ - 2017-12-21
-------------------
Added
~~~~~
- Add support for bitwarden `#19 <https://github.com/roddhjav/pass-import/pull/19>`__.

Fixed
~~~~~
- Fix typos `#22 <https://github.com/roddhjav/pass-import/pull/22>`__
- Fix a lot of python linter errors.
- Improve installation documentation.


`2.0`_ - 2017-12-03
-------------------
Changed
~~~~~~~
``pass-import`` now natively supports import from other password manager and
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


`1.0`_ - 2017-12-01
-------------------
Fixed
~~~~~
- KDE wallet: unicode bugfix `#16 <https://github.com/roddhjav/pass-import/pull/16>`__.


`0.2`_ - 2017-09-15
-------------------
Added
~~~~~
- keepass2csv: add username and do not add empty lines `#13 <https://github.com/roddhjav/pass-import/pull/13>`__.
- Add Enpass `#9 <https://github.com/roddhjav/pass-import/pull/9>`__.
- Add Chrome importer `#3 <https://github.com/roddhjav/pass-import/pull/3>`__.

Fixed
~~~~~
- Lastpass: Ensure UTF-8 encoding `#5 <https://github.com/roddhjav/pass-import/pull/5>`__.


`0.1`_ - 2017-09-01
-------------------

- Initial release.

.. _3.0: https://github.com/roddhjav/pass-import/releases/tag/v3.0
.. _2.7: https://github.com/roddhjav/pass-import/releases/tag/v2.7
.. _2.6: https://github.com/roddhjav/pass-import/releases/tag/v2.6
.. _2.5: https://github.com/roddhjav/pass-import/releases/tag/v2.5
.. _2.4: https://github.com/roddhjav/pass-import/releases/tag/v2.4
.. _2.3: https://github.com/roddhjav/pass-import/releases/tag/v2.3
.. _2.2: https://github.com/roddhjav/pass-import/releases/tag/v2.2
.. _2.1: https://github.com/roddhjav/pass-import/releases/tag/v2.1
.. _2.0: https://github.com/roddhjav/pass-import/releases/tag/v2.0
.. _1.0: https://github.com/roddhjav/pass-import/releases/tag/v1.0
.. _0.2: https://github.com/roddhjav/pass-import/releases/tag/v0.2
.. _0.1: https://github.com/roddhjav/pass-import/releases/tag/v0.1

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
