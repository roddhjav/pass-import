# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import copy
from unittest.mock import patch

from pass_import.managers.keepass import Keepass
import tests


class TestExportKeepass(tests.Test):
    """Test keepass general features."""

    def setUp(self):
        """Setup a new keepass repository."""
        self._tmpdir('keepass.kdbx')
        self.keepass = Keepass(self.prefix)
        self.keepass.all = True

    def test_keepass_exist(self):
        """Testing: exist."""
        self._init_keepass()
        self.assertTrue(self.keepass.exist())
        self.keepass.prefix = ''
        self.assertFalse(self.keepass.exist())

    def test_keepass_isvalid(self):
        """Testing: isvalid."""
        self.assertTrue(self.keepass.isvalid())


class TestExportKeepassInsert(tests.Test):
    """Test keepass insert features."""
    keep = {
        'password', 'login', 'url', 'website', 'uuid', 'otpauth', 'path',
        'comments'
    }

    def setUp(self):
        self._tmpdir('keepass.kdbx')

    @patch("getpass.getpass")
    def test_keepass_insert(self, pw):
        """Testing: keepass insert."""
        pw.return_value = self.masterpassword
        self._init_keepass()
        entry = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }
        ref = copy.deepcopy(entry)

        with Keepass(self.prefix) as keepass:
            keepass.insert(entry)
            keepass.parse()
            data = keepass.data[0]
            data['path'] = os.path.join(data['group'], data['title'])
            self.assertImport([data], [ref], self.keep)

    @patch("getpass.getpass")
    def test_keepass_insert_empty(self, pw):
        """Testing: keepass insert empty."""
        pw.return_value = self.masterpassword
        self._init_keepass()
        entry = {'path': 'test'}
        ref = copy.deepcopy(entry)

        with Keepass(self.prefix) as keepass:
            keepass.insert(entry)
            keepass.parse()
            data = keepass.data[0]
            data['path'] = os.path.join(data.pop('group', ''),
                                        data.pop('title', ''))
            self.assertImport([data], [ref], self.keep)

    @patch("getpass.getpass")
    def test_keepass_binary(self, pw):
        """Testing: keepass insert & show binary file."""
        pw.return_value = self.masterpassword
        self._init_keepass()
        with open(os.path.join(tests.assets, 'pass.png'), 'rb') as file:
            data = file.read()
        entry = {'data': data, 'path': 'pass.png'}
        ref = copy.deepcopy(entry)

        with Keepass(self.prefix) as keepass:
            keepass.insert(entry)
            keepass.parse()
        self.assertEqual(keepass.data[0]['data'], ref['data'])
