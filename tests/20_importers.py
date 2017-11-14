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
import setup
import unittest


class TestImporters(setup.TestPassSimple):

    def test_importers(self):
        """ Testing: importer parse method using real data. """
        self.refdata = self._get_refdata()
        for manager in self.passimport.importers:
            with self.subTest(manager):
                # Load importer class, file to test and parse the file
                ImporterClass = getattr(self.passimport,
                                        self.passimport.importers[manager][0])
                importer = ImporterClass(all=True)
                ext = '.xml' if manager in self.xml else '.csv'
                testfile = os.path.join(self.db, manager + ext)
                with open(testfile, 'r', encoding='utf-8') as file:
                    importer.parse(file)

                # Check the data parsed
                keys = ['title', 'password', 'login']
                refdata = self.refdata.copy()
                self._clean(keys, refdata)
                self._clean(keys, importer.data)
                for entry in importer.data:
                    self.assertIn(entry, refdata)

    def test_importers_format(self):
        """ Testing: importer file format """
        for manager in self.passimport.importers:
            if manager == 'dashlane':
                continue
            with self.subTest(manager):
                # Load importer class & file to test.
                ImporterClass = getattr(self.passimport,
                                        self.passimport.importers[manager][0])
                importer = ImporterClass()
                path = '.dummy.xml' if manager in self.xml else '.dummy.csv'
                testfile = os.path.join(self.db, path)

                # Parse the file
                with self.assertRaises(self.passimport.FormatError):
                    with open(testfile, 'r', encoding='utf-8') as file:
                        importer.parse(file)


if __name__ == '__main__':
    unittest.main()
