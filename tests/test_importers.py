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
import sys
from unittest.mock import patch

import yaml
from tests.commons import TestBaseImport


REF_DB = 'tests/references/'
REFERENCE_OTP = yaml.safe_load(open(REF_DB + 'otp.yml', 'r'))
REFERENCE_WIFI = yaml.safe_load(open(REF_DB + 'networkmanager-wifi.yml', 'r'))
REFERENCE_NOTE = yaml.safe_load(open(REF_DB + 'applekeychain-note.yml', 'r'))
REFERENCE_CARD = yaml.safe_load(open(REF_DB + 'encryptr-card.yml', 'r'))
REFERENCE_OTHER = yaml.safe_load(open(REF_DB + 'keepass-other.yml', 'r'))
REFERENCE_KDBX = yaml.safe_load(open(REF_DB + 'keepass-kdbx.yml', 'r'))
REFERENCE_REVELATION = yaml.safe_load(open('tests/references/revelation-other.yml', 'r'))


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
        keep = ['title', 'otpauth', 'type']
        otp = ['andotp', 'gnome-authenticator', 'aegis']
        for manager in otp:
            with self.subTest(manager):
                importer = self._class(manager)
                testpath = os.path.join(self.db, manager + '.json')
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
                importer = self._class('csv')
                importer.cols = cols[manager]
                testpath = self._path(manager)
                reference = self._reference(manager)
                encoding = self.importers[manager]['encoding']
                with open(testpath, 'r', encoding=encoding) as file:
                    importer.parse(file)

                self.assertImport(importer.data, reference)

    def test_importers_pass(self):
        """Testing: parse method for password-store."""
        importer = self._class('pass')
        reference = self._reference()
        prefix = os.path.join(self.db, 'pass')
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
        importer = self._class('keepass')
        reference = self._reference()
        pw.return_value = self.masterpassword
        testpath = os.path.join(self.db, 'keepass.kdbx')
        importer.parse(testpath)

        reference.extend(REFERENCE_KDBX)
        for entry in importer.data:
            if entry['title'] == 'news.ycombinator.com':
                entry['title'] = 'https://news.ycombinator.com'

        self.assertImport(importer.data, reference)

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
        importer = self._class('keepass-xml')
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
    def test_importers_aegis(self, pw):
        """Testing: parse method for Aegis encrypted with AES."""
        keep = ['title', 'otpauth', 'type']
        importer = self._class('aegis')
        pw.return_value = self.masterpassword
        testpath = os.path.join(self.db, 'aegis.cipher.json')
        with open(testpath, 'r') as file:
            importer.parse(file)

        self.assertImport(importer.data, REFERENCE_OTP, keep)

    @patch("getpass.getpass")
    def test_importers_andotpaes(self, pw):
        """Testing: parse method for andOTP encrypted with AES."""
        keep = ['title', 'otpauth', 'type']
        importer = self._class('andotp')
        pw.return_value = self.masterpassword
        testpath = os.path.join(self.db, 'andotp.json.aes')
        with open(testpath, 'r') as file:
            importer.parse(file)

        self.assertImport(importer.data, REFERENCE_OTP, keep)

    def test_importers_andotpgpg(self):
        """Testing: parse method for andOTP encrypted with GPG."""
        keep = ['title', 'otpauth', 'type']
        importer = self._class('andotp')
        testpath = os.path.join(self.db, 'andotp.gpg')
        with open(testpath, 'r') as file:
            importer.parse(file)

        self.assertImport(importer.data, REFERENCE_OTP, keep)

    def test_importers_gnomekeyring(self):
        """Testing: parse method for Gnome Keyring."""
        if sys.version_info.minor < 5:
            return
        collection = 'pass-import'
        importer = self._class('gnome-keyring')
        reference = self._reference()
        importer.parse(collection)

        for key in ['group', 'login', 'url', 'comments']:
            for entry in reference:
                entry.pop(key, None)
        for entry in reference:
            entry['group'] = collection + entry.get('group', '')
        self.assertImport(importer.data, reference)

    def test_importers_revelationother(self):
        """Testing: parse method for Revelation with special cases."""
        keyslist = ['title', 'password', 'login', 'database', 'host', 'port',
                    'url', 'email', 'phone', 'location', 'description',
                    'comments']
        keyslist.append('group')
        importer = self._class('revelation')
        testpath = os.path.join(self.db, 'revelation-other.xml')
        with open(testpath, 'r') as file:
            importer.parse(file)
        self.assertImport(importer.data, REFERENCE_REVELATION, keep=keyslist)
