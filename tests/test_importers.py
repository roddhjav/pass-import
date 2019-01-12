#!/usr/bin/env python3
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017-2019 Alexandre PUJOL <alexandre@pujol.io>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
from collections import OrderedDict as Odict

from .. import pass_import
from tests.commons import TestBase


REF = [Odict([('title', 'mastodon.social'),
              ('password', "D<INNeT?#?Bf4%`zA/4i!/'$T"),
              ('login', 'ostqxi')]),
       Odict([('title', 'twitter.com'),
              ('password', 'SoNEwvU,kJ%-cIKJ9[c#S;]jB'),
              ('login', 'ostqxi')]),
       Odict([('title', 'news.ycombinator.com'),
              ('password', "1)Btf2EI~Tfb7g2A!Sy',*Sj#"),
              ('login', 'ostqxi')]),
       Odict([('title', 'ovh.com'),
              ('password', '^Vr/|o>_H8X%T]7>f}7|:U!Zs'),
              ('login', 'jsdkyvbwjn')]),
       Odict([('title', 'ovh.com'),
              ('password', "3Z-VW!i,j(&!zRGPu(hFe]s'("),
              ('login', 'bynbyjhqjz')]),
       Odict([('title', 'aib'),
              ('password',
               "ws5T@;_UB[Q|P!8'`~z%XC'JHFUbf#IX _E0}:HF,[{ei0hBg14"),
              ('login', 'dpbx@fner.ws')]),
       Odict([('title', 'dpbx@afoqwdr.tx'),
              ('password', '9KVHnx:.S_S;cF`=CE@e\\p{v6'),
              ('login', 'dpbx')]),
       Odict([('title', 'dpbx@klivak.xb'),
              ('password', '2cUqe}e9}>IVZf)Ye>3C8ZN,r'),
              ('login', 'dpbx')]),
       Odict([('title', 'dpbx@mnyfymt.ws'),
              ('password', 'rPCkmNkhIa>{izt3C3F823!Go'),
              ('login', 'dpbx')]),
       Odict([('title', 'dpbx@fner.ws'),
              ('password', "mt}h'hSUCY;SU;;A!l[8y3O:8"),
              ('login', 'dpbx')]),
       Odict([('title', 'space title'),
              ('password', ']stDKo{%pk'),
              ('login', 'vkeelpbu')]),
       Odict([('title', 'empty entry')]),
       Odict([('title', 'empty password'),
              ('login', 'vkeelpbu')]),
       Odict([('title', 'note')])]

REF_WIFI = [Odict([('title', 'android'),
                   ('password', 'dMa+GoMjGz')]),
            Odict([('title', 'Box-A5O9'),
                   ('password', '07B1DB8DBCB541C48202487760D0E1D6')]),
            Odict([('title', 'eduroam'),
                   ('password', 'X3<yS1g9wW-@lC87pekRmXMJp')])]


class TestBaseImporters(TestBase):

    @staticmethod
    def _clean(keys, data):
        """Clean data from unwanted keys and weird formatting."""
        for entry in data:
            delete = [k for k in entry.keys() if k not in keys]
            empty = [k for k, v in entry.items() if not v]
            delete.extend(empty)
            for key in delete:
                entry.pop(key, None)

            delete = []
            for key in entry:
                entry[key] = entry[key].replace('https://', '')
                entry[key] = entry[key].replace('http://', '')
                if not entry[key]:
                    delete.append(key)
            for key in delete:
                entry.pop(key, None)

    def _path(self, manager):
        """Get database file to test."""
        ext = '.xml' if manager in self.xml else '.csv'
        ext = '.1pif' if manager == '1password4pif' else ext
        ext = '.json' if manager == 'enpass6' else ext
        encoding = 'utf-8-sig' if manager == '1password4pif' else 'utf-8'
        return (os.path.join(self.db, manager + ext), encoding)

    def assertImport(self, keys, data, refdata):
        """Compare imported data with the reference data."""
        self._clean(keys, data)
        for entry in data:
            self.assertIn(entry, refdata)

    @staticmethod
    def _class(manager):
        """Load importer class."""
        ImporterClass = getattr(pass_import,
                                pass_import.importers[manager][0])
        importer = ImporterClass(extra=True)
        return importer


class TestImporters(TestBaseImporters):

    def test_importers(self):
        """Testing: importer parse method using real data."""
        keys = ['title', 'password', 'login', 'ssid']
        ignore = ['networkmanager']
        for manager in pass_import.importers:
            if manager in ignore:
                continue
            with self.subTest(manager):
                importer = self._class(manager)
                testpath, encoding = self._path(manager)
                with open(testpath, 'r', encoding=encoding) as file:
                    importer.parse(file)

                self.assertImport(keys, importer.data, REF)

    def test_importers_networkmanager(self):
        """Testing: importer parse method from Network Manager settings."""
        keys = ['title', 'password']
        testpath = os.path.join(self.db, 'networkmanager')
        importer = self._class('networkmanager')
        importer.parse(testpath)
        self.assertImport(keys, importer.data, REF_WIFI)

    def test_importers_format(self):
        """Testing: importer file format."""
        formaterror = (pass_import.FormatError, AttributeError, ValueError)
        ignore = ['dashlane', 'networkmanager', 'upm', 'enpass6']
        for manager in pass_import.importers:
            if manager in ignore:
                continue
            with self.subTest(manager):
                importer = self._class(manager)
                ext = '.xml' if manager in self.xml else '.csv'
                testpath = os.path.join(self.db, '.dummy' + ext)

                with self.assertRaises(formaterror):
                    with open(testpath, 'r', encoding='utf-8') as file:
                        importer.parse(file)
