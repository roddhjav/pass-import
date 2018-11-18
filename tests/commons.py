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
import shutil
import unittest
from collections import OrderedDict
import pass_import


class TestPassSimple(unittest.TestCase):
    tmp = "/tmp/pass-import/python/"
    gpgid = "D4C78DB7920E1E27F5416B81CC9DB947CF90C77B"
    xml = ['fpm', 'keepassx', 'keepass', 'pwsafe', 'revelation', 'kedpm']
    db = "tests/db/"

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


class TestPass(TestPassSimple):
    @classmethod
    def setUpClass(cls):
        # GPG Config
        if 'GPG_AGENT_INFO' in os.environ:
            os.environ.pop('GPG_AGENT_INFO', None)
        os.environ['GNUPGHOME'] = os.path.join(os.getcwd(), 'tests/gnupg')

        # Tests directories
        cls.tmp = os.path.join(cls.tmp, cls.__name__[8:].lower())
        shutil.rmtree(cls.tmp, ignore_errors=True)
        os.makedirs(cls.tmp, exist_ok=True)

    def setUp(self):
        testname = self.id().split('_').pop() + '-store'
        os.environ['PASSWORD_STORE_DIR'] = os.path.join(self.tmp, testname)
        os.makedirs(os.environ['PASSWORD_STORE_DIR'], exist_ok=True)
        self.store = pass_import.PasswordStore()

    def _passinit(self):
        with open(os.path.join(self.store.prefix, '.gpg-id'), 'w') as file:
            file.write("%s\n" % self.gpgid)
