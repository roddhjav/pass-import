# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import io
import os
from unittest.mock import MagicMock, patch

import tests
from pass_import.errors import FormatError
from pass_import.managers.gnomekeyring import GnomeKeyring


class TestParseCornerCases(tests.Test):
    """Test importers against small inline corner case exports."""

    def _parse(self, name, content):
        """Parse an inline export with the manager name."""
        with tests.cls(name, io.StringIO(content)) as importer:
            importer.parse()
            return importer.data

    def test_csv_field_limit(self):
        """Testing: CSV header larger than the csv field limit."""
        content = 'a' * 200000 + '\n'
        with self.assertRaises(FormatError):
            self._parse('LastpassCSV', content)

    def test_lastpass_csv_corrupted(self):
        """Testing: corrupted Lastpass CSV export without grouping."""
        content = ('url,username,password,extra,name,grouping,fav\n'
                   'https://twitter.com/,ostqxi,password\n')
        with self.assertRaises(FormatError):
            self._parse('LastpassCSV', content)

    def test_onepassword_pif(self):
        """Testing: 1PIF trashed item and otpauth section field."""
        sep = '***5642bee8-a5ff-11dc-8314-0800200c9a66***\n'
        content = (
            '{"typeName":"webforms.WebForm","title":"trashed",'
            '"trashed":true,"secureContents":{}}\n' + sep +
            '{"typeName":"webforms.WebForm","title":"otp",'
            '"secureContents":{"fields":[{"designation":"password",'
            '"value":"pw"}],"sections":[{"fields":['
            '{"v":"otpauth://totp/otp?secret=JBSWY3DPEHPK3PXP"},'
            '{"v":"other"}]}]}}\n' + sep)
        data = self._parse('OnePassword4PIF', content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'otp')
        self.assertEqual(data[0]['password'], 'pw')
        self.assertEqual(data[0]['otpauth'],
                         'otpauth://totp/otp?secret=JBSWY3DPEHPK3PXP')

    def test_revelation_hostdomain(self):
        """Testing: Revelation entries with a domain field."""
        content = (
            '<?xml version="1.0" encoding="utf-8" ?>\n'
            '<revelationdata version="0.4.14" dataversion="1">\n'
            '<entry type="generic"><name>a</name>'
            '<field id="generic-hostname">server</field>'
            '<field id="generic-domain">example.org</field></entry>\n'
            '<entry type="generic"><name>b</name>'
            '<field id="generic-domain">example.org</field></entry>\n'
            '<entry type="generic"><name>c</name>'
            '<field id="generic-hostname">www.example.org</field>'
            '<field id="generic-domain">example.org</field></entry>\n'
            '</revelationdata>\n')
        data = self._parse('Revelation', content)
        hosts = {entry['title']: entry['host'] for entry in data}
        self.assertEqual(hosts, {
            'a': 'server.example.org',
            'b': 'example.org',
            'c': 'www.example.org'
        })

    def test_bitwarden_custom_field_conflict(self):
        """Testing: Bitwarden custom field named as an existing key."""
        content = (
            '{"encrypted": false, "folders": [], "items": [{"id": "1",'
            '"folderId": null, "type": 1, "name": "foo", "favorite": false,'
            '"fields": [{"name": "title", "value": "bar", "type": 0}],'
            '"login": {"username": "user", "password": "pw"}}]}')
        data = self._parse('BitwardenJSON', content)
        self.assertEqual(data[0]['title'], 'foo')
        self.assertEqual(data[0]['title_'], 'bar')

    def test_html_not_html(self):
        """Testing: HTML detecter with a non HTML XML file."""
        pm = tests.managers.get('ClipperzHTML')
        with pm(io.StringIO('<root><a>b</a></root>')) as importer:
            self.assertFalse(importer.is_format())

    def test_pass_root(self):
        """Testing: password-store import with a root."""
        prefix = os.path.join(tests.db, 'pass')
        with tests.cls('PasswordStore', prefix, root='Emails') as importer:
            importer.parse()
            data = importer.data
        self.assertEqual(len(data), 4)
        for entry in data:
            self.assertTrue(entry['group'].startswith('Emails'))

    def test_pass_is_format(self):
        """Testing: password-store detection on a non store path."""
        pm = tests.managers.get('PasswordStore')
        for prefix in [tests.db, os.path.join(tests.db, 'lastpass.csv')]:
            with self.subTest(prefix):
                self.assertFalse(pm(prefix).is_format())


class TestGnomeKeyring(tests.Test):
    """Test the Gnome Keyring importer without a real keyring."""

    def test_gnome_no_secretstorage(self):
        """Testing: Gnome Keyring without secretstorage."""
        with patch('pass_import.managers.gnomekeyring.SECRETSTORAGE', False):
            with GnomeKeyring('') as importer:
                self.assertTrue(importer.exist())
                self.assertTrue(importer.isvalid())
                with self.assertRaises(ImportError):
                    importer.parse()

    def test_gnome_parse(self):
        """Testing: Gnome Keyring parse with a mocked secretstorage."""
        item = MagicMock()
        item.get_label.return_value = 'title'
        item.get_secret.return_value = b'password'
        item.get_modified.return_value = 1
        item.get_created.return_value = 0
        item.get_attributes.return_value = {'account': 'login'}
        collection = MagicMock()
        collection.get_label.return_value = 'pass-import'
        collection.get_all_items.return_value = [item]
        other = MagicMock()
        other.get_label.return_value = 'other'
        secretstorage = MagicMock()
        secretstorage.get_all_collections.return_value = [other, collection]
        with patch('pass_import.managers.gnomekeyring.SECRETSTORAGE', True), \
                patch('pass_import.managers.gnomekeyring.secretstorage',
                      secretstorage, create=True):
            with GnomeKeyring('pass-import') as importer:
                importer.parse()
                data = importer.data
        self.assertEqual(data, [{
            'group': 'pass-import', 'title': 'title', 'password': 'password',
            'modified': 1, 'created': 0, 'login': 'login'
        }])
        other.unlock.assert_not_called()
