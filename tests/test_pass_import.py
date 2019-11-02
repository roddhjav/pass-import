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

from unittest.mock import patch

import os
import tests


class TestPassImportBase(tests.Test):

    def setUp(self):
        self._tmpdir()
        self._passinit()


class TestPassImport(TestPassImportBase):

    def test_pass_import_list(self):
        """Testing: pass import --list."""
        cmd = ['--list']
        self._passimport(cmd, 0)

    def test_pass_import_quietlist(self):
        """Testing: pass import --list --quiet."""
        cmd = ['--list', '--quiet']
        self._passimport(cmd, 0)

    def test_pass_import_help(self):
        """Testing: pass import --help."""
        cmd = ['--help']
        self._passimport(cmd, 0)

    def test_pass_import_version(self):
        """Testing: pass import --version."""
        cmd = ['--version']
        self._passimport(cmd, 0)

    def test_pass_import_nomanager(self):
        """Testing: password manager not present."""
        cmd = []
        self._passimport(cmd, 1)

    def test_pass_import_notamnager(self):
        """Testing: pass import not-a-manager."""
        cmd = ['not-a-manager']
        self._passimport(cmd, 1)

    def test_pass_import_notanoption(self):
        """Testing: pass import --not-an-option."""
        cmd = ['--not-an-option']
        self._passimport(cmd, 2)

    def test_pass_import_notafile(self):
        """Testing: pass import 1password not_a_file."""
        cmd = ['1password', 'not_a_file']
        self._passimport(cmd, 1)

    def test_pass_import_storenotinitialized(self):
        """Testing: store not initialized."""
        cmd = ['1password', self.db + '1password.csv']
        os.remove(os.path.join(self.store.prefix, '.gpg-id'))
        self._passimport(cmd, 1)

    def test_pass_import_invalidid(self):
        """Testing: invalid user ID."""
        cmd = ['1password', self.db + '1password.csv']
        os.remove(os.path.join(self.store.prefix, '.gpg-id'))
        self.gpgids = ['']
        self._passinit()
        self._passimport(cmd, 1)

    def test_pass_import_file(self):
        """Testing: pass import 1password4pif db/1password4pif.1pif -v."""
        cmd = ['1password4pif', self.db + '1password4pif.1pif', '--verbose']
        self._passimport(cmd)

    def test_pass_import_root(self):
        """Testing: pass import 1password db/1password.csv --path root."""
        cmd = ['1password', self.db + '1password.csv', '--path', 'root']
        self._passimport(cmd)

    def test_pass_import_clean(self):
        """Testing: pass import 1password db/1password.csv --clean."""
        cmd = ['1password', self.db + '1password.csv', '--clean', '--quiet']
        self._passimport(cmd)

    def test_pass_import_all(self):
        """Testing: pass import 1password db/1password.csv --all."""
        cmd = ['1password', self.db + '1password.csv', '--all', '--quiet']
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

    def test_pass_import_convert(self):
        """Testing: pass import --convert db/keepass-xml.xml."""
        cmd = ['keepass-xml', self.db + 'keepass-xml.xml', '--convert', '-q']
        self._passimport(cmd)

        path = os.path.join(self.store.prefix, '.import')
        with open(path, 'w') as configfile:
            configfile.write('---\nseparator: A')

        cmd += ['--sep=~']
        self._passimport(cmd)

        cmd = ['keepass-xml', self.db + 'keepass-xml.xml', '--convert', '-q']
        self._passimport(cmd)

    def test_pass_import_config(self):
        """Testing: pass import --convert db/keepass-xml.xml with conf file."""
        cmd = ['keepass-xml', self.db + 'keepass-xml.xml', '--convert',
               '--config', 'tests/config.yml']
        self._passimport(cmd)

    def test_pass_import_badconfig(self):
        """Testing: pass import with bad config file."""
        cmd = ['keepassxml', self.db + 'keepassxml.xml', '--convert',
               '--config', 'tests/assets/format/dummy.xml']
        self._passimport(cmd, 1)


class TestPassImportManagers(TestPassImportBase):

    def test_pass_import_networkmanager(self):
        """Testing: pass import networkmanager db/networkmanager/eduroam."""
        cmd = ['networkmanager', self.db + 'networkmanager/eduroam', '--quiet']
        self._passimport(cmd)

    def test_pass_import_networkmanager_dir(self):
        """Testing: pass import networkmanager db/networkmanager/."""
        cmd = ['networkmanager', self.db + 'networkmanager/', '--quiet']
        self._passimport(cmd)

    def test_pass_import_pass(self):
        """Testing: pass import pass db/pass."""
        cmd = ['pass', self.db + 'pass', '--quiet']
        self._passimport(cmd)

    def test_pass_import_gnomekeyring(self):
        """Testing: pass import gnome-keyring pass-import."""
        cmd = ['gnome-keyring', 'pass-import', '--quiet']
        self._passimport(cmd)

    @patch("getpass.getpass")
    def test_pass_import_keepass(self, pw):
        """Testing: pass import keepass db/keepass.kdbx."""
        cmd = ['keepass', self.db + 'keepass.kdbx', '--quiet']
        pw.return_value = self.masterpassword
        self._passimport(cmd)
