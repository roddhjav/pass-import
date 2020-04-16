# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.errors import PMError
from pass_import.managers.passwordstore import PasswordStore
import tests


class TestPass(tests.Test):
    """Base class for password store tests."""

    def setUp(self):
        """Create a directory for a new password store repository."""
        self._tmpdir()
        os.environ['PASSWORD_STORE_DIR'] = self.prefix
        self.store = PasswordStore(self.prefix)
        self.store.all = True


class TestExportPassGeneral(TestPass):
    """Test pass general features."""

    def test_pass_environment_no_prefix(self):
        """Testing: no prefix."""
        os.environ.pop('PASSWORD_STORE_DIR', None)
        with self.assertRaises(PMError):
            PasswordStore()

    def test_pass_environment_variables(self):
        """Testing: environment variables."""
        self.assertEqual(self.store.env['PASSWORD_STORE_DIR'],
                         os.environ['PASSWORD_STORE_DIR'])
        self.assertEqual(self.store.env['GNUPGHOME'], os.environ['GNUPGHOME'])

    def test_pass_prefix(self):
        """Testing: prefix get/set."""
        prefix = tests.assets + 'pass-store'
        store = PasswordStore(prefix)
        self.assertEqual(prefix, store.prefix)
        store.prefix = self.store.prefix
        self.assertEqual(store.env['PASSWORD_STORE_DIR'], self.store.prefix)

    def test_pass_exist(self):
        """Testing: store not initialized."""
        self.assertFalse(self.store.exist())
        entry = {'path': 'Test/test', 'password': 'dummy'}
        with self.assertRaises(PMError):
            self.store.insert(entry)
        self._init_pass()
        self.assertTrue(self.store.exist())

    def test_pass_valid_credentials(self):
        """Testing: valid credentials."""
        self.gpgids = ['D4C78DB7920E1E27F5416B81CC9DB947CF90C77B',
                       '70BD448330ACF0653645B8F2B4DDBFF0D774A374',
                       '62EBE74BE834C2EC71E6414595C4B715EB7D54A8', '']
        self._init_pass()
        self.assertTrue(self.store.isvalid())

    def test_pass_invalid_credentials(self):
        """Testing: invalid credentials."""
        self.gpgids = ['D4C78DB7920E1E27F5416B81CC9DB947CF90C77B',
                       'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
                       '62EBE74BE834C2EC71E6414595C4B715EB7D54A8', '']
        self._init_pass()
        self.assertFalse(self.store.isvalid())

    def test_pass_empty_credentials(self):
        """Testing: empty credentials."""
        self.gpgids = ['']
        self._init_pass()
        self.assertFalse(self.store.isvalid())


class TestExportPassInsert(TestPass):
    """Test pass insert features."""

    def test_pass_insert(self):
        """Testing: pass insert."""
        self._init_pass()
        entry = {'password': 'UuQHzvv6IHRIJGjwKru7',
                 'login': 'lnqYm3ZWtm',
                 'url': 'https://twitter.com',
                 'website': 'https://pujol.io',
                 'uuid': '44jle5q3fdvrprmaahozexy2pi',
                 'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PX'
                            'P&issuer=alice@google.com&algorithm=SHA1&digits=6'
                            '&period=30',
                 'path': 'Test/test'}
        ref = ("UuQHzvv6IHRIJGjwKru7\nlogin: lnqYm3ZWtm\n"
               "url: https://twitter.com\notpauth://totp/totp-secret?secret=JB"
               "SWY3DPEHPK3PXP&issuer=alice@google.com&algorithm=SHA1&digits=6"
               "&period=30\nwebsite: https://pujol.io\n"
               "uuid: 44jle5q3fdvrprmaahozexy2pi\n")
        self.store.insert(entry)
        self.assertEqual(self.store._command(['show', 'Test/test']), ref)

    def test_pass_insert_empty(self):
        """Testing: pass insert empty."""
        self._init_pass()
        entry = {'path': 'test'}
        entry_expected = '\n'
        self.store.insert(entry)
        self.assertEqual(self.store._command(['show', 'test']), entry_expected)

    def test_pass_insert_force(self):
        """Testing: pass insert --force."""
        self.test_pass_insert()
        entry2 = {'path': 'Test/test', 'password': 'EaP:bCmLZliqa|]WR/#HZP-aa',
                  'login': 'roddhjav', 'comments': 'This is a second comment'}
        ref = ("EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\n"
               "comments: This is a second comment\n")
        with self.assertRaises(PMError):
            self.store.insert(entry2)
        self.store.force = True
        self.store.insert(entry2)
        self.assertEqual(self.store._command(['show', 'Test/test']), ref)


class TestExportPassShow(TestPass):
    """Test pass list/show features."""

    def setUp(self):
        """Use the password repository in tests/assets/pass-store."""
        self.prefix = tests.assets + 'pass-store'
        os.environ['PASSWORD_STORE_DIR'] = self.prefix
        self.store = PasswordStore(self.prefix)

    def test_pass_list_path(self):
        """Testing: pass list exact path."""
        path = 'Social/mastodon.social'
        ref = ['Social/mastodon.social']
        self.assertEqual(self.store.list(path), ref)

    def test_pass_list(self):
        """Testing: pass list."""
        ref = ['Bank/aib', 'CornerCases/empty entry',
               'CornerCases/empty password', 'CornerCases/note',
               'CornerCases/space title', 'Emails/WS/dpbx@fner.ws',
               'Emails/WS/dpbx@mnyfymt.ws', 'Emails/dpbx@afoqwdr.tx',
               'Emails/dpbx@klivak.xb', 'Servers/ovh.com', 'Servers/ovh.com0',
               'Social/mastodon.social', 'Social/news.ycombinator.com',
               'Social/twitter.com', 'tombpass']
        self.assertEqual(self.store.list(), ref)

    def test_pass_list_root(self):
        """Testing: pass list path/."""
        ref = ['Emails/WS/dpbx@fner.ws', 'Emails/WS/dpbx@mnyfymt.ws',
               'Emails/dpbx@afoqwdr.tx', 'Emails/dpbx@klivak.xb']
        self.assertEqual(self.store.list('Emails'), ref)
        ref = ['Emails/WS/dpbx@fner.ws', 'Emails/WS/dpbx@mnyfymt.ws']
        self.assertEqual(self.store.list('Emails/WS'), ref)

    def test_pass_show(self):
        """Testing: pass show Social/mastodon.social."""
        path = "Social/mastodon.social"
        entry = {'group': 'Social',
                 'login': 'ostqxi',
                 'otpauth': ('otpauth://totp/mastodon.social:ostqxi?secret='
                             'JBSWY3DPEHPK3PXP'),
                 'password': "D<INNeT?#?Bf4%`zA/4i!/'$T",
                 'title': 'mastodon.social',
                 'url': 'mastodon.social/'}
        self.assertEqual(self.store.show(path), entry)

    def test_pass_show_emptypassword(self):
        """Testing: pass show 'CornerCases/empty password'."""
        path = "CornerCases/empty password"
        entry = {'group': 'CornerCases',
                 'login': 'vkeelpbu',
                 'title': 'empty password',
                 'url': 'nhysdo.wg'}
        self.assertEqual(self.store.show(path), entry)

    def test_pass_show_notes(self):
        """Testing: pass show 'CornerCases/empty password'."""
        path = "CornerCases/note"
        entry = {'group': 'CornerCases',
                 'title': 'note',
                 'comments': ('This is a multiline note entry. Cube shank petr'
                              'oleum guacamole dart mower\nacutely slashing up'
                              'per cringing lunchbox tapioca wrongful unbeaten'
                              ' sift.')}

        self.assertEqual(self.store.show(path), entry)


class TestExportPassBinary(TestPass):
    """Test pass with binary files."""

    def test_pass_binary(self):
        """Testing: pass insert & show binary file."""
        self._init_pass()
        with open(os.path.join(tests.assets, 'pass.png'), 'rb') as file:
            data = file.read()
        entry = {'data': data, 'path': 'pass.png'}
        self.store.insert(entry)

        entry2 = self.store.show('pass.png')
        self.assertEqual(entry['data'], entry2['data'])
