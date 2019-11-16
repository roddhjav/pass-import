#!/usr/bin/env python3
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017-2019 Alexandre PUJOL <alexandre@pujol.io>.
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
from unittest.mock import patch

import tests


REFERENCE_OTP = tests.yaml_load('otp.yml')
REFERENCE_WIFI = tests.yaml_load('networkmanager-wifi.yml')
REFERENCE_NOTE = tests.yaml_load('applekeychain-note.yml')
REFERENCE_CARD = tests.yaml_load('encryptr-card.yml')
REFERENCE_OTHER = tests.yaml_load('keepass-other.yml')
REFERENCE_KDBX = tests.yaml_load('keepass-kdbx.yml')


class TestImporters(tests.Test):
    """Test the parse method of the importers against the reference data."""

    def test_importers_generic(self):
        """Testing: parse method for all importers."""
        for manager in tests.conf:
            with self.subTest(manager):
                importer = tests.cls(manager)
                testpath = tests.path(manager)
                reference = tests.reference(manager)
                encoding = tests.conf[manager]['encoding']
                with open(testpath, 'r', encoding=encoding) as file:
                    importer.parse(file)

                self.assertImport(importer.data, reference)

    def test_importers_otp(self):
        """Testing: parse method for all OTP importers."""
        keep = ['title', 'otpauth', 'type']
        otp = ['andotp', 'gnome-authenticator', 'aegis']
        for manager in otp:
            with self.subTest(manager):
                importer = tests.cls(manager)
                testpath = os.path.join(tests.db, manager + '.json')
                with open(testpath, 'r') as file:
                    importer.parse(file)

                self.assertImport(importer.data, REFERENCE_OTP, keep)

    def test_importers_csv(self):
        """Testing: parse method for the generic CSV importer."""
        csv = ['1password4', 'dashlane', 'roboform']
        cols = {'1password4': 'title,comments,login,password,url',
                'dashlane': 'title,url,login,password,comments,,',
                'roboform': 'title,url,login,password,comments,group,,'}
        for manager in csv:
            with self.subTest(manager):
                importer = tests.cls('csv')
                importer.cols = cols[manager]
                testpath = tests.path(manager)
                reference = tests.reference(manager)
                encoding = tests.conf[manager]['encoding']
                with open(testpath, 'r', encoding=encoding) as file:
                    importer.parse(file)

                self.assertImport(importer.data, reference)

    def test_importers_pass(self):
        """Testing: parse method for password-store."""
        importer = tests.cls('pass')
        reference = tests.reference()
        prefix = os.path.join(tests.db, 'pass')
        importer.parse(prefix)

        #
        for entry in importer.data:
            if entry['title'] == 'news.ycombinator.com':
                entry['title'] = 'https://news.ycombinator.com'
            if entry['group'] == 'Servers/ovh.com':
                entry['group'] = 'Servers'
                entry['title'] = 'ovh.com'
        self.assertImport(importer.data, reference)

    @patch("getpass.getpass")
    def test_importers_keepass(self, pw):
        """Testing: parse method for Keepass Kdbx."""
        importer = tests.cls('keepass')
        reference = tests.reference()
        pw.return_value = tests.masterpassword
        testpath = os.path.join(tests.db, 'keepass.kdbx')
        importer.parse(testpath)

        reference.extend(REFERENCE_KDBX)
        for entry in importer.data:
            if entry['title'] == 'news.ycombinator.com':
                entry['title'] = 'https://news.ycombinator.com'

        self.assertImport(importer.data, reference)

    def test_importers_networkmanager(self):
        """Testing: parse method for Network Manager."""
        importer = tests.cls('networkmanager')
        testpath = os.path.join(tests.db, 'networkmanager')
        importer.parse(testpath)
        self.assertImport(importer.data, REFERENCE_WIFI)

    def test_importers_applekeychain_note(self):
        """Testing: parse method for AppleKeychain with notes."""
        importer = tests.cls('apple-keychain')
        testpath = os.path.join(tests.db, 'apple-keychain-note.txt')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_NOTE)

    def test_importers_keepassother(self):
        """Testing: parse method for Keepass with special cases."""
        importer = tests.cls('keepass-xml')
        testpath = os.path.join(tests.db, 'keepass-other.xml')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_OTHER)

    def test_importers_keepassxother(self):
        """Testing: parse method for KeepassX with special cases."""
        importer = tests.cls('keepassx')
        testpath = os.path.join(tests.db, 'keepassx-other.xml')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_OTHER)

    def test_importers_encryptr(self):
        """Testing: parse method for Encryptr with credit card."""
        keep = ['title', 'Type', 'Name on card', 'Card Number', 'CVV',
                'Expiry', 'group']
        importer = tests.cls('encryptr')
        testpath = os.path.join(tests.db, 'encryptr-card.csv')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_CARD, keep)

    @patch("getpass.getpass")
    def test_importers_aegis(self, pw):
        """Testing: parse method for Aegis encrypted with AES."""
        keep = ['title', 'otpauth', 'type']
        importer = tests.cls('aegis')
        pw.return_value = tests.masterpassword
        testpath = os.path.join(tests.db, 'aegis.cipher.json')
        with open(testpath, 'r') as file:
            importer.parse(file)

        self.assertImport(importer.data, REFERENCE_OTP, keep)

    @patch("getpass.getpass")
    def test_importers_andotpaes(self, pw):
        """Testing: parse method for andOTP encrypted with AES."""
        keep = ['title', 'otpauth', 'type']
        importer = tests.cls('andotp')
        pw.return_value = tests.masterpassword
        testpath = os.path.join(tests.db, 'andotp.json.aes')
        with open(testpath, 'r') as file:
            importer.parse(file)

        self.assertImport(importer.data, REFERENCE_OTP, keep)

    def test_importers_andotpgpg(self):
        """Testing: parse method for andOTP encrypted with GPG."""
        keep = ['title', 'otpauth', 'type']
        importer = tests.cls('andotp')
        testpath = os.path.join(tests.db, 'andotp.gpg')
        with open(testpath, 'r') as file:
            importer.parse(file)

        self.assertImport(importer.data, REFERENCE_OTP, keep)

    def test_importers_gnomekeyring(self):
        """Testing: parse method for Gnome Keyring."""
        collection = 'pass-import'
        importer = tests.cls('gnome-keyring')
        reference = tests.reference()
        importer.parse(collection)

        for key in ['group', 'login', 'url', 'comments']:
            for entry in reference:
                entry.pop(key, None)
        for entry in reference:
            entry['group'] = collection + entry.get('group', '')
        self.assertImport(importer.data, reference)
