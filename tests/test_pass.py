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

import pass_import
from tests.commons import TestPass


class TestPassStore(TestPass):

    def test_environment_no_prefix(self):
        """Testing: no prefix."""
        os.environ.pop('PASSWORD_STORE_DIR', None)
        with self.assertRaises(pass_import.PasswordStoreError):
            pass_import.PasswordStore()

    def test_environment_variables(self):
        """Testing: environment variables."""
        self.assertEqual(self.store.env['PASSWORD_STORE_DIR'], os.environ['PASSWORD_STORE_DIR'])
        self.assertEqual(self.store.env['GNUPGHOME'], os.environ['GNUPGHOME'])

    def test_exist(self):
        """Testing: store not initialized."""
        self.assertFalse(self.store.exist())
        with self.assertRaises(pass_import.PasswordStoreError):
            self.store.insert("Test/test", "dummy")
        self._passinit()
        self.assertTrue(self.store.exist())

    def test_insert(self):
        """Testing: pass insert."""
        self._passinit()
        path = "Test/test"
        entry = "EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\ncomments: This is a comment\n"
        self.store.insert(path, entry)
        self.assertEqual(self.store._pass(['show', path]), entry)

    def test_insert_force(self):
        """Testing: pass insert --force."""
        self.test_insert()
        path = "Test/test"
        entry2 = "EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\ncomments: This is a second comment\n"
        with self.assertRaises(pass_import.PasswordStoreError):
            self.store.insert(path, entry2, force=False)
        self.store.insert(path, entry2, force=True)
        self.assertEqual(self.store._pass(['show', path]), entry2)

    def test_validRecipients(self):
        """Testing: valid recipients."""
        self.gpgids = ['D4C78DB7920E1E27F5416B81CC9DB947CF90C77B',
                       '70BD448330ACF0653645B8F2B4DDBFF0D774A374',
                       '62EBE74BE834C2EC71E6414595C4B715EB7D54A8', '']
        self._passinit()
        self.assertTrue(self.store.is_valid_recipients())

    def test_invalidRecipients(self):
        """Testing: invalid recipients."""
        self.gpgids = ['D4C78DB7920E1E27F5416B81CC9DB947CF90C77B',
                       'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
                       '62EBE74BE834C2EC71E6414595C4B715EB7D54A8', '']
        self._passinit()
        self.assertFalse(self.store.is_valid_recipients())

    def test_emptyRecipients(self):
        """Testing: empty recipients."""
        self.gpgids = ['']
        self._passinit()
        self.assertFalse(self.store.is_valid_recipients())


class TestPassStoreList(TestPass):

    @classmethod
    def setUp(self):
        os.environ['PASSWORD_STORE_DIR'] = os.path.join(os.getcwd(), 'tests/pass-store')
        self.store = pass_import.PasswordStore()

    def test_listPath(self):
        """Testing: pass list exact path."""
        path = 'Social/mastodon.social'
        ref = ['Social/mastodon.social']
        self.assertEqual(self.store.list(path), ref)

    def test_list(self):
        """Testing: pass list."""
        ref = ['Bank/aib', 'CornerCases/empty entry',
               'CornerCases/empty password', 'CornerCases/note',
               'CornerCases/space title', 'Emails/WS/dpbx@fner.ws',
               'Emails/WS/dpbx@mnyfymt.ws', 'Emails/dpbx@afoqwdr.tx',
               'Emails/dpbx@klivak.xb', 'Servers/ovh.com', 'Servers/ovh.com0',
               'Social/mastodon.social', 'Social/news.ycombinator.com',
               'Social/twitter.com', 'tombpass']
        self.assertEqual(self.store.list(), ref)

    def test_listRoot(self):
        """Testing: pass list path."""
        ref = ['Emails/WS/dpbx@fner.ws', 'Emails/WS/dpbx@mnyfymt.ws',
               'Emails/dpbx@afoqwdr.tx', 'Emails/dpbx@klivak.xb']
        self.assertEqual(self.store.list('Emails'), ref)
        ref = ['Emails/WS/dpbx@fner.ws', 'Emails/WS/dpbx@mnyfymt.ws']
        self.assertEqual(self.store.list('Emails/WS'), ref)
