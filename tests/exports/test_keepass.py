# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import copy
import os
from unittest.mock import patch

import tests
from pass_import.errors import PMError
from pass_import.managers.keepass import Keepass


class TestExportKeepass(tests.Test):
    """Test keepass general features."""

    def setUp(self):
        """Setup a new keepass repository."""
        self._tmpdir('keepass.kdbx')
        self.keepass = Keepass(self.prefix)
        self.keepass.all = True

    def test_keepass_exist(self):
        """Testing: exist."""
        self._init_keepass()
        self.assertTrue(self.keepass.exist())
        self.keepass.prefix = ''
        self.assertFalse(self.keepass.exist())

    def test_keepass_isvalid(self):
        """Testing: isvalid."""
        self.assertTrue(self.keepass.isvalid())


@tests.skipIfNoModule('pykeepass')
class TestExportKeepassInsert(tests.Test):
    """Test keepass insert features."""
    keep = {
        'password', 'login', 'url', 'website', 'uuid', 'otpauth', 'path',
        'comments'
    }

    def setUp(self):
        self._tmpdir('keepass.kdbx')

    @patch("getpass.getpass")
    def test_keepass_insert(self, pw):
        """Testing: keepass insert."""
        pw.return_value = self.masterpassword
        self._init_keepass()
        entry = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }
        ref = copy.deepcopy(entry)

        with Keepass(self.prefix) as keepass:
            keepass.insert(entry)
            keepass.parse()
            data = keepass.data[0]
            data['path'] = os.path.join(data['group'], data['title'])
            self.assertImport([data], [ref], self.keep)

    @patch("getpass.getpass")
    def test_keepass_insert_empty(self, pw):
        """Testing: keepass insert empty."""
        pw.return_value = self.masterpassword
        self._init_keepass()
        entry = {'path': 'test'}
        ref = copy.deepcopy(entry)

        with Keepass(self.prefix) as keepass:
            keepass.insert(entry)
            keepass.parse()
            data = keepass.data[0]
            data['path'] = os.path.join(data.pop('group', ''),
                                        data.pop('title', ''))
            self.assertImport([data], [ref], self.keep)

    @patch("getpass.getpass")
    def test_keepass_binary(self, pw):
        """Testing: keepass insert & show binary file."""
        pw.return_value = self.masterpassword
        self._init_keepass()
        with open(os.path.join(tests.assets, 'pass.png'), 'rb') as file:
            data = file.read()
        entry = {'data': data, 'path': 'pass.png'}
        ref = copy.deepcopy(entry)

        with Keepass(self.prefix) as keepass:
            keepass.insert(entry)
            keepass.parse()
        self.assertEqual(keepass.data[0]['data'], ref['data'])

    @patch("getpass.getpass")
    def test_keepass_insert_exists(self, pw):
        """Testing: keepass insert an existing entry without force."""
        pw.return_value = self.masterpassword
        self._init_keepass()
        with Keepass(self.prefix) as keepass:
            keepass.insert({'path': 'Test/test', 'password': 'a'})
            with self.assertRaises(PMError):
                keepass.insert({'path': 'Test/test', 'password': 'b'})


@tests.skipIfNoModule('pykeepass')
class TestImportKeepassReference(tests.Test):
    """Test keepass field references and root import."""

    def setUp(self):
        """Create a new keepass repository with field references."""
        from pykeepass import create_database
        self._tmpdir('keepass.kdbx')
        kdbx = create_database(self.prefix, password=self.masterpassword)
        group = kdbx.add_group(kdbx.root_group, 'Social')
        ref = kdbx.add_entry(kdbx.root_group, 'ref', 'alice', 'secret')
        uid = ref.uuid.hex.upper()
        missing = 'F' * 32
        kdbx.add_entry(group, 'entry', f'{{REF:U@I:{uid}}}',
                       f'pre-{{REF:P@I:{uid}}}-post',
                       url=f'{{REF:T@I:{uid}}}',
                       notes=f'a{{REF:P@I:{missing}}}b')
        kdbx.save()

    @patch("getpass.getpass")
    def test_keepass_subref(self, pw):
        """Testing: keepass field references."""
        pw.return_value = self.masterpassword
        with Keepass(self.prefix) as keepass:
            keepass.parse()
        data = {entry['title']: entry for entry in keepass.data}
        entry = data['entry']
        self.assertEqual(entry['login'], 'alice')
        self.assertEqual(entry['password'], 'pre-secret-post')
        self.assertTrue(entry['url'].startswith('{REF:T@I:'))
        self.assertEqual(entry['comments'], 'ab')

    @patch("getpass.getpass")
    def test_keepass_root(self, pw):
        """Testing: keepass import with a root."""
        pw.return_value = self.masterpassword
        with Keepass(self.prefix, settings={'root': 'Social'}) as keepass:
            keepass.parse()
        self.assertEqual([entry['title'] for entry in keepass.data],
                         ['entry'])
