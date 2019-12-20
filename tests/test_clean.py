# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

import pass_import.clean
import tests
from pass_import.managers.passwordstore import PasswordStore


class TestStatic(tests.Test):
    """Test of the static function in clean.py."""

    def test_cmdline(self):
        """Testing: clean.cmdline."""
        string = 'Root Group&Named@root\'[directory]'
        string_expected = 'Root-GroupandNamedAtrootdirectory'
        string = pass_import.clean.cmdline(string)
        self.assertEqual(string, string_expected)

    def test_convert(self):
        """Testing: clean.convert."""
        string = 'Root/Group\\Named>root\0directory'
        string_expected = 'Root-Group-Named-root-directory'
        string = pass_import.clean.convert(string)
        self.assertEqual(string, string_expected)

    def test_convert_separator(self):
        """Testing: clean.convert with ~ as separator."""
        string = 'Root/Group\\Named>root\0directory'
        string_expected = 'Root~Group~Named~root~directory'
        pass_import.clean.SEPARATOR = '~'
        string = pass_import.clean.convert(string)
        self.assertEqual(string, string_expected)
        pass_import.clean.SEPARATOR = '-'

    def test_group(self):
        """Testing: clean.group."""
        string = 'Root/Group\\Named>root\0directory'
        string_expected = 'Root%sGroup%sNamed-root-directory' % (os.sep,
                                                                 os.sep)
        string = pass_import.clean.group(string)
        self.assertEqual(string, string_expected)

    def test_protocol(self):
        """Testing: clean.protocol."""
        string = 'https://duckduckgo.comhttp://google.com'
        string_expected = 'duckduckgo.comgoogle.com'
        string = pass_import.clean.protocol(string)
        self.assertEqual(string, string_expected)

    def test_title(self):
        """Testing: clean.title."""
        string = 'tw\\it/ter / login'
        string_expected = 'tw-it-ter - login'
        string = pass_import.clean.title(string)
        self.assertEqual(string, string_expected)

    def test_replaces(self):
        """Testing: clean.replaces."""
        string = ''
        string_expected = ''
        caracters = {}
        string = pass_import.clean.replaces(caracters, string)
        self.assertEqual(string, string_expected)


class TestClean(tests.Test):
    """Base class for entry cleaning tests."""

    @classmethod
    def setUpClass(cls):
        cls.store = PasswordStore('')


class TestCleanClean(TestClean):
    """Test clean features."""

    def test_data(self):
        """Testing: clean data."""
        self.store.data = [{
            'title': 'twitter.com',
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'comments': '',
            'group': 'Social',
            'address': '',
            'sex': '',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi'
        }]
        data_expected = [{
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'path': 'Social/twitter.com'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_url(self):
        """Testing: clean data - url as path name."""
        self.store.data = [{
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'twitter.com'
        }]
        data_expected = [{
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'twitter.com',
            'path': 'lnqYm3ZWtm'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_login(self):
        """Testing: clean data - login as path name."""
        self.store.data = [{
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm'
        }]
        data_expected = [{
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'path': 'lnqYm3ZWtm'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_notitle(self):
        """Testing: clean data - notitle as path name."""
        self.store.data = [{'password': 'UuQHzvv6IHRIJGjwKru7'}]
        data_expected = [{
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'path': 'notitle'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_title(self):
        """Testing: clean data - remove separator from title."""
        self.store.data = [{'title': 'twi/tter\\.com'}]
        data_expected = [{'path': 'twi-tter-.com'}]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_empty(self):
        """Testing: clean data - empty title and clean enabled."""
        self.store.data = [{'password': 'UuQHzvv6IHRIJGjwKru7'}]
        data_expected = [{
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'path': 'notitle'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_convert(self):
        """Testing: convert password path."""
        self.store.data = [{
            'title': 'ovh>com',
            'password': 'AGJjkMPsRUqDXyUdLbC4',
            'login': 'lnqYm3ZWtm'
        }, {
            'password': 'VRiplZSniSBlHNnQvc9e',
            'login': 'fm/mhpv*ity'
        }]
        data_expected = [{
            'password': 'AGJjkMPsRUqDXyUdLbC4',
            'login': 'lnqYm3ZWtm',
            'path': 'ovh-com'
        }, {
            'password': 'VRiplZSniSBlHNnQvc9e',
            'login': 'fm/mhpv*ity',
            'path': 'fm-mhpv-ity'
        }]
        self.store.clean(False, True)
        self.assertEqual(self.store.data, data_expected)


class TestCleanDuplicate(TestClean):
    """Test duplicate path management."""

    def test_paths(self):
        """Testing: duplicate paths."""
        self.store.data = [{
            'title': 'ovh.com',
            'password': 'AGJjkMPsRUqDXyUdLbC4',
            'login': 'lnqYm3ZWtm'
        }, {
            'title': 'ovh.com',
            'password': 'VRiplZSniSBlHNnQvc9e',
            'login': 'lnqYm3ZWtm'
        }, {
            'title': 'ovh.com',
            'password': '[Q&$\fd]!`vKA&b',
            'login': 'fmmhpvity'
        }, {
            'title': 'ovh.com',
            'password': 'DQm_Y+a(sDC)[1|U-S<8Dq!A',
            'login': 'ptfzlnvmj'
        }]
        data_expected = [{
            'password': 'AGJjkMPsRUqDXyUdLbC4',
            'login': 'lnqYm3ZWtm',
            'path': 'ovh.com/lnqYm3ZWtm'
        }, {
            'password': 'VRiplZSniSBlHNnQvc9e',
            'login': 'lnqYm3ZWtm',
            'path': 'ovh.com/lnqYm3ZWtm-1'
        }, {
            'password': '[Q&$\fd]!`vKA&b',
            'login': 'fmmhpvity',
            'path': 'ovh.com/fmmhpvity'
        }, {
            'password': 'DQm_Y+a(sDC)[1|U-S<8Dq!A',
            'login': 'ptfzlnvmj',
            'path': 'ovh.com/ptfzlnvmj'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_subfolder(self):
        """Testing: duplicate to subfolder."""
        self.store.data = [{
            'title': 'google.com',
            'login': 'mdtx@gmail.com',
            'group': 'Emails'
        }, {
            'title': 'google.com',
            'login': 'lnqY@gmail.com',
            'group': 'Emails'
        }, {
            'title': 'google.com',
            'login': 'fmmh@gmail.com',
            'group': 'Emails'
        }, {
            'title': 'google.com',
            'login': 'ptfz@gmail.com',
            'group': 'Emails'
        }]
        data_expected = [{
            'login': 'mdtx@gmail.com',
            'path': 'Emails/google.com/mdtx@gmail.com'
        }, {
            'login': 'lnqY@gmail.com',
            'path': 'Emails/google.com/lnqY@gmail.com'
        }, {
            'login': 'fmmh@gmail.com',
            'path': 'Emails/google.com/fmmh@gmail.com'
        }, {
            'login': 'ptfz@gmail.com',
            'path': 'Emails/google.com/ptfz@gmail.com'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)

    def test_numbers(self):
        """Testing: duplicate with numbers."""
        self.store.data = [{
            'title': 'ovh.com'
        }, {
            'title': 'ovh.com'
        }, {
            'title': 'ovh.com'
        }, {
            'title': 'ovh.com'
        }]
        data_expected = [{
            'path': 'ovh.com/notitle'
        }, {
            'path': 'ovh.com/notitle-1'
        }, {
            'path': 'ovh.com/notitle-2'
        }, {
            'path': 'ovh.com/notitle-3'
        }]
        self.store.clean(False, False)
        self.assertEqual(self.store.data, data_expected)
