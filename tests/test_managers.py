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

from collections import OrderedDict as Odict

from .. import pass_import
from tests.commons import TestPassSimple


class TestPasswordManager(TestPassSimple):

    def setUp(self):
        self.importer = pass_import.PasswordManager()
        self.importer.data = [Odict([('title', 'twitter.com'),
                                     ('password', 'UuQHzvv6IHRIJGjwKru7'),
                                     ('login', 'lnqYm3ZWtm'),
                                     ('url', 'https://twitter.com'),
                                     ('comments', ''),
                                     ('group', 'Social'),
                                     ('address', ''),
                                     ('sex', ''),
                                     ('website', 'https://pujol.io'),
                                     ('uuid', '44jle5q3fdvrprmaahozexy2pi')])]
        self.data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                     ('login', 'lnqYm3ZWtm'),
                                     ('url', 'https://twitter.com'),
                                     ('website', 'https://pujol.io'),
                                     ('uuid', '44jle5q3fdvrprmaahozexy2pi'),
                                     ('path', 'Social/twitter.com')])]

    def test_get_data(self):
        """Testing: convert dict to password entry."""
        entry = Odict([('password', 'EaP:bCmLZliqa|]WR/#HZP'),
                       ('login', 'roddhjav'),
                       ('comments', 'This is a comment')])
        entry_expected = "EaP:bCmLZliqa|]WR/#HZP\nlogin: roddhjav\ncomments: This is a comment\n"
        self.assertTrue(self.importer.get(entry) == entry_expected)

    def test_get_empty(self):
        """Testing: convert empty dict to password entry."""
        entry = Odict()
        entry_expected = '\n'
        self.assertTrue(self.importer.get(entry) == entry_expected)

    def test_clean_data(self):
        """Testing: clean data."""
        self.importer.clean(clean=False)
        self.assertTrue(self.importer.data == self.data_expected)

    def test_clean_all(self):
        """Testing: clean all data."""
        self.importer.data[0]['title'] = 'https://twitter@com'
        self.data_expected[0]['path'] = 'Social/twitterAtcom'
        self.importer.clean(clean=True)
        self.assertTrue(self.importer.data == self.data_expected)

    def test_clean_path(self):
        """Testing: clean data & generate password path."""
        # Test url as path name
        self.importer.data = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                     ('login', 'lnqYm3ZWtm'),
                                     ('url', 'twitter.com')])]
        data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                ('login', 'lnqYm3ZWtm'),
                                ('url', 'twitter.com'),
                                ('path', 'twitter.com')])]
        self.importer.clean(clean=False)
        self.assertTrue(self.importer.data == data_expected)

        # Test login as path name
        self.importer.data = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                     ('login', 'lnqYm3ZWtm')])]
        data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                ('login', 'lnqYm3ZWtm'),
                                ('path', 'lnqYm3ZWtm')])]
        self.importer.clean(clean=False)
        self.assertTrue(self.importer.data == data_expected)

        # Test notitle as path name
        self.importer.data = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7')])]
        data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                ('path', 'notitle')])]
        self.importer.clean(clean=False)
        self.assertTrue(self.importer.data == data_expected)

    def test_clean_duplicate_paths(self):
        """Testing: clean duplicate paths."""
        self.importer.data = [Odict([('title', 'ovh.com'),
                                     ('password', 'AGJjkMPsRUqDXyUdLbC4'),
                                     ('login', 'lnqYm3ZWtm')]),
                              Odict([('title', 'ovh.com'),
                                     ('password', 'VRiplZSniSBlHNnQvc9e'),
                                     ('login', 'lnqYm3ZWtm')]),
                              Odict([('title', 'ovh.com'),
                                     ('password', '[Q&$\fd]!`vKA&b'),
                                     ('login', 'fmmhpvity')]),
                              Odict([('title', 'ovh.com'),
                                     ('password', 'DQm_Y+a(sDC)[1|U-S<8Dq!A'),
                                     ('login', 'ptfzlnvmj')])]
        data_expected = [Odict([('password', 'AGJjkMPsRUqDXyUdLbC4'),
                                ('login', 'lnqYm3ZWtm'),
                                ('path', 'ovh.com')]),
                         Odict([('password', 'VRiplZSniSBlHNnQvc9e'),
                                ('login', 'lnqYm3ZWtm'),
                                ('path', 'ovh.com0')]),
                         Odict([('password', '[Q&$\fd]!`vKA&b'),
                                ('login', 'fmmhpvity'),
                                ('path', 'ovh.com1')]),
                         Odict([('password', 'DQm_Y+a(sDC)[1|U-S<8Dq!A'),
                                ('login', 'ptfzlnvmj'),
                                ('path', 'ovh.com2')])]
        self.importer.clean(clean=False)
        self.assertTrue(self.importer.data == data_expected)
