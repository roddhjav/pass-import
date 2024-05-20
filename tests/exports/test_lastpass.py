# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2022 Alexandre PUJOL <alexandre@pujol.io>.

from unittest.mock import patch

import tests
from pass_import.managers.lastpass import LastpassCLI


@tests.skipIfNoInstalled('lpass')
class TestExportLastpass(tests.Test):
    """Test for Lastpass."""

    def setUp(self):
        self.lpass = LastpassCLI()

    def test_lastpass_exist(self):
        """Testing: lastpass exist."""
        self.assertTrue(self.lpass.exist())

    def test_lastpass_isvalid(self):
        """Testing: lastpass validcredentials."""
        self.assertTrue(self.lpass.isvalid())

    @patch('pass_import.managers.LastpassCLI._command')
    def test_lastpass_list_empty(self, command):
        """Testing: lastpass list empty repository."""
        command.return_value = tests.mocked('lastpass', 'list')
        uids = self.lpass.list('Nothing')
        self.assertEqual(uids, [])

    @patch('pass_import.managers.LastpassCLI._command')
    def test_lastpass_list(self, command):
        """Testing: lastpass list repository."""
        command.return_value = tests.mocked('lastpass', 'list')
        ref = [
            '8273029964772952977', '2484914384825433708',
            '6082506157297743545', '2708675046823528822',
            '4286509791900574846', '8309982398435317891',
            '4061988620109635891', '5256086908408307038',
            '3765864825443255811', '3243291093373152461',
            '5243770479038533622', '3905446787942154016',
            '6051084001543180250', '8440852123732500555',
        ]
        uids = self.lpass.list('Import')
        self.assertEqual(len(uids), 14)
        self.assertEqual(uids, ref)

    @patch('pass_import.managers.LastpassCLI._command')
    def test_lastpass_show(self, command):
        """Testing: lastpass show."""
        command.side_effect = [
            tests.mocked('lastpass', 'show-8273029964772952977.json'),
            tests.mocked('lastpass', 'show-8273029964772952977'),
        ]
        ref = {
            'comments': '',
            'group': 'Import/Bank',
            'id': '8273029964772952977',
            'last_modified_gmt': '1483228800',
            'last_touch': '1483228800',
            'login': 'dpbx@fner.ws',
            'password': "ws5T@;_UB[Q|P!8'`~z%XC'JHFUbf#IX _E0}:HF,[{ei0hBg14",
            'pin': '462916',
            'title': 'aib',
            'url': 'https://onlinebanking.aib.ie',
        }
        entry = self.lpass.show('8273029964772952977')
        self.assertEqual(entry, ref)

    @patch('pass_import.managers.LastpassCLI._command')
    def test_lastpass_insert(self, command):
        """Testing: lastpass insert."""
        entry = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'pin': '97375',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test',
        }
        ref_arg = ['add', '--sync=now', '--non-interactive',
                   '--color=never', 'Unittests\\Test/test']
        ref_data = """Password: UuQHzvv6IHRIJGjwKru7
Username: lnqYm3ZWtm
URL: https://twitter.com
otpauth: otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&issuer=alice@google.com&algorithm=SHA1&digits=6&period=30
website: https://pujol.io
pin: 97375
"""
        command.side_effect = ['dummy', '']

        self.lpass.root = 'Unittests'
        self.lpass.force = True
        self.lpass.all = True
        self.lpass.insert(entry)

        arg = command.call_args_list[1][0][0]
        data = command.call_args_list[1][0][1]
        self.assertEqual(arg, ref_arg)
        self.assertEqual(data, ref_data)


@tests.skipIfNo('lastpass')
class TestExportLastpassAPI(tests.Test):
    """Test for Lastpass with API connection."""

    def setUp(self):
        self._credentials('lastpass')
        self.settings = {'all': True, 'force': True, 'root': 'Unittests'}

    @patch("getpass.getpass")
    def test_lastpass_insert_api(self, pw):
        """Testing: lastpass insert api."""
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
            'path': 'Test/test',
        }
        with LastpassCLI(self.login, settings=self.settings) as lpass:
            lpass.insert(entry)

    @patch("getpass.getpass")
    def test_lastpass_show_api(self, pw):
        """Testing: lastpass show api."""
        keep = {
            'password', 'login', 'url', 'website', 'otpauth', 'path',
            'comments', 'pin'
        }
        ref = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'pin': '97375',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',

        }

        pw.return_value = self.masterpassword
        with LastpassCLI(self.login, settings=self.settings) as lpass:
            uids = lpass.list('Unittests/Test/test')
            data = lpass.show(uids.pop())
            self.assertImport([data], [ref], keep)
