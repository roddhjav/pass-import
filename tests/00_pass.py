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
import setup
import shutil
import unittest


class TestPassStore(setup.TestPass):

    def test_environnement_no_prefix(self):
        """ Testing: no prefix & binary """
        os.environ.pop('PASSWORD_STORE_DIR', None)
        os.environ.pop('PASSWORD_STORE_BIN', None)
        with self.assertRaises(self.passimport.PasswordStoreError):
            self.passimport.PasswordStore()
        os.environ['PASSWORD_STORE_BIN'] = shutil.which("pass")

    def test_environnement_variables(self):
        """ Testing: environnement variables """
        self.assertEqual(self.store.env['PASSWORD_STORE_DIR'], os.environ['PASSWORD_STORE_DIR'])
        self.assertEqual(self.store.env['PASSWORD_STORE_BIN'], os.environ['PASSWORD_STORE_BIN'])
        self.assertEqual(self.store.env['GNUPGHOME'], os.environ['GNUPGHOME'])

    def test_exist(self):
        """ Testing: store not initialized """
        self.assertFalse(self.store.exist())
        with self.assertRaises(self.passimport.PasswordStoreError):
            self.store.insert("Test/test", "dummy")
        self._passinit()
        self.assertTrue(self.store.exist())

    def test_insert(self):
        """ Testing: pass insert """
        self._passinit()
        path = "Test/test"
        entry = "EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\ncomments: This is a comment\n"
        self.store.insert(path, entry)
        self.assertEqual(self.store._pass(['show', path]), entry)

    def test_insert_force(self):
        """ Testing: pass insert --force """
        self.test_insert()
        path = "Test/test"
        entry2 = "EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\ncomments: This is a second comment\n"
        with self.assertRaises(self.passimport.PasswordStoreError):
            self.store.insert(path, entry2, force=False)
        self.store.insert(path, entry2, force=True)
        self.assertEqual(self.store._pass(['show', path]), entry2)


if __name__ == '__main__':
    unittest.main()
