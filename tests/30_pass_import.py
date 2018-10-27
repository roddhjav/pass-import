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
import unittest
import setup


class TestPassImport(setup.TestPass):
    def setUp(self):
        super(TestPassImport, self).setUp()
        self._passinit()

    def _passimport(self, cmd, code=None):
        if code is None:
            self.passimport.main(cmd)
        else:
            with self.assertRaises(SystemExit) as cm:
                self.passimport.main(cmd)
            self.assertEqual(cm.exception.code, code)

    def test_pass_import_list(self):
        """Testing: pass import --list."""
        cmd = ['--list']
        self._passimport(cmd)

    def test_pass_import_help(self):
        """Testing: pass import --help."""
        cmd = ['--help']
        self._passimport(cmd, 0)

    def test_pass_import_version(self):
        """Testing: pass import --version."""
        cmd = ['--version']
        self._passimport(cmd, 0)

    def test_pass_import_ManagerNotPresent(self):
        """Testing: password manager not present."""
        cmd = []
        self._passimport(cmd, 1)

    def test_pass_import_NotAManager(self):
        """Testing: pass import not-a-manager."""
        cmd = ['not-a-manager']
        self._passimport(cmd, 1)

    def test_pass_import_NotAnOption(self):
        """Testing: pass import --not-an-option."""
        cmd = ['--not-an-option']
        self._passimport(cmd, 2)

    def test_pass_import_NotAFile(self):
        """Testing: pass import 1password not_a_file."""
        cmd = ['1password', 'not_a_file']
        self._passimport(cmd, 1)

    def test_pass_import_StoreNotInitialized(self):
        """Testing: store not initialized."""
        cmd = ['1password', self.db + '1password.csv']
        os.remove(os.path.join(self.store.prefix, '.gpg-id'))
        self._passimport(cmd, 1)

    def test_pass_import_FromFile(self):
        """Testing: pass import 1password db/1password.csv -v."""
        cmd = ['1password', self.db + '1password.csv', '--verbose']
        self._passimport(cmd)

    def test_pass_import_root(self):
        """Testing: pass import 1password db/1password.csv --path root."""
        cmd = ['1password', self.db + '1password.csv', '--path', 'root']
        self._passimport(cmd)

    def test_pass_import_clean(self):
        """Testing: pass import 1password db/1password.csv --clean."""
        cmd = ['1password', self.db + '1password.csv', '--clean', '--quiet']
        self._passimport(cmd)

    def test_pass_import_extra(self):
        """Testing: pass import 1password db/1password.csv --extra."""
        cmd = ['1password', self.db + '1password.csv', '--extra', '--quiet']
        self._passimport(cmd)

    def test_pass_import_force(self):
        """Testing: pass import 1password db/1password.csv --force."""
        cmd = ['1password', self.db + '1password.csv']
        self._passimport(cmd)
        self._passimport(cmd)
        cmd.append('--force')
        self._passimport(cmd)

    def test_pass_import_format(self):
        """Testing: pass import passwordexporter db/lastpass.csv."""
        cmd = ['passwordexporter', self.db + '1password.csv']
        self._passimport(cmd, 1)

    def test_pass_import_networkmanager(self):
        """Testing: pass import networkmanager db/networkmanager/eduroam."""
        cmd = ['networkmanager', self.db + 'networkmanager/eduroam']
        self._passimport(cmd)

    def test_pass_import_networkmanager_dir(self):
        """Testing: pass import networkmanager db/networkmanager/."""
        cmd = ['networkmanager', self.db + 'networkmanager/']
        self._passimport(cmd)


if __name__ == '__main__':
    unittest.main()
