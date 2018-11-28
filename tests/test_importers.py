#!/usr/bin/env python3
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017 Alexandre PUJOL <alexandre@pujol.io>.
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
import csv
from collections import OrderedDict

from .. import pass_import
from tests.commons import TestPassSimple


class TestBaseImporters(TestPassSimple):

    def _get_refdata(self, keys, path='.template.csv'):
        refdata = []
        reffile = os.path.join(self.db, path)
        with open(reffile, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')
            for row in reader:
                entry = OrderedDict()
                for key in keys:
                    entry[key] = row.get(key, None)
                refdata.append(entry)
        self._clean(keys, refdata)
        return refdata

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

    def _get_testpath(self, manager):
        """Get database file to test."""
        ext = '.xml' if manager in self.xml else '.csv'
        ext = '.1pif' if manager == '1password4pif' else ext
        encoding = 'utf-8-sig' if manager == '1password4pif' else 'utf-8'
        return (os.path.join(self.db, manager + ext), encoding)

    def _check_imported_data(self, keys, data, refdata):
        """Compare imported data with the reference data."""
        self._clean(keys, data)
        for entry in data:
            self.assertIn(entry, refdata)

    @staticmethod
    def _load_import(manager):
        """Load importer class."""
        ImporterClass = getattr(pass_import,
                                pass_import.importers[manager][0])
        importer = ImporterClass(extra=True)
        return importer


class TestImporters(TestBaseImporters):

    def test_importers(self):
        """Testing: importer parse method using real data."""
        keys = ['title', 'password', 'login', 'ssid']
        refdata = self._get_refdata(keys)
        ignore = ['networkmanager']
        for manager in pass_import.importers:
            if manager in ignore:
                continue
            with self.subTest(manager):
                importer = self._load_import(manager)
                testpath, encoding = self._get_testpath(manager)
                with open(testpath, 'r', encoding=encoding) as file:
                    importer.parse(file)

                self._check_imported_data(keys, importer.data, refdata)

    def test_importers_networkmanager(self):
        """Testing: importer parse method from Network Manager settings."""
        keys = ['title', 'password']
        testpath = os.path.join(self.db, 'networkmanager')
        refdata = self._get_refdata(keys, '.template-wifi.csv')
        importer = self._load_import('networkmanager')
        importer.parse(testpath)
        self._check_imported_data(keys, importer.data, refdata)

    def test_importers_format(self):
        """Testing: importer file format."""
        formaterror = (pass_import.FormatError, AttributeError, ValueError)
        ignore = ['dashlane', 'networkmanager', 'upm']
        for manager in pass_import.importers:
            if manager in ignore:
                continue
            with self.subTest(manager):
                importer = self._load_import(manager)
                ext = '.xml' if manager in self.xml else '.csv'
                testpath = os.path.join(self.db, '.dummy' + ext)

                with self.assertRaises(formaterror):
                    with open(testpath, 'r', encoding='utf-8') as file:
                        importer.parse(file)
