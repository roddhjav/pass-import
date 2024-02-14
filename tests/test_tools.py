# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
from unittest.mock import patch

import pass_import.clean as clean
import pass_import.tools
from pass_import.core import Cap
import tests


class TestStatic(tests.Test):
    """Test the static functions."""

    @patch("getpass.getpass")
    def test_getpassword(self, passwd):
        """Testing: getpassword function."""
        passwd.return_value = self.masterpassword
        password = pass_import.tools.getpassword('Dummy')
        self.assertEqual(password, self.masterpassword)


class TestConfig(tests.Test):
    """Test the Config class."""

    def setUp(self):
        self.conf = pass_import.tools.Config()

    def test_settings(self):
        """Testing: read configuration file and gen settings."""
        os.environ['PASSWORD_STORE_DIR'] = 'pass/to/store'  # nosec
        args = {'config': tests.assets + 'config.yml'}
        conf = pass_import.tools.Config()
        conf.readconfig(args)
        settings = conf.getsettings('')

        self.assertEqual(clean.SEPARATOR, '5')
        self.assertEqual(clean.CLEANS, {' ': '5'})
        self.assertEqual(clean.PROTOCOLS, [])
        self.assertEqual(
            clean.INVALIDS,
            ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\x00', '\t'])
        self.assertEqual(settings, {
            'decrypted': False,
            'action': Cap.IMPORT,
            'delimiter': ',',
            'root': '',
        })

    def test_showentry(self):
        """Testing: show a password entry."""
        conf = pass_import.tools.Config()
        conf.verbosity(2)
        entry = {
            'path': 'Social/mastodon.social',
            'password': 'EaP:bCmLZliqa|]WR/#HZP',
            'login': 'roddhjav',
            'group': 'Social'
        }
        ref = ('\x1b[1m\x1b[95m  .  \x1b[0m\x1b[35mPath: \x1b[0mSocial/mastodo'
               'n.social\n\x1b[1m\x1b[95m  .  \x1b[0m\x1b[35mData: \x1b[0mEaP:'
               'bCmLZliqa|]WR/#HZP\n           login: roddhjav')
        with tests.captured() as (out, err):
            conf.show(entry)
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(message, ref)

    def test_debug(self):
        """Testing: debug message."""
        conf = pass_import.tools.Config()
        conf.verbosity(3)
        with tests.captured() as (out, err):
            conf.debug('pass', 'debug message')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(
            message,
            '\x1b[1m\x1b[95m  .  \x1b[0m\x1b[35mpass: \x1b[0mdebug message')

    def test_verbose_simple(self):
        """Testing: message verbose simple."""
        with tests.captured() as (out, err):
            self.conf.verbose('pass', 'verbose message')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(message, '')

    def test_verbose(self):
        """Testing: message verbose."""
        conf = pass_import.tools.Config()
        conf.verbosity(1, False)
        with tests.captured() as (out, err):
            conf.verbose('pass', 'verbose msg')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(
            message,
            '\x1b[1m\x1b[95m  .  \x1b[0m\x1b[35mpass: \x1b[0mverbose msg')

        with tests.captured() as (out, err):
            conf.verbose('pass')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(message,
                         '\x1b[1m\x1b[95m  .  \x1b[0m\x1b[35mpass\x1b[0m')

    def test_message(self):
        """Testing: classic message."""
        with tests.captured() as (out, err):
            self.conf.message('classic message')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(message, '\x1b[1m  .  \x1b[0mclassic message')

        conf = pass_import.tools.Config()
        conf.verbosity(1, True)
        with tests.captured() as (out, err):
            conf.message('classic message')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(message, '')

    def test_echo(self):
        """Testing: small echo."""
        with tests.captured() as (out, err):
            self.conf.echo('small echo')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(message, 'small echo')

    def test_success(self):
        """Testing: success message."""
        with tests.captured() as (out, err):
            self.conf.success('success message')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(
            message,
            '\x1b[1m\x1b[92m (*) \x1b[0m\x1b[32msuccess message\x1b[0m')

    def test_warning(self):
        """Testing: warning message."""
        with tests.captured() as (out, err):
            self.conf.warning('warning message')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(
            message,
            '\x1b[1m\x1b[93m  w  \x1b[0m\x1b[33mwarning message\x1b[0m')

    def test_error(self):
        """Testing: error message."""
        with tests.captured() as (out, err):
            self.conf.error('error message')
            message = err.getvalue().strip()
        self.assertEqual(out.getvalue().strip(), '')
        self.assertEqual(
            message,
            '\x1b[1m\x1b[91m [x] \x1b[0m\x1b[1mError: \x1b[0merror message')

    def test_die(self):
        """Testing: die message."""
        with tests.captured() as (out, err):
            with self.assertRaises(SystemExit) as cm:
                self.conf.die('critical error')
            message = err.getvalue().strip()
            self.assertEqual(cm.exception.code, 1)
        self.assertEqual(out.getvalue().strip(), '')
        self.assertEqual(
            message,
            '\x1b[1m\x1b[91m [x] \x1b[0m\x1b[1mError: \x1b[0mcritical error')
