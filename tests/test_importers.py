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

import yaml
from tests.commons import TestBaseImport


REFERENCE_OTP = yaml.safe_load(open('tests/references/otp.yml', 'r'))
REFERENCE_WIFI = yaml.safe_load(open('tests/references/networkmanager-wifi.yml', 'r'))
REFERENCE_NOTE = yaml.safe_load(open('tests/references/applekeychain-note.yml', 'r'))
REFERENCE_CARD = yaml.safe_load(open('tests/references/encryptr-card.yml', 'r'))
REFERENCE_OTHER = yaml.safe_load(open('tests/references/keepass-other.yml', 'r'))




class TestImporters(TestBaseImport):

    def test_importers_generic(self):
        """Testing: parse method for all importers."""
        for manager in self.importers:
            with self.subTest(manager):
                importer = self._class(manager)
                testpath = self._path(manager)
                reference = self._reference(manager)
                encoding = self.importers[manager]['encoding']
                with open(testpath, 'r', encoding=encoding) as file:
                    importer.parse(file)

                self.assertImport(importer.data, reference)

    def test_importers_otp(self):
        """Testing: parse method for all OTP importers."""
        keep = ['title', 'otpauth', 'tags', 'type']
        otp = ['andotp', 'gnome-authenticator']
        for manager in otp:
            with self.subTest(manager):
                importer = self._class(manager)
                testpath = os.path.join(self.db, manager + '.json')
                with open(testpath, 'r') as file:
                    importer.parse(file)

                self.assertImport(importer.data, REFERENCE_OTP, keep)

    def test_importers_networkmanager(self):
        """Testing: parse method for Network Manager."""
        importer = self._class('networkmanager')
        testpath = os.path.join(self.db, 'networkmanager')
        importer.parse(testpath)
        self.assertImport(importer.data, REFERENCE_WIFI)

    def test_importers_applekeychain_note(self):
        """Testing: parse method for AppleKeychain with notes."""
        importer = self._class('apple-keychain')
        testpath = os.path.join(self.db, 'apple-keychain-note.txt')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_NOTE)

    def test_importers_keepassother(self):
        """Testing: parse method for Keepass with special cases."""
        importer = self._class('keepass')
        testpath = os.path.join(self.db, 'keepass-other.xml')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_OTHER)

    def test_importers_keepassxother(self):
        """Testing: parse method for KeepassX with special cases."""
        importer = self._class('keepassx')
        testpath = os.path.join(self.db, 'keepassx-other.xml')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_OTHER)

    def test_importers_encryptr(self):
        """Testing: parse method for Encryptr with credit card."""
        keep = ['title', 'Type', 'Name on card', 'Card Number', 'CVV',
                'Expiry', 'group']
        importer = self._class('encryptr')
        testpath = os.path.join(self.db, 'encryptr-card.csv')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_CARD, keep)

    @patch("getpass.getpass")
    def test_importers_andotpAES(self, pw):
        """Testing: parse method for andOTP encrypted wit AES."""
        keep = ['title', 'otpauth', 'tags', 'type']
        importer = self._class('andotp')
        pw.return_value = self.masterpassword
        testpath = os.path.join(self.db, 'andotp.json.aes')
        with open(testpath, 'r') as file:
            importer.parse(file)

        self.assertImport(importer.data, REFERENCE_OTP, keep)
