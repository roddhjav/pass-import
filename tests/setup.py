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
import shutil
import unittest

class TestPassSimple(unittest.TestCase):
    tmp = "/tmp/pass-import/python/"
    db = "exporteddb/"

    @classmethod
    def setUpClass(self):
        # Getting pass-import module
        try:
            sys.path.append('../lib')
            self.passimport = __import__('import')
        except Exception as e:
            print("Unable to find import.py: %s", e)
            exit(1)

class TestPass(TestPassSimple):
    @classmethod
    def setUpClass(self):
        # Getting pass-import module
        super(TestPass, self).setUpClass()

        # Pass binary
        os.environ['PASSWORD_STORE_BIN'] = "/usr/bin/pass"

        # GPG Config
        if 'GPG_AGENT_INFO' in os.environ:
            os.environ.pop('GPG_AGENT_INFO', None)
        os.environ['GNUPGHOME'] = os.path.join(os.path.expanduser('~'), '.gnupg')

        # Tests directories
        self.tmp = os.path.join(self.tmp, self.__name__[8:].lower())
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.makedirs(self.tmp, exist_ok=True)

    def setUp(self):
        testname = self.id().split('_').pop() + 'store'
        os.environ['PASSWORD_STORE_DIR'] = os.path.join(self.tmp, testname)
        os.makedirs(os.environ['PASSWORD_STORE_DIR'], exist_ok=True)
        self.store = self.passimport.PasswordStore()

    def _passinit(self):
        with open(os.path.join(self.store.prefix, '.gpg-id'), 'w') as file:
            file.write("%s\n" % self.gpgid)
