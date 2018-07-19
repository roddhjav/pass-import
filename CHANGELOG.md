# Changes By Release

All the releases are signed using the GPG key
[`06A26D531D56C42D66805049C5469996F0DF68EC`](https://pujol.io/keys/). You should
check the key's fingerprint and verify the signature:

##### Donwload and verify the release
```sh
VERSION='<version>'
wget https://github.com/roddhjav/pass-import/releases/download/v$VERSION/pass-import-$VERSION.tar.gz.asc
wget https://github.com/roddhjav/pass-import/releases/download/v$VERSION/pass-import-$VERSION.tar.gz
gpg --recv-keys 06A26D531D56C42D66805049C5469996F0DF68EC
gpg --verify pass-import-$VERSION.tar.gz.asc
```

##### Install `pass-import`
```sh
tar xzf pass-import-$VERSION.tar.gz
cd pass-import-$VERSION
sudo make install  # For OSX: make install PREFIX=/usr/local
```

## 2.3 - 2018-07-19

* Add support for the following importers:
  - KeepassX 2 (`keepassx2`) [#45](https://github.com/roddhjav/pass-import/issues/45)
  - Chrome with sqlite3 (`chromesqlite`) [#42](https://github.com/roddhjav/pass-import/issues/42)
  - NetworkManager to import wifi passwords (`networkmanager`) [#39](https://github.com/roddhjav/pass-import/pull/39)
* Firefox: support FF-Password-Exporter instead of Password Exporter. [#40](https://github.com/roddhjav/pass-import/issues/40)
* Add a nice error if defusedxml is not present [#24](https://github.com/roddhjav/pass-import/issues/24)
* Add the few missing unit tests
* Add changelog

## 2.2 - 2018-03-18

* Add support for 1PIF file [#36](https://github.com/roddhjav/pass-import/pull/36).
* Important clean-up & code improvement [#34](https://github.com/roddhjav/pass-import/pull/34).
* Pwsafe: add support for:
  - Multiline notes [#29](https://github.com/roddhjav/pass-import/pull/29),
  - Password history [#30](https://github.com/roddhjav/pass-import/pull/30),
  - Email [#32](https://github.com/roddhjav/pass-import/pull/32).
* Do not remove protocol in url [#31](https://github.com/roddhjav/pass-import/pull/31).
* Update chrome CSV format for Chrome 66 [#26](https://github.com/roddhjav/pass-import/pull/26) & [#27](https://github.com/roddhjav/pass-import/pull/27).
* Update 1password format [#27](https://github.com/roddhjav/pass-import/pull/27) & [#28](https://github.com/roddhjav/pass-import/pull/28).
* Fix typos & improve code coverage.

## 2.1 - 2017-12-21

* Fix typos [#22](https://github.com/roddhjav/pass-import/pull/22)
* Add support for bitwarden [#19](https://github.com/roddhjav/pass-import/pull/19).
* Fix a lot of python linter errors.
* Improve installation documentation.

## 2.0 - 2017-12-03

##### Major version
`pass-import` now natively supports import from other password manager and
therefore, it does not require the importer scripts any-more. Moreover, all the
importer's systems have been intensely tested against a test database.

##### pass-import now supports the following 17 password managers:
* 1password6
* 1password4
* chrome
* dashlane
* enpass
* fpm
* gorilla
* kedpm
* keepass
* keepasscsv
* keepassx
* keepassxc
* lastpass
* passwordexporter
* pwsafe
* revelation
* roboform

## 1.0 - 2017-12-01

* KDE wallet: unicode bugfix [#16](https://github.com/roddhjav/pass-import/pull/16).

## 0.2 - 2017-09-15

* keepass2csv: add username and do not add empty lines [#13](https://github.com/roddhjav/pass-import/pull/13).
* Add Enpass [#9](https://github.com/roddhjav/pass-import/pull/9).
* Lastpass: Ensure UTF-8 encoding [#5](https://github.com/roddhjav/pass-import/pull/5).
* Add Chrome importer [#3](https://github.com/roddhjav/pass-import/pull/3).

## 0.1 - 2017-09-01

* Initial release.
