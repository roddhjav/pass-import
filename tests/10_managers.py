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

import setup
import unittest


class TestPasswordManager(setup.TestPassSimple):

    def setUp(self):
        self.importer = self.passimport.PasswordManager()

    def test_get_data(self):
        """ Testing: convert dict to password entry """
        entry = {'password': 'EaP:bCmLZliqa|]WR/#HZP-aa', 'login': 'roddhjav',
                 'comments': 'This is a comment'}
        entry_expected = "EaP:bCmLZliqa|]WR/#HZP-aa\nlogin: roddhjav\ncomments: This is a comment\n"
        self.assertTrue(self.importer.get(entry) == entry_expected)

    def test_get_empty(self):
        """ Testing: convert empty dict to password entry """
        entry = dict()
        entry_expected = ""
        self.assertTrue(self.importer.get(entry) == entry_expected)

    def test_satanize_data(self):
        """ Testing: satanize data """
        self.importer.data = [{'title': 'twitter.com',
                               'password': 'UuQHzvv6IHRIJGjwKru7',
                               'login': 'lnqYm3ZWtm',
                               'url': 'https://twitter.com',
                               'comments': '',
                               'group': 'Social',
                               'address': '',
                               'sex': '',
                               'website': 'https://pujol.io',
                               'uuid': '44jle5q3fdvrprmaahozexy2pi'}]
        data_expected = [{'password': 'UuQHzvv6IHRIJGjwKru7',
                          'login': 'lnqYm3ZWtm',
                          'url': 'twitter.com',
                          'website': 'https://pujol.io',
                          'uuid': '44jle5q3fdvrprmaahozexy2pi',
                          'path': 'Social/twitter.com'}]
        self.importer.satanize(False)
        self.assertTrue(self.importer.data == data_expected)

    def test_satanize_clean(self):  # Works with MORE fake test data
        """ Testing: satanize and clean data """
        self.importer.data = [{'title': 'https://twitter@com',
                               'password': 'UuQHzvv6IHRIJGjwKru7',
                               'login': 'lnqYm3ZWtm',
                               'url': 'https://twitter.com',
                               'comments': '',
                               'group': 'Social',
                               'address': '',
                               'sex': '',
                               'website': 'https://pujol.io',
                               'uuid': '44jle5q3fdvrprmaahozexy2pi'}]
        data_expected = [{'password': 'UuQHzvv6IHRIJGjwKru7',
                          'login': 'lnqYm3ZWtm',
                          'url': 'twitter.com',
                          'website': 'https://pujol.io',
                          'uuid': '44jle5q3fdvrprmaahozexy2pi',
                          'path': 'Social/twitterAtcom'}]
        self.importer.satanize(True)
        self.assertTrue(self.importer.data == data_expected)

    def test_satanize_path(self):
        """ Testing: satanize data & generate password path"""
        # Test url as path name
        self.importer.data = [{'password': 'UuQHzvv6IHRIJGjwKru7',
                               'login': 'lnqYm3ZWtm',
                               'url': 'twitter.com'}]
        data_expected = [{'password': 'UuQHzvv6IHRIJGjwKru7',
                          'login': 'lnqYm3ZWtm',
                          'url': 'twitter.com',
                          'path': 'twitter.com'}]
        self.importer.satanize(False)
        self.assertTrue(self.importer.data == data_expected)

        # Test login as path name
        self.importer.data = [{'password': 'UuQHzvv6IHRIJGjwKru7',
                               'login': 'lnqYm3ZWtm'}]
        data_expected = [{'password': 'UuQHzvv6IHRIJGjwKru7',
                          'login': 'lnqYm3ZWtm',
                          'path': 'lnqYm3ZWtm'}]
        self.importer.satanize(False)
        self.assertTrue(self.importer.data == data_expected)

        # Test notitle as path name
        self.importer.data = [{'password': 'UuQHzvv6IHRIJGjwKru7'}]
        data_expected = [{'password': 'UuQHzvv6IHRIJGjwKru7',
                          'path': 'notitle'}]
        self.importer.satanize(False)
        self.assertTrue(self.importer.data == data_expected)

    def test_satanize_duplicate_paths(self):
        """ Testing: satanize duplicate paths """
        self.importer.data = [{'title': 'ovh.com',
                               'password': 'AGJjkMPsRUqDXyUdLbC4',
                               'login': 'lnqYm3ZWtm'},
                              {'title': 'ovh.com',
                               'password': 'VRiplZSniSBlHNnQvc9e',
                               'login': 'lnqYm3ZWtm'}]
        data_expected = [{'password': 'AGJjkMPsRUqDXyUdLbC4',
                          'login': 'lnqYm3ZWtm',
                          'path': 'ovh.com'},
                         {'password': 'VRiplZSniSBlHNnQvc9e',
                          'login': 'lnqYm3ZWtm',
                          'path': 'ovh.com0'}]
        self.importer.satanize(False)
        self.assertTrue(self.importer.data == data_expected)


if __name__ == '__main__':
    unittest.main()
