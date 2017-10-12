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
try:
    sys.path.append('../lib')
    passimport = __import__('import')
except Exception as e:
    print("Unable to find import.py: %s", e)
    exit(1)

PLAIN_DB = "exporteddb/"
TMP = "/tmp/pass-import/python/import"

class TestPassImport(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if 'GPG_AGENT_INFO' in os.environ:
            os.environ.pop('GPG_AGENT_INFO', None)
        os.environ['PASSWORD_STORE_BIN'] = '/usr/bin/pass'
        os.environ['GNUPGHOME'] = os.path.join(os.path.expanduser('~'), '.gnupg')
        shutil.rmtree(TMP, ignore_errors=True)
        os.makedirs(TMP, exist_ok=True)

    def setUp(self):
        testname = self.id().split('_').pop()
        os.environ['PASSWORD_STORE_DIR'] = os.path.join(TMP, testname + '-store')
        os.makedirs(os.environ['PASSWORD_STORE_DIR'])
        self.store = passimport.PasswordStore()
        self._pass_init()

    def _pass_init(self):
        with open(os.path.join(self.store.prefix, '.gpg-id'), 'w') as file:
            file.write("%s\n" % KEY1)

    def _pass_import_exit(self, cmd, code):
        with self.assertRaises(SystemExit) as cm:
            passimport.main(cmd)
        self.assertEqual(cm.exception.code, code)

    def test_pass_import_list(self):
        """ Testing: pass import --list """
        passimport.main(['-l'])

    def test_pass_import_help(self):
        """ Testing: pass import --help """
        cmd = ['--help']
        self._pass_import_exit(cmd, 0)

    def test_pass_import_version(self):
        """ Testing: pass import --version """
        cmd = ['--version']
        self._pass_import_exit(cmd, 0)

    def test_pass_import_ManagerNotPresent(self):
        """ Testing: password manager not present """
        cmd = []
        self._pass_import_exit(cmd, 1)

    def test_pass_import_NotAManager(self):
        """ Testing: pass import not-a-manager """
        cmd = ['not-a-manager']
        self._pass_import_exit(cmd, 1)

    def test_pass_import_NotAnOption(self):
        """ Testing: pass import --not-an-option """
        cmd = ['--not-an-option']
        self._pass_import_exit(cmd, 2)

    def test_pass_import_NotAFile(self):
        """ Testing: pass import 1password not_a_file """
        cmd = ['1password', 'not_a_file']
        self._pass_import_exit(cmd, 1)

    def test_pass_import_StoreNotInitialized(self):
        """ Testing: store not initialized """
        cmd = ['1password', PLAIN_DB + '1password']
        os.remove(os.path.join(self.store.prefix, '.gpg-id'))
        self._pass_import_exit(cmd, 1)

    def test_pass_import_FromFile(self):
        """ Testing: pass import 1password db/1password -v"""
        cmd = ['1password', PLAIN_DB + '1password', '--verbose']
        passimport.main(cmd)

    def test_pass_import_FromStdin(self):
        """ Testing: pass import 1password """
        cmd = ['dashlane', '--quiet']
        passimport.main(cmd)

    def test_pass_import_root(self):
        """ Testing: pass import 1password db/1password --path root """
        cmd = ['1password', PLAIN_DB + '1password', '--path', 'root']
        passimport.main(cmd)

    def test_pass_import_clean(self):
        """ Testing: pass import 1password db/1password --clean """
        cmd = ['1password', PLAIN_DB + '1password', '--clean', '--quiet']
        passimport.main(cmd)

    def test_pass_import_extra(self):
        """ Testing: pass import 1password db/1password --extra """
        cmd = ['1password', PLAIN_DB + '1password', '--extra', '--quiet']
        passimport.main(cmd)

    def test_pass_import_force(self):
        """ Testing: pass import 1password db/1password --force """
        cmd = ['1password', PLAIN_DB + '1password']
        passimport.main(cmd)
        passimport.main(cmd)
        cmd.append('--force')
        passimport.main(cmd)

    def test_pass_import_format(self):
        """ Testing: pass import passwordexporter db/lastpass """
        cmd = ['passwordexporter', PLAIN_DB + 'lastpass']
        self._pass_import_exit(cmd, 1)


if __name__ == '__main__':
    unittest.main()
