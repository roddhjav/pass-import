# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import Cap
from pass_import.errors import PMError
from pass_import.managers.csv import GenericCSV
import tests


DATA = [{
    'password': 'UuQHzvv6IHRIJGjwKru7',
    'login': 'lnqYm3ZWtm',
    'url': 'https://twitter.com',
    'website': 'https://pujol.io',
    'uuid': '44jle5q3fdvrprmaahozexy2pi',
    'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
               'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
               'iod=30',
    'group': 'Test',
    'title': 'test1'
}, {
    'group': 'Test',
    'title': 'test2'
}]


class TestExportCSV(tests.Test):
    """Test CSV general features."""

    def setUp(self):
        """Setup a new keepass repository."""
        self._tmpdir('file.csv')
        self.gcsv = GenericCSV(self.prefix)

    def test_csv_exist(self):
        """Testing: exist."""
        self.assertTrue(self.gcsv.exist())


class TestExportCSVInsert(tests.Test):
    """Test CSV insert features."""

    def setUp(self):
        self._tmpdir('file.csv')

    def test_csv_clean(self):
        """Testing: csv clean."""
        data_expected = [{
            'comments': '',
            'email': '',
            'group': 'Test',
            'login': 'lnqYm3ZWtm',
            'otpauth':
                'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&issuer=ali'
                'ce@google.com&algorithm=SHA1&digits=6&period=30',
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'title': 'test1',
            'url': 'https://twitter.com',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'website': 'https://pujol.io'
        }, {
            'comments': '',
            'email': '',
            'group': 'Test',
            'login': '',
            'otpauth': '',
            'password': '',
            'title': 'test2',
            'url': ''
        }]
        header = 'comments,email,group,login,otpauth,password,title,url\n'

        settings = {'action': Cap.EXPORT}
        with GenericCSV(self.prefix, settings) as gcsv:
            gcsv.data = DATA
            gcsv.clean(False, False)
            self.assertEqual(gcsv.data, data_expected)

        with open(self.prefix, 'r') as file:
            self.assertEqual(file.read(), header)

    def test_csv_clean_all(self):
        """Testing: csv clean all."""
        data_expected = [{
            'group': 'Test',
            'login': 'lnqYm3ZWtm',
            'otpauth':
                'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&issuer=ali'
                'ce@google.com&algorithm=SHA1&digits=6&period=30',
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'title': 'test1',
            'url': 'https://twitter.com',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'website': 'https://pujol.io'
        }, {
            'group': 'Test',
            'login': '',
            'otpauth': '',
            'password': '',
            'title': 'test2',
            'url': '',
            'uuid': '',
            'website': ''
        }]
        header = 'group,login,otpauth,password,title,url,uuid,website\n'

        settings = {'action': Cap.EXPORT}
        with GenericCSV(self.prefix, settings) as gcsv:
            gcsv.all = True
            gcsv.data = DATA
            gcsv.clean(False, False)
            self.assertEqual(gcsv.data, data_expected)

        with open(self.prefix, 'r') as file:
            self.assertEqual(file.read(), header)

    def test_csv_insert(self):
        """Testing: csv insert."""
        ref = (
            "comments,email,group,login,otpauth,password,title,url\n"
            ",,Test,lnqYm3ZWtm,otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3"
            "PXP&issuer=alice@google.com&algorithm=SHA1&digits=6&period=30,UuQ"
            "Hzvv6IHRIJGjwKru7,test1,https://twitter.com\n,,Test,,,,test2,\n"
        )

        settings = {'action': Cap.EXPORT}
        with GenericCSV(self.prefix, settings) as gcsv:
            gcsv.data = DATA
            gcsv.clean(False, False)
            for entry in gcsv.data:
                gcsv.insert(entry)

        with open(self.prefix, 'r') as file:
            self.assertEqual(file.read(), ref)

    def test_csv_insert_all(self):
        """Testing: csv insert all."""
        ref = (
            "group,login,otpauth,password,title,url,uuid,website\n"
            "Test,lnqYm3ZWtm,otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PX"
            "P&issuer=alice@google.com&algorithm=SHA1&digits=6&period=30,UuQHz"
            "vv6IHRIJGjwKru7,test1,https://twitter.com,44jle5q3fdvrprmaahozexy"
            "2pi,https://pujol.io\nTest,,,,test2,,,\n"
        )

        settings = {'action': Cap.EXPORT}
        with GenericCSV(self.prefix, settings) as gcsv:
            gcsv.all = True
            gcsv.data = DATA
            gcsv.clean(False, False)
            for entry in gcsv.data:
                gcsv.insert(entry)

        with open(self.prefix, 'r') as file:
            self.assertEqual(file.read(), ref)

    def test_csv_open_exist(self):
        """Testing: csv open exist."""
        with open(self.prefix, 'w') as file:
            file.write('dummy')

        settings = {'action': Cap.EXPORT}
        with self.assertRaises(PMError):
            with GenericCSV(self.prefix, settings):
                pass

    def test_csv_open_exist_force(self):
        """Testing: csv open exist force."""
        with open(self.prefix, 'w') as file:
            file.write('dummy')

        settings = {'action': Cap.EXPORT, 'force': True}
        with GenericCSV(self.prefix, settings):
            pass
