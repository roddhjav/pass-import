# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2022 Alexandre PUJOL <alexandre@pujol.io>.
#

from unittest.mock import patch

import tests
from pass_import.managers.bitwarden import BitwardenCLI


class TestExportBitwarden(tests.Test):
    """Test for Bitwarden."""

    def setUp(self):
        self.bw = BitwardenCLI()

    def test_bitwarden_exist(self):
        """Testing: bitwarden exist."""
        self.assertTrue(self.bw.exist())

    def test_bitwarden_isvalid(self):
        """Testing: bitwarden validcredentials."""
        self.assertTrue(self.bw.isvalid())


@tests.skipIfNo('bitwarden')
class TestExportBitwardenAPI(tests.Test):
    """Test for Bitwarden with API connexion."""

    def setUp(self):
        self._credentials('bitwarden')
        self.settings = {'all': True, 'force': True, 'root': 'Unittests'}

    @patch("getpass.getpass")
    def test_bitwarden_insert_api(self, pw):
        """Testing: bitwarden insert api."""
        pw.return_value = self.masterpassword
        entry = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'pin': '97375',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }
        print('LOGIN', self.login)
        with BitwardenCLI(self.login, settings=self.settings) as bw:
            # bw.list()
            bw.insert(entry)
