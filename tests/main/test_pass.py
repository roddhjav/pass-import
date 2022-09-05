# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
from unittest import mock

import tests


class TestMainPass(tests.Test):
    """Test with password store as destination password manager."""

    def setUp(self):
        """Create a password store repository, use the pass extension."""
        self._tmpdir()
        os.environ['PASSWORD_STORE_DIR'] = self.prefix
        os.environ['_PASSWORD_STORE_EXTENSION'] = 'import'  # nosec
        self._init_pass()

    def test_main_help_manager(self):
        """Testing: pass import --help network-manager."""
        cmd = ['--help', 'network-manager']
        self.main(cmd, 0)

    def test_main_success(self):
        """Testing: pass import passpack db/passpack.csv -vvv."""
        cmd = ['passpack', tests.db + 'passpack.csv', '-vvv']
        self.main(cmd)

    def test_main_classname(self):
        """Testing: pass import Roboform db/roboform.csv -q."""
        cmd = ['Roboform', tests.db + 'roboform.csv', '-q']
        self.main(cmd)

    def test_main_not_a_file(self):
        """Testing: pass import revelation not_a_file."""
        cmd = ['revelation', 'not_a_file']
        self.main(cmd, 1, 'not_a_file is not a password repository.')

    def test_main_store_do_not_exist(self):
        """Testing: store not initialized."""
        cmd = ['upm', tests.db + 'upm.csv']
        os.remove(os.path.join(self.prefix, '.gpg-id'))
        self.main(cmd, 1, 'is not a password repository.')

    def test_main_invalid_keys(self):
        """Testing: invalid keys."""
        cmd = ['upm', tests.db + 'upm.csv']
        os.remove(os.path.join(self.prefix, '.gpg-id'))
        self.gpgids = ['']
        self._init_pass()
        self.main(
            cmd, 1,
            'invalid credentials, password encryption/decryption aborted.')

    def test_main_root(self):
        """Testing: pass import lastpass db/lastpass.csv --path root."""
        cmd = ['lastpass', tests.db + 'lastpass.csv', '--path', 'root', '-q']
        self.main(cmd)

    def test_main_clean(self):
        """Testing: pass import pass db/pass --clean."""
        cmd = ['pass', tests.db + 'pass', '--clean', '-q']
        self.main(cmd)

    def test_main_all(self):
        """Testing: pass import keepass db/keepass.xml --all."""
        cmd = ['keepass', tests.db + 'keepass.xml', '--all', '-q']
        self.main(cmd)

    def test_main_force(self):
        """Testing: pass import enpass db/enpass.json --force."""
        cmd = ['enpass', tests.db + 'enpass.json', '-q']
        self.main(cmd)
        self.main(cmd)
        cmd.append('--force')
        self.main(cmd)

    def test_main_wrong_format(self):
        """Testing: pass import passman db/1password.csv."""
        cmd = ['passman', tests.db + '1password.csv', '-q']
        self.main(cmd, 1, 'is not a valid exported passman file.')

    def test_main_convert(self):
        """Testing: pass import gorilla db/gorilla.csv --convert."""
        cmd = ['gorilla', tests.db + 'gorilla.csv', '--convert', '-q']
        self.main(cmd)

    # Test the main format detection function.

    def test_main_detect_one_prefix_unable(self):
        """Testing: pass import db/dashlane.csv ."""
        cmd = [tests.db + 'dashlane.csv', '-q']
        self.main(cmd, 1, 'Unable to detect the manager. '
                          'Please try with: pass import <manager>')

    def test_main_detect_two_manager(self):
        """Testing: pass import keepass db/keepass.csv."""
        cmd = ['keepass', tests.db + 'keepass.csv', '-q']
        self.main(cmd)

    def test_main_detect_two_no_manager(self):
        """Testing: pass import db/keepass.xml keepass."""
        cmd = [tests.db + 'keepass.csv', 'keepass', '-q']
        self.main(cmd, 1, 'is not a supported source password manager.')

    # Test the decrypter function.

    def test_main_decrypt_with_manager(self):
        """Testing: pass import lastpass db/lastpass.csv.gpg."""
        cmd = ['lastpass', tests.db + 'lastpass.csv.gpg', '-q']
        self.main(cmd)

    def test_main_decrypt_without_manager(self):
        """Testing: pass import db/andotp.gpg."""
        cmd = [tests.db + 'andotp.gpg', '-q']
        self.main(cmd)

    # Test the audit feature.

    @mock.patch('requests.get', tests.mock_hibp)
    def test_main_audit(self):
        """Testing: pass import db/audit.yml."""
        cmd = [tests.db + 'audit.yml', '--pwned']
        self.main(cmd)
