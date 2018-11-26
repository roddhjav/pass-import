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
from collections import OrderedDict as Odict

from .. import pass_import
from tests.commons import TestPassSimple


class TestPasswordManager(TestPassSimple):
    def setUp(self):
        self.importer = pass_import.PasswordManager()


class TestPasswordManagerGeneral(TestPasswordManager):

    def test_get_data(self):
        """Testing: convert dict to password entry."""
        entry = Odict([('password', 'EaP:bCmLZliqa|]WR/#HZP'),
                       ('login', 'roddhjav'),
                       ('comments', 'This is a comment')])
        entry_expected = "EaP:bCmLZliqa|]WR/#HZP\nlogin: roddhjav\ncomments: This is a comment\n"
        self.assertEqual(self.importer.get(entry), entry_expected)

    def test_get_empty(self):
        """Testing: convert empty dict to password entry."""
        entry = Odict()
        entry_expected = '\n'
        self.assertEqual(self.importer.get(entry), entry_expected)

    def test_replaces(self):
        """Testing: _replace method."""
        string = ''
        string_expected = ''
        caracters = {}
        string = self.importer._replaces(caracters, string)
        self.assertEqual(string, string_expected)

    def test_clean_cmdline(self):
        """Testing: _clean_cmdline method."""
        string = 'Root Group&Named@root\'[directory]'
        string_expected = 'Root_GroupandNamedAtrootdirectory'
        string = self.importer._clean_cmdline(string)
        self.assertEqual(string, string_expected)

    def test_clean_protocol(self):
        """Testing: _clean_protocol method."""
        string = 'https://duckduckgo.comhttp://google.com'
        string_expected = 'duckduckgo.comgoogle.com'
        string = self.importer._clean_protocol(string)
        self.assertEqual(string, string_expected)

    def test_clean_group(self):
        """Testing: _clean_group method."""
        string = 'Root/Group\\Named>root\0directory'
        string_expected = 'Root%sGroup%sNamed-root-directory' % (os.sep, os.sep)
        string = self.importer._clean_group(string)
        self.assertEqual(string, string_expected)

    def test_convert(self):
        """Testing: _convert method."""
        string = 'Root/Group\\Named>root\0directory'
        string_expected = 'Root-Group-Named-root-directory'
        string = self.importer._convert(string)
        self.assertEqual(string, string_expected)

    def test_convert_separator(self):
        """Testing: _convert method with ~ as separator."""
        string = 'Root/Group\\Named>root\0directory'
        string_expected = 'Root~Group~Named~root~directory'
        self.importer.separator = '~'
        string = self.importer._convert(string)
        self.assertEqual(string, string_expected)


class TestPasswordManagerClean(TestPasswordManager):

    def test_data(self):
        """Testing: clean data."""
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
        self.importer.clean(clean=False, convert=False)
        self.assertEqual(self.importer.data, self.data_expected)

    def test_all(self):
        """Testing: clean all data."""
        self.importer.data = [Odict([('title', 'https://twitter@com'),
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
                                     ('path', 'Social/twitterAtcom')])]
        self.importer.clean(clean=True, convert=False)
        self.assertEqual(self.importer.data, self.data_expected)

    def tests_url(self):
        """Testing: clean data - url as path name."""
        self.importer.data = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                     ('login', 'lnqYm3ZWtm'),
                                     ('url', 'twitter.com')])]
        data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                ('login', 'lnqYm3ZWtm'),
                                ('url', 'twitter.com'),
                                ('path', 'lnqYm3ZWtm')])]
        self.importer.clean(clean=False, convert=False)
        self.assertEqual(self.importer.data, data_expected)

    def tests_login(self):
        """Testing: clean data - login as path name."""
        self.importer.data = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                     ('login', 'lnqYm3ZWtm')])]
        data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                ('login', 'lnqYm3ZWtm'),
                                ('path', 'lnqYm3ZWtm')])]
        self.importer.clean(clean=False, convert=False)
        self.assertEqual(self.importer.data, data_expected)

    def tests_notitle(self):
        """Testing: clean data - notitle as path name."""
        self.importer.data = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7')])]
        data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                ('path', 'notitle')])]
        self.importer.clean(clean=False, convert=False)
        self.assertEqual(self.importer.data, data_expected)

    def tests_empty(self):
        """Testing: clean data - empty title and clean enabled."""
        self.importer.data = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7')])]
        data_expected = [Odict([('password', 'UuQHzvv6IHRIJGjwKru7'),
                                ('path', 'notitle')])]
        self.importer.clean(clean=True, convert=False)
        self.assertEqual(self.importer.data, data_expected)

    def test_convert(self):
        """Testing: convert password path."""
        self.importer.data = [Odict([('title', 'ovh>com'),
                                     ('password', 'AGJjkMPsRUqDXyUdLbC4'),
                                     ('login', 'lnqYm3ZWtm')]),
                              Odict([('password', 'VRiplZSniSBlHNnQvc9e'),
                                     ('login', 'fm/mhpv*ity')])]
        data_expected = [Odict([('password', 'AGJjkMPsRUqDXyUdLbC4'),
                                ('login', 'lnqYm3ZWtm'),
                                ('path', 'ovh-com')]),
                         Odict([('password', 'VRiplZSniSBlHNnQvc9e'),
                                ('login', 'fm/mhpv*ity'),
                                ('path', 'fm-mhpv-ity')])]
        self.importer.clean(clean=False, convert=True)
        self.assertEqual(self.importer.data, data_expected)


class TestPasswordManagerDuplicate(TestPasswordManager):

    def test_paths(self):
        """Testing: duplicate paths."""
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
                                ('path', 'ovh.com/lnqYm3ZWtm')]),
                         Odict([('password', 'VRiplZSniSBlHNnQvc9e'),
                                ('login', 'lnqYm3ZWtm'),
                                ('path', 'ovh.com/lnqYm3ZWtm-1')]),
                         Odict([('password', '[Q&$\fd]!`vKA&b'),
                                ('login', 'fmmhpvity'),
                                ('path', 'ovh.com/fmmhpvity')]),
                         Odict([('password', 'DQm_Y+a(sDC)[1|U-S<8Dq!A'),
                                ('login', 'ptfzlnvmj'),
                                ('path', 'ovh.com/ptfzlnvmj')])]
        self.importer.clean(clean=False, convert=False)
        self.assertEqual(self.importer.data, data_expected)

    def test_subfolder(self):
        """Testing: duplicate to subfolder."""
        self.importer.data = [Odict([('title', 'google.com'),
                                     ('login', 'mdtx@gmail.com'),
                                     ('group', 'Emails')]),
                              Odict([('title', 'google.com'),
                                     ('login', 'lnqY@gmail.com'),
                                     ('group', 'Emails')]),
                              Odict([('title', 'google.com'),
                                     ('login', 'fmmh@gmail.com'),
                                     ('group', 'Emails')]),
                              Odict([('title', 'google.com'),
                                     ('login', 'ptfz@gmail.com'),
                                     ('group', 'Emails')])]
        data_expected = [Odict([('login', 'mdtx@gmail.com'),
                                ('path', 'Emails/google.com/mdtx@gmail.com')]),
                         Odict([('login', 'lnqY@gmail.com'),
                                ('path', 'Emails/google.com/lnqY@gmail.com')]),
                         Odict([('login', 'fmmh@gmail.com'),
                                ('path', 'Emails/google.com/fmmh@gmail.com')]),
                         Odict([('login', 'ptfz@gmail.com'),
                                ('path', 'Emails/google.com/ptfz@gmail.com')])]
        self.importer.clean(clean=False, convert=False)
        self.assertEqual(self.importer.data, data_expected)

    def test_numbers(self):
        """Testing: duplicate with numbers."""
        self.importer.data = [Odict([('title', 'ovh.com')]),
                              Odict([('title', 'ovh.com')]),
                              Odict([('title', 'ovh.com')]),
                              Odict([('title', 'ovh.com')])]
        data_expected = [Odict([('path', 'ovh.com/notitle')]),
                         Odict([('path', 'ovh.com/notitle-1')]),
                         Odict([('path', 'ovh.com/notitle-2')]),
                         Odict([('path', 'ovh.com/notitle-3')])]
        self.importer.clean(clean=False, convert=False)
        self.assertEqual(self.importer.data, data_expected)
