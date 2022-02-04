# -*- encoding: utf-8 -*-
# pass-import - test suite common resources
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
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
"""pass-import test suite common resources.
It provides:
  - tests.tmp Path to the test temporary directory.
  - tests.tests Root path for tests
  - tests.assets Root path of tests assets.
  - tests.db Root path of db where the files to import live.
  - tests.formats Root path with basic malformed formats.
  - tests.managers Interface to manage the managers classes.
  - tests.conf Dictionary with managers tests settings.
  - tests.Tests() Base test class.
  - tests.yaml_load() Open and load a yaml reference resource.
  - tests.cls() Load a password manager object.
  - tests.reference() Set the expected reference data for a given manager.
  - tests.clear() Clear data from key not in keep.
  - tests.captured() Context manager to capture stdout.
  - tests.mocked() Mock cloud password managers API response.
  - tests.skipIfNo() Skip a password manager test if it is disabled.
"""

import os
import sys
import shutil
import unittest
from io import StringIO
from contextlib import contextmanager
import yaml

import pass_import
import pass_import.__main__


tmp = '/tmp/tests/pass-import/'  # nosec
tests = os.path.abspath('tests')
assets = os.path.join(tests, 'assets') + os.sep
formats = os.path.join(assets, 'format') + os.sep
db = os.path.join(assets, 'db') + os.sep
managers = pass_import.Managers()
with open(os.path.join(tests, 'tests.yml'), 'r') as cfile:
    conf = yaml.safe_load(cfile)


def _id(obj):
    return obj


def skipIfNo(name):
    """Skip a password manager test if it is disabled."""
    manager = name.upper()
    enabled = 'T_%s' % manager
    password = 'TESTS_%s_PASS' % manager
    if not (enabled in os.environ and password in os.environ):
        return unittest.skip(f"Skipping: {name} tests disabled.")
    return _id


def mocked(manager, cmd):
    """Mock cloud password managers API response."""
    names = {'bitwarden', 'lastpass', 'onepassword'}
    if manager not in names:
        return ''

    path = os.path.join(assets, 'mock', manager, cmd)
    with open(path) as file:
        return file.read()


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


def yaml_load(ref_path):
    """Open and load a yaml reference resource."""
    ref_path = os.path.join(assets, 'references', ref_path)
    with open(ref_path, 'r') as file:
        return yaml.safe_load(file)


def cls(name, prefix=None, **args):
    """Load a password manager object."""
    if not prefix:
        prefix = os.path.join(db, conf[name]['path'])
    settings = {'extra': True}
    for key, value in args.items():
        settings[key] = value
    return managers.get(name)(prefix, settings=settings)


def reference(name=None):
    """Set the expected reference data for a given manager.

    Some password managers do not store a lot off data (no group...).
    Therefore, we need to remove these entries from the reference data
    when testing these managers.

    """
    with open(assets + '/references/main.yml', 'r') as file:
        ref = yaml.safe_load(file)
    if name:
        if 'without' in conf[name]:
            for key in conf[name]['without']:
                for entry in ref:
                    entry.pop(key, None)
        if 'root' in conf[name]:
            for entry in ref:
                entry[
                    'group'] = conf[name]['root'] + entry['group']
    return ref


def clear(data, keep=None):
    """Clear data from key not in keep."""
    if not keep:
        keep = ['title', 'password', 'login', 'url', 'comments', 'group']
    for entry in data:
        delete = [k for k in entry.keys() if k not in keep]
        empty = [k for k, v in entry.items() if not v]
        delete.extend(empty)
        for key in delete:
            entry.pop(key, None)


class Test(unittest.TestCase):
    """Common resources for all tests.

    :param str key: Optional key for a password manager.
    :param str token: Optional token for a password manager.
    :param str login: Login for a password manager.
    :param str prefix: Path to a password repository.
    :param str masterpassword: Master password used for a password manager.
    :param list gpgids: Test GPGIDs.

    """
    key = ''
    token = ''
    login = ''
    prefix = ''
    masterpassword = 'correct horse battery staple'
    gpgids = ['D4C78DB7920E1E27F5416B81CC9DB947CF90C77B', '']

    def __init__(self, methodName='runTest'):  # noqa
        super().__init__(methodName)

        # GPG keyring & pass settings
        os.environ.pop('GPG_AGENT_INFO', None)
        os.environ.pop('PASSWORD_STORE_SIGNING_KEY', None)
        os.environ['GNUPGHOME'] = os.path.join(os.getcwd(), assets + 'gnupg')

    # Main related method

    def main(self, cmd, code=None, msg=''):
        """Call to the main function."""
        sys.argv = ['main']
        sys.argv.extend(cmd)
        if code is None:
            pass_import.__main__.main()
        elif msg == '':
            with self.assertRaises(SystemExit) as cm:
                pass_import.__main__.main()
            self.assertEqual(cm.exception.code, code)
        else:
            with captured() as (out, err):
                with self.assertRaises(SystemExit) as cm:
                    pass_import.__main__.main()
                if code == 0:
                    message = out.getvalue().strip()
                else:
                    message = err.getvalue().strip()
                self.assertIn(msg, message)
                self.assertEqual(cm.exception.code, code)

    # Export related method

    def _tmpdir(self, path=''):
        """Create a temporary test directory named after the testname."""
        self.prefix = os.path.join(tmp, self._testMethodName)

        # Re-initialize the test directory
        if os.path.isdir(self.prefix):
            shutil.rmtree(self.prefix, ignore_errors=True)
        os.makedirs(self.prefix, exist_ok=True)

        if path != '':
            self.prefix = os.path.join(self.prefix, path)

    # Import related methods

    def assertImport(self, data, refdata, keep=None):  # noqa
        """Compare imported data with the reference data."""
        clear(data, keep)
        self.assertEqual(len(data), len(refdata))
        for entry in data:
            self.assertIn(entry, refdata)

    # Special exporter access methods

    def _credentials(self, manager=''):
        """Set credentials for cloud based password managers."""
        names = {'bitwarden', 'lastpass', 'onepassword'}
        if manager in names:
            name = manager.upper()
            self.masterpassword = os.environ.get(f'TESTS_{name}_PASS', '')
            self.login = os.environ.get(f'TESTS_{name}_LOGIN', '')
            self.key = os.environ.get(f'TESTS_{name}_SECRETKEY', '')
            self.token = os.environ.get(f'TESTS_{name}_TOKEN', '')

    def _init_pass(self):
        """Initialize a new password store repository."""
        with open(os.path.join(self.prefix, '.gpg-id'), 'w') as file:
            file.write('\n'.join(self.gpgids))

    def _init_keepass(self):
        """Initialize a new keepass repository."""
        shutil.copyfile(assets + 'export/keepass.kdbx', self.prefix)
