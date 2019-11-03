#!/usr/bin/env python3
# pass-import - test suite common resources
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

import os
import sys
import shutil
import unittest
from io import StringIO
from contextlib import contextmanager
import yaml

import pass_import


@contextmanager
def captured():
    """Context manager to capture stdout."""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class Test(unittest.TestCase):
    """Common resources for all tests.

    :param str tmp: Path to the test temporary directory.
    :param str assets: Root path of tests assets.
    :param str format: Root path with basic malformed formats.
    :param str db: Root path of db where the files to import live.
    :param str masterpassword: Master password used for a password manager.
    :param dict tests: Dictionary with managers tests settings.
    :param str prefix: Prefix of the password store repository.
    :param list gpgids: Test GPGIDs.
    :param PasswordStore store: Password store object to test.

    """
    store = None
    prefix = ''
    assets = 'tests/assets/'
    db = 'tests/assets/db/'
    format = 'tests/assets/format/'
    tmp = '/tmp/tests/pass-import/python/'  # nosec
    masterpassword = 'correct horse battery staple'
    gpgids = ['D4C78DB7920E1E27F5416B81CC9DB947CF90C77B', '']

    def __init__(self, methodName='runTest'):
        super(Test, self).__init__(methodName)
        self.importers = pass_import.IMPORTERS
        with open('tests/tests.yml', 'r') as file:
            self.tests = yaml.safe_load(file)

        # GPG keyring, pass & lastpass settings
        os.environ.pop('GPG_AGENT_INFO', None)
        os.environ.pop('PASSWORD_STORE_SIGNING_KEY', None)
        os.environ['GNUPGHOME'] = os.path.join(os.getcwd(),
                                               self.assets + 'gnupg')
    # Main related method

    def _passimport(self, cmd, code=None):
        sys.argv = cmd
        if code is None:
            pass_import.main()
        else:
            with self.assertRaises(SystemExit) as cm:
                pass_import.main()
            self.assertEqual(cm.exception.code, code)

    # Export related method

    def _tmpdir(self):
        """Create a temporary test directory named after the testname."""
        self.prefix = os.path.join(self.tmp, self._testMethodName)

        # Set PASSWORD_STORE_DIR & declare a passwordstore object
        os.environ['PASSWORD_STORE_DIR'] = self.prefix
        self.store = pass_import.PasswordStore()

        # Re-initialize the test directory
        if os.path.isdir(self.prefix):
            shutil.rmtree(self.prefix, ignore_errors=True)
        os.makedirs(self.prefix, exist_ok=True)

    def _passinit(self):
        """Initialize a new password store repository."""
        with open(os.path.join(self.prefix, '.gpg-id'), 'w') as file:
            file.write('\n'.join(self.gpgids))

    # Import related methods

    @staticmethod
    def _class(manager):
        """Load an importer class."""
        cls = pass_import.IMPORTERS[manager]
        importer = cls(extra=True)
        return importer

    def _path(self, manager):
        """Get database file to test."""
        ext = self.tests[manager]['extension']
        return os.path.join(self.db, "%s.%s" % (manager, ext))

    def _reference(self, manager=None):
        """Set the expected reference data for a given manager.

        Some password managers do not store a lot off data (no group...).
        Therefore, we need to remove these entries from the reference data
        when testing these managers.

        """
        with open(self.assets + '/references/main.yml', 'r') as file:
            reference = yaml.safe_load(file)
        if manager:
            if 'without' in self.tests[manager]:
                for key in self.tests[manager]['without']:
                    for entry in reference:
                        entry.pop(key, None)
            if 'root' in self.tests[manager]:
                for entry in reference:
                    entry[
                        'group'] = self.tests[manager]['root'] + entry['group']
        return reference

    @staticmethod
    def _clear(data, keep=None):
        """Only keep the keys present in the template and reference file."""
        if not keep:
            keep = ['title', 'password', 'login', 'url', 'comments', 'group']
        for entry in data:
            delete = [k for k in entry.keys() if k not in keep]
            empty = [k for k, v in entry.items() if not v]
            delete.extend(empty)
            for key in delete:
                entry.pop(key, None)

    def assertImport(self, data, refdata, keep=None):
        """Compare imported data with the reference data."""
        self._clear(data, keep)
        for entry in data:
            self.assertIn(entry, refdata)
