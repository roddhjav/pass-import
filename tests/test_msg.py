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

import sys
from io import StringIO
from contextlib import contextmanager

import pass_import
from tests.commons import TestPassSimple


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestMsg(TestPassSimple):

    def setUp(self):
        self.msg = pass_import.Msg(False, False)

    def test_verbose(self):
        """Testing: message verbose."""
        with captured_output() as (out, err):
            self.msg.verbose('pass', 'verbose message')
            message = out.getvalue().strip()
        self.assertEqual(message, '')

        msg = pass_import.Msg(True, False)
        with captured_output() as (out, err):
            msg.verbose('pass', 'verbose msg')
            message = out.getvalue().strip()
        self.assertEqual(err.getvalue().strip(), '')
        self.assertEqual(message, '\x1b[1m\x1b[95m  .  \x1b[0m\x1b[35mpass: \x1b[0mverbose msg')
        print(message)

    def test_message(self):
        """Testing: classic message message."""
        with captured_output() as (out, err):
            self.msg.message('classic message')
            message = out.getvalue().strip()
        self.assertEqual(message, '\x1b[1m  .  \x1b[0mclassic message')
        print(message)

        msg = pass_import.Msg(True, True)
        with captured_output() as (out, err):
            msg.message('classic message')
            message = out.getvalue().strip()
        self.assertEqual(message, '')

    def test_echo(self):
        """Testing: small echo."""
        with captured_output() as (out, err):
            self.msg.echo('smal echo')
            message = out.getvalue().strip()
        self.assertEqual(message, 'smal echo')
        print(message)

    def test_success(self):
        """Testing: success message."""
        with captured_output() as (out, err):
            self.msg.success('success message')
            message = out.getvalue().strip()
        self.assertEqual(message, '\x1b[1m\x1b[92m (*) \x1b[0m\x1b[32msuccess message\x1b[0m')
        print(message)

    def test_warning(self):
        """Testing: warning message."""
        with captured_output() as (out, err):
            self.msg.warning('warning message')
            message = out.getvalue().strip()
        self.assertEqual(message, '\x1b[1m\x1b[93m  w  \x1b[0m\x1b[33mwarning message\x1b[0m')
        print(message)

    def test_error(self):
        """Testing: error message."""
        with captured_output() as (out, err):
            self.msg.error('error message')
            message = out.getvalue().strip()
        self.assertEqual(message, '\x1b[1m\x1b[91m [x] \x1b[0m\x1b[1mError: \x1b[0merror message')
        print(message)

    def test_die(self):
        """Testing: die message."""
        with captured_output() as (out, err):
            with self.assertRaises(SystemExit) as cm:
                self.msg.die('critical error')
            message = out.getvalue().strip()
            self.assertEqual(cm.exception.code, 1)
        self.assertEqual(message, '\x1b[1m\x1b[91m [x] \x1b[0m\x1b[1mError: \x1b[0mcritical error')
        print(message)
