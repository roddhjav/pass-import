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
import sys
import unittest
from collections import OrderedDict
try:
    sys.path.append('../lib')
    passimport = __import__('import')
except Exception as e:
    print("Unable to find import.py: %s", e)
    exit(1)

PLAIN_DB = "exporteddb/"

class TestImporters(unittest.TestCase):
    xml = ['fpm', 'keepassx', 'keepass', 'pwsafe', 'revelation']

    def test_importers_check_format(self):
        """ Testing: importer file format """
        passimport.importers.pop('dashlane', None)
        for manager in passimport.importers:
            with self.subTest(manager):
                # Load importer class, fike to test and parse the file
                ImporterClass = getattr(passimport,
                                        passimport.importers[manager][0])
                importer = ImporterClass()
                if manager in self.xml:
                    testfile = os.path.join(PLAIN_DB, '.dummy.xml')
                else:
                    testfile = os.path.join(PLAIN_DB, '.dummy.csv')

                with self.assertRaises(passimport.FormatError):
                    with open(testfile, 'r', encoding='utf-8') as file:
                        importer.parse(file)


if __name__ == '__main__':
    unittest.main()
