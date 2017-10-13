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
import shutil
import unittest
try:
    sys.path.append('../lib')
    passimport = __import__('import')
except Exception as e:
    print("Unable to find import.py: %s", e)
    exit(1)

TMP = "/tmp/pass-import/python/pass"

class TestPassStore(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if 'GPG_AGENT_INFO' in os.environ:
            os.environ.pop('GPG_AGENT_INFO', None)
        os.environ['PASSWORD_STORE_BIN'] = '/usr/bin/pass'
        os.environ['GNUPGHOME'] = os.path.join(os.path.expanduser('~'), '.gnupg')
        shutil.rmtree(TMP, ignore_errors=True)
        os.makedirs(TMP, exist_ok=True)

    def setUp(self):
        testname = self.id().split('_').pop()
        os.environ['PASSWORD_STORE_DIR'] = os.path.join(TMP, testname + '-store')
        os.makedirs(os.environ['PASSWORD_STORE_DIR'])
        self.store = passimport.PasswordStore()

    def _pass_init(self):
        with open(os.path.join(self.store.prefix, '.gpg-id'), 'w') as file:
            file.write("%s\n" % KEY1)

    def test_environnement_no_prefix(self):
        """ Testing: no prefix & binary """
        os.environ.pop('PASSWORD_STORE_DIR', None)
        os.environ.pop('PASSWORD_STORE_BIN', None)
        with self.assertRaises(passimport.PasswordStoreError):
            passimport.PasswordStore()
        os.environ['PASSWORD_STORE_BIN'] = '/usr/bin/pass'

    def test_environnement_variables(self):
        """ Testing: environnement variables """
        self.assertEqual(self.store.env['PASSWORD_STORE_DIR'], os.environ['PASSWORD_STORE_DIR'])
        self.assertEqual(self.store.env['PASSWORD_STORE_BIN'], os.environ['PASSWORD_STORE_BIN'])
        self.assertEqual(self.store.env['GNUPGHOME'], os.environ['GNUPGHOME'])

    def test_exist(self):
        """ Testing: store not initialized """
        self.assertFalse(self.store.exist())
        with self.assertRaises(passimport.PasswordStoreError):
            self.store.insert("Test/test", "dummy")
        self._pass_init()
        self.assertTrue(self.store.exist())

    def test_insert(self):
        """ Testing: pass insert """
        self._pass_init()
        path = "Test/test"
        entry = "EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\ncomments: This is a comment\n"
        self.store.insert(path, entry)
        self.assertEqual(self.store._pass(['show', path]), entry)

    def test_insert_force(self):
        """ Testing: pass insert --force """
        self.test_insert()
        path = "Test/test"
        entry2 = "EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\ncomments: This is a second comment\n"
        with self.assertRaises(passimport.PasswordStoreError):
            self.store.insert(path, entry2, force=False)
        self.store.insert(path, entry2, force=True)
        self.assertEqual(self.store._pass(['show', path]), entry2)


if __name__ == '__main__':
    unittest.main()
