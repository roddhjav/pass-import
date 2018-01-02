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
import sys
import csv
import shutil
import unittest
import importlib
from collections import OrderedDict


class TestPassSimple(unittest.TestCase):
    tmp = "/tmp/pass-import/python/"
    gpgid = "D4C78DB7920E1E27F5416B81CC9DB947CF90C77B"
    xml = ['fpm', 'keepassx', 'keepass', 'pwsafe', 'revelation', 'kedpm']
    db = "db/"

    @classmethod
    def setUpClass(self):
        # Getting pass-import module
        try:
            sys.path.append('../lib')
            self.passimport = importlib.import_module('import')
        except Exception as e:
            print("Unable to find import.py: %s", e)
            exit(1)

    def _get_refdata(self, keys):
        refdata = []
        reffile = os.path.join(self.db, '.template.csv')
        with open(reffile, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')
            for row in reader:
                entry = OrderedDict()
                for key in keys:
                    value = row[key]
                    if value is not None and not len(value) == 0:
                        entry[key] = value
                refdata.append(entry)
        return refdata

    @staticmethod
    def _clean(keys, data):
        """ Clean data from unwanted keys and weird formatting """
        for entry in data:
            delete = [k for k in entry.keys() if k not in keys]
            for key in delete:
                entry.pop(key, None)

            delete = []
            for key in entry:
                entry[key] = entry[key].replace('https://', '')
                entry[key] = entry[key].replace('http://', '')
                if entry[key] is None or len(entry[key]) == 0:
                    delete.append(key)
            for key in delete:
                entry.pop(key, None)

    def _get_testpath(self, manager):
        """ Get database file to test """
        ext = '.xml' if manager in self.xml else '.csv'
        return os.path.join(self.db, manager + ext)

    def _check_imported_data(self, data):
        """ Compare imported data with the reference data """
        keys = ['title', 'password', 'login']
        refdata = self._get_refdata(keys)
        self._clean(keys, refdata)
        self._clean(keys, data)
        for entry in data:
            self.assertIn(entry, refdata)


class TestPass(TestPassSimple):
    @classmethod
    def setUpClass(self):
        # Getting pass-import module
        super(TestPass, self).setUpClass()

        # Pass binary
        os.environ['PASSWORD_STORE_BIN'] = shutil.which("pass")

        # GPG Config
        if 'GPG_AGENT_INFO' in os.environ:
            os.environ.pop('GPG_AGENT_INFO', None)
        os.environ['GNUPGHOME'] = os.path.join(os.getcwd(), 'gnupg')

        # Tests directories
        self.tmp = os.path.join(self.tmp, self.__name__[8:].lower())
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.makedirs(self.tmp, exist_ok=True)

    def setUp(self):
        testname = self.id().split('_').pop() + '-store'
        os.environ['PASSWORD_STORE_DIR'] = os.path.join(self.tmp, testname)
        os.makedirs(os.environ['PASSWORD_STORE_DIR'], exist_ok=True)
        self.store = self.passimport.PasswordStore()

    def _passinit(self):
        with open(os.path.join(self.store.prefix, '.gpg-id'), 'w') as file:
            file.write("%s\n" % self.gpgid)
