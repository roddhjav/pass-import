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
import yaml

from pass_import import FormatError
import tests


class TestImporterFormat(tests.Test):
    """Ensure the parse method fail when a malformed file is given."""
    formaterror = (FormatError, AttributeError, ValueError,
                   yaml.scanner.ScannerError)

    def test_importer_format(self):
        """Testing: file format for all importers."""
        ignore = ['dashlane', 'keeper', 'upm']
        for manager in self.tests:
            if manager in ignore:
                continue
            with self.subTest(manager):
                importer = self._class(manager)
                ext = self.tests[manager]['extension']
                testpath = os.path.join(self.format, 'dummy.' + ext)

                with self.assertRaises(self.formaterror):
                    with open(testpath, 'r', encoding='utf-8') as file:
                        importer.parse(file)

    def test_importer_format_otp(self):
        """Testing: file format for OTP based importers."""
        importer = self._class('aegis')
        testpath = os.path.join(self.db, 'andotp.json')
        with self.assertRaises(self.formaterror):
            with open(testpath, 'r', encoding='utf-8') as file:
                importer.parse(file)

    def test_importer_format_csv(self):
        """Testing: file format for generic CSV importer."""
        importer = self._class('csv')
        testpath = os.path.join(self.db, 'lastpass.csv')
        importer.cols = ''
        with self.assertRaises(self.formaterror):
            with open(testpath, 'r', encoding='utf-8') as file:
                importer.parse(file)
