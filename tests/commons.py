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
import shutil
import unittest
import pass_import


class TestBase(unittest.TestCase):
    tmp = "/tmp/pass-import/python/"
    gpgids = ['D4C78DB7920E1E27F5416B81CC9DB947CF90C77B', '']
    xml = ['fpm', 'keepassx', 'keepass', 'pwsafe', 'revelation', 'kedpm']
    db = "tests/db/"


class TestPass(TestBase):
    """Base test class for passwordstore related tests.
    This base test class provides the unittest with.
        1. A working gpg keyring
        2. A directory where it can create new password store
        3. A _passinit function

    The test root directory is created in self.tmp. Inside this directory, each
    test has its own directory.
    """

    @classmethod
    def setUpClass(cls):
        # GPG Settings
        if 'GPG_AGENT_INFO' in os.environ:
            os.environ.pop('GPG_AGENT_INFO')
        os.environ['GNUPGHOME'] = os.path.join(os.getcwd(), 'tests/gnupg')

    def setUp(self):
        # The test name is the test method name after 'test_'
        testname = self.id().split('.').pop()[len('test_'):]

        # Set PASSWORD_STORE_DIR & declare a passwordstore object
        prefix = os.path.join(self.tmp, testname)
        os.environ['PASSWORD_STORE_DIR'] = prefix
        self.store = pass_import.PasswordStore()

        # Re-initialize the test directory
        if os.path.isdir(prefix):
            shutil.rmtree(prefix, ignore_errors=True)
        os.makedirs(prefix, exist_ok=True)

    def _passinit(self):
        with open(os.path.join(self.store.prefix, '.gpg-id'), 'w') as file:
            file.write('\n'.join(self.gpgids))
