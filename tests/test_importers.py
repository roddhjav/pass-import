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
import copy
import yaml

from .. import pass_import
from tests.commons import TestBase


REFERENCE = yaml.safe_load(open('tests/references/main.yml', 'r'))
REFERENCE_WIFI = yaml.safe_load(open('tests/references/networkmanager-wifi.yml', 'r'))
REFERENCE_NOTE = yaml.safe_load(open('tests/references/applekeychain-note.yml', 'r'))
REFERENCE_CARD = yaml.safe_load(open('tests/references/encryptr-card.yml', 'r'))
REFERENCE_OTHER = yaml.safe_load(open('tests/references/keepass-other.yml', 'r'))


class TestBaseImporters(TestBase):
    importers = yaml.safe_load(open('tests/importers.yml', 'r'))

    @staticmethod
    def _clear(data, keep=None):
        """Only keep the keys present in the template and reference file."""
        if not keep:
            keep = ['title', 'password', 'login', 'url', 'comments', 'group']
        for entry in data:
            delete = [k for k in entry.keys() if k not in keep]
            empty = [k for k, v in entry.items() if not v]
            delete.extend(empty)
            for key in delete:
                entry.pop(key, None)

    @staticmethod
    def _class(manager):
        """Load importer class."""
        ImporterClass = getattr(pass_import,
                                pass_import.importers[manager][0])
        importer = ImporterClass(all=True)
        return importer

    def _path(self, manager):
        """Get database file to test."""
        ext = self.importers[manager]['extension']
        return os.path.join(self.db, "%s.%s" % (manager, ext))

    def _reference(self, manager):
        """Set the expected reference data for a given manager.
        Some password manager do not store a lot off data (no group...).
        Therefore, we need to remove these entries from the reference data when
        testing these managers.
        """
        reference = copy.deepcopy(REFERENCE)
        if 'without' in self.importers[manager]:
            for key in self.importers[manager]['without']:
                for entry in reference:
                    entry.pop(key, None)
        elif 'root' in self.importers[manager]:
            for entry in reference:
                entry['group'] = self.importers[manager]['root'] + entry['group']
        return reference

    def assertImport(self, data, refdata, keep=None):
        """Compare imported data with the reference data."""
        self._clear(data, keep)
        for entry in data:
            self.assertIn(entry, refdata)


class TestImporters(TestBaseImporters):

    def test_importers_generic(self):
        """Testing: parse method for all importers."""
        for manager in self.importers:
            with self.subTest(manager):
                importer = self._class(manager)
                testpath = self._path(manager)
                reference = self._reference(manager)
                encoding = self.importers[manager]['encoding']
                with open(testpath, 'r', encoding=encoding) as file:
                    importer.parse(file)

                self.assertImport(importer.data, reference)

    def test_importers_networkmanager(self):
        """Testing: parse method for Network Manager."""
        importer = self._class('networkmanager')
        testpath = os.path.join(self.db, 'networkmanager')
        importer.parse(testpath)
        self.assertImport(importer.data, REFERENCE_WIFI)

    def test_importers_applekeychain_note(self):
        """Testing: parse method for AppleKeychain with notes."""
        importer = self._class('apple-keychain')
        testpath = os.path.join(self.db, 'apple-keychain-note.txt')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_NOTE)

    def test_importers_keepassother(self):
        """Testing: parse method for Keepass with special cases."""
        importer = self._class('keepass')
        testpath = os.path.join(self.db, 'keepass-other.xml')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_OTHER)

    def test_importers_keepassxother(self):
        """Testing: parse method for KeepassX with special cases."""
        importer = self._class('keepassx')
        testpath = os.path.join(self.db, 'keepassx-other.xml')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_OTHER)

    def test_importers_encryptr(self):
        """Testing: parse method for Encryptr with credit card."""
        keep = ['title', 'Type', 'Name on card', 'Card Number', 'CVV',
                'Expiry', 'group']
        importer = self._class('encryptr')
        testpath = os.path.join(self.db, 'encryptr-card.csv')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_CARD, keep)


class TestImportersFormat(TestBaseImporters):
    formaterror = (pass_import.FormatError, AttributeError, ValueError,
                   yaml.scanner.ScannerError)

    def test_importers_format(self):
        """Testing: file format for all importers."""
        ignore = ['dashlane', 'upm']
        for manager in self.importers:
            if manager in ignore:
                continue
            with self.subTest(manager):
                importer = self._class(manager)
                ext = self.importers[manager]['extension']
                testpath = os.path.join(self.format, 'dummy.' + ext)

                with self.assertRaises(self.formaterror):
                    with open(testpath, 'r', encoding='utf-8') as file:
                        importer.parse(file)
