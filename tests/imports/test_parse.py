# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
from unittest.mock import patch

import tests

REFERENCE_OTP = tests.yaml_load('otp.yml')
REFERENCE_WIFI = tests.yaml_load('networkmanager-wifi.yml')
REFERENCE_NOTE = tests.yaml_load('applekeychain-note.yml')
REFERENCE_CARD = tests.yaml_load('encryptr-card.yml')
REFERENCE_OTHER = tests.yaml_load('keepass-other.yml')
REFERENCE_KDBX = tests.yaml_load('keepass-kdbx.yml')
REFERENCE_REVELATION = tests.yaml_load('revelation-other.yml')
REFERENCE_BITWARDEN = tests.yaml_load('bitwarden-other.yml')


class TestParse(tests.Test):
    """Test the parse method of the importers against the reference data."""

    # Multiple importer tests

    @patch("getpass.getpass")
    def test_imports(self, pw):
        """Testing: parse method for all importers."""
        pw.return_value = self.masterpassword
        dkeep = ['title', 'password', 'login', 'url', 'comments', 'group']
        for manager in tests.conf:
            if not tests.conf[manager].get('parse', True):
                continue
            with self.subTest(manager):
                reference = tests.reference(manager)
                keep = tests.conf[manager].get('keep', dkeep)
                with tests.cls(manager) as importer:
                    importer.parse()
                    self.assertImport(importer.data, reference, keep)

    @patch("getpass.getpass")
    def test_imports_otp(self, pw):
        """Testing: parse method for all OTP importers."""
        keep = ['title', 'otpauth', 'type']
        pw.return_value = self.masterpassword
        otp = [
            'Aegis', 'AegisCipher', 'AndOTP', 'FreeOTPPlus',
            'GnomeAuthenticator'
        ]
        for manager in otp:
            with self.subTest(manager):
                with tests.cls(manager) as importer:
                    importer.parse()
                    self.assertImport(importer.data, REFERENCE_OTP, keep)

    # Single importer tests

    def test_import_applekeychain_notes(self):
        """Testing: parse method for AppleKeychain with notes."""
        prefix = os.path.join(tests.db, 'apple-keychain-note.txt')
        with tests.cls('AppleKeychain', prefix) as importer:
            importer.parse()
            self.assertImport(importer.data, REFERENCE_NOTE)

    def test_import_csv(self):
        """Testing: parse method for the generic CSV importer."""
        csv = ['OnePassword4CSV', 'Roboform']
        cols = {
            'OnePassword4CSV': 'title,comments,login,password,url',
            'Roboform': 'title,url,login,password,comments,group,,'
        }
        for manager in csv:
            with self.subTest(manager):
                prefix = os.path.join(tests.db, tests.conf[manager]['path'])
                reference = tests.reference(manager)
                with tests.cls('GenericCSV', prefix) as importer:
                    importer.cols = cols[manager]
                    importer.parse()
                    self.assertImport(importer.data, reference)

    def test_import_encryptr(self):
        """Testing: parse method for Encryptr with credit card."""
        keep = [
            'title', 'Type', 'Name on card', 'Card Number', 'CVV', 'Expiry',
            'group'
        ]
        prefix = os.path.join(tests.db, 'encryptr-card.csv')
        with tests.cls('Encryptr', prefix) as importer:
            importer.parse()
            self.assertImport(importer.data, REFERENCE_CARD, keep)

    @tests.skipIfNoModule('secretstorage')
    def test_import_gnome_keyring(self):
        """Testing: parse method for Gnome Keyring."""
        collection = 'pass-import'
        with tests.cls('GnomeKeyring', collection) as importer:
            importer.parse()
            data = importer.data

        # Manual cleaning
        reference = tests.reference()
        for key in ['group', 'login', 'url', 'comments']:
            for entry in reference:
                entry.pop(key, None)
        for entry in reference:
            entry['group'] = collection + entry.get('group', '')
        self.assertImport(data, reference)

    @patch("getpass.getpass")
    def test_import_keepass(self, pw):
        """Testing: parse method for Keepass Kdbx."""
        prefix = os.path.join(tests.db, 'keepass.kdbx')
        reference = tests.reference()
        pw.return_value = self.masterpassword
        with tests.cls('Keepass', prefix) as importer:
            importer.parse()
            data = importer.data

        # Manual cleaning
        reference.extend(REFERENCE_KDBX)
        for entry in data:
            if entry['title'] == 'news.ycombinator.com':
                entry['title'] = 'https://news.ycombinator.com'

        self.assertImport(data, reference,
                          keep=['title', 'password', 'login', 'url',
                                'comments', 'group', 'otpauth'])

    def test_import_keepass_other(self):
        """Testing: parse method for Keepass with special cases."""
        prefix = os.path.join(tests.db, 'keepass-other.xml')
        with tests.cls('KeepassXML', prefix) as importer:
            importer.parse()
            self.assertImport(importer.data, REFERENCE_OTHER)

    @tests.skipIfNoInstalled('lpass')
    @patch('pass_import.managers.LastpassCLI._command')
    @patch('pass_import.managers.LastpassCLI._call')
    @patch("getpass.getpass")
    def test_import_lastpass(self, pw, call, command):
        """Testing: parse method for Lastpass CLI."""
        # Generate mocked API call response
        show_uids_response = ['', tests.mocked('lastpass', 'list')]
        uids = [
            '8273029964772952977', '2484914384825433708',
            '6082506157297743545', '2708675046823528822',
            '4286509791900574846', '8309982398435317891',
            '4061988620109635891', '5256086908408307038',
            '3765864825443255811', '3243291093373152461',
            '5243770479038533622', '3905446787942154016',
            '6051084001543180250', '8440852123732500555',
        ]
        for ids in uids:
            show_uids_response.append(
                tests.mocked('lastpass', f'show-{ids}.json')
            )
            show_uids_response.append(
                tests.mocked('lastpass', f'show-{ids}')
            )
        show_uids_response.append('')  # sync

        pw.return_value = 'dummy'
        call.return_value = (1, None, None)
        command.side_effect = show_uids_response

        reference = tests.reference('LastpassCLI')
        with tests.cls('LastpassCLI', 'login', root='Import') as importer:
            importer.parse()
            self.assertImport(importer.data, reference)

    def test_import_networkmanager(self):
        """Testing: parse method for NetworkManager."""
        prefix = os.path.join(tests.db, 'networkmanager')
        with tests.cls('NetworkManager', prefix) as importer:
            importer.parse()
            self.assertImport(importer.data, REFERENCE_WIFI)

    def test_import_pass(self):
        """Testing: parse method for password-store."""
        prefix = os.path.join(tests.db, 'pass')
        reference = tests.reference()
        with tests.cls('PasswordStore', prefix) as importer:
            importer.parse()
            data = importer.data

        # Manual cleaning
        for entry in data:
            if entry['title'] == 'news.ycombinator.com':
                entry['title'] = 'https://news.ycombinator.com'
            if entry['group'] == 'Servers/ovh.com':
                entry['group'] = 'Servers'
                entry['title'] = 'ovh.com'
        self.assertImport(data, reference)

    def test_importers_revelation(self):
        """Testing: parse method for Revelation with special cases."""
        keep = [
            'title', 'password', 'login', 'database', 'host', 'port', 'url',
            'email', 'phone', 'location', 'description', 'comments', 'group'
        ]
        prefix = os.path.join(tests.db, 'revelation-other.xml')
        with tests.cls('Revelation', prefix) as importer:
            importer.parse()
            self.assertImport(importer.data, REFERENCE_REVELATION, keep)

    def test_importers_bitwarden(self):
        """Testing: parse method for Bitwarden with special cases."""
        keep = [
            'title', 'password', 'login', 'database', 'host', 'port', 'url',
            'email', 'phone', 'location', 'description', 'comments', 'group',
            'otpauth', 'title', 'brand', 'cardholderName', 'code', 'expMonth',
            'expYear', 'number', 'title', 'address1', 'address2', 'address3',
            'city', 'company', 'country', 'email', 'firstName', 'lastName',
            'licenseNumber', 'middleName', 'passportNumber', 'phone',
            'postalCode', 'ssn', 'username', 'passportNumber',
            'licenseNumber', 'title', 'comments', 'my text field',
            'my hidden field', 'a boolean field which is off',
            'a boolean field which is on', 'secureNote', 'title_', 'url2'
        ]
        prefix = os.path.join(tests.db, 'bitwarden-other.json')
        with tests.cls('BitwardenJSON', prefix) as importer:
            importer.parse()
            self.assertImport(importer.data, REFERENCE_BITWARDEN, keep)
